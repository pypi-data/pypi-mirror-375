# Copyright 2020-2023 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""Train utility."""
from __future__ import absolute_import

import os
import sys
import json
from collections.abc import Iterable

import time
import numpy as np

from mindspore.common.tensor import Tensor
from mindspore._c_expression import TensorPy as Tensor_
from mindspore._c_expression import MSContext, ms_ctx_param
from mindspore.common.dtype import _dtype_to_nptype, _pytype_to_dtype
from mindspore.common import dtype as mstype
from mindspore import context
from mindspore import log as logger
from mindspore import _checkparam as Validator
from mindspore.common.api import _cell_graph_executor
from mindspore.communication.management import get_rank, get_group_size
from mindspore.train.mind_ir_pb2 import ModelProto as mindir_model
from mindspore.train.checkpoint_pb2 import Checkpoint
from mindspore.train.node_strategy_pb2 import ParallelStrategyMap as ckpt_strategy
from mindspore.train.lineage_pb2 import DatasetGraph, TrainLineage, EvaluationLineage, UserDefinedInfo
from mindspore.parallel._parallel_serialization import _make_dir
from mindspore.ops.operations import debug_ops
from mindspore.nn.cell import Cell


def _convert_type(types):
    """
    Convert from numpy type to tensor type.

    Args:
        types (list): Numpy type list of element in dataset.

    Returns:
        list, list of element in dataset.
    """
    ms_types = []
    for np_type in types:
        ms_type = _pytype_to_dtype(np_type)  # pylint:disable=protected-access
        ms_types.append(ms_type)
    return ms_types


def _get_types_and_shapes(dataset):
    """Get dataset types and shapes."""
    dataset_types = _convert_type(dataset.output_types())
    dataset_shapes = dataset.output_shapes()
    return dataset_types, dataset_shapes


def enable_data_broadcast():
    """Get status to indicate if enable dataset broadcast."""
    return MSContext.get_instance().get_param(ms_ctx_param.dataset_broadcast_opt_level) > 0


def _exec_datagraph(exec_dataset, dataset_size, phase='dataset', create_data_info_queue=False):
    """Initialize and execute the dataset graph."""
    batch_size = exec_dataset.get_batch_size()
    input_indexs = exec_dataset.input_indexs

    # transform data format
    dataset_types, dataset_shapes = _get_types_and_shapes(exec_dataset)
    send_epoch_end = bool(dataset_size == -1)
    queue_name = _cell_graph_executor.get_queue_name(phase)
    if queue_name is None:
        queue_name = str("")

    # Don't enable dynamic shape(multi-subgraph) feature in pp/data_broadcast mode,
    # otherwise get_data_info will stuck since some rank do not consume data.
    use_pipeline_parallel = (context.get_auto_parallel_context("pipeline_stages") > 1)
    data_broadcast = enable_data_broadcast()

    if use_pipeline_parallel or data_broadcast:
        create_data_info_queue = False

    exec_dataset = exec_dataset.device_que(send_epoch_end=send_epoch_end,
                                           create_data_info_queue=create_data_info_queue, queue_name=queue_name)
    _cell_graph_executor.init_dataset(exec_dataset.queue_name,
                                      dataset_size,
                                      batch_size,
                                      dataset_types,
                                      dataset_shapes,
                                      input_indexs,
                                      phase=phase)
    return exec_dataset


def _make_directory(path, arg_name='path'):
    """Make directory."""
    return _make_dir(path, arg_name)


def _construct_tensor_list(types, shapes, batch_expand_num=1):
    """
    Construct list of tensors with types and shapes, used to initialize the network.

    Args:
        types: List or Tuple. The output types of element in dataset.
        shapes: List or Tuple. The output shapes of element in dataset.
        batch_expand_num (int): Batch expand number.

    Returns:
        List, list of Tensors.
    """
    if len(types) != len(shapes):
        raise ValueError("The length of dataset types must be equal to dataset shapes, "
                         "but got dataset types={} and dataset shapes={}".format(types, shapes))
    tensor_list = []
    for type_, shape in zip(types, shapes):
        new_shape = ()
        for i, item in enumerate(shape):
            if i == 0:
                new_shape += (item * batch_expand_num,)
            else:
                new_shape += (item,)
        tensor = Tensor(np.zeros(new_shape, _dtype_to_nptype(type_)), dtype=type_)  # pylint:disable=protected-access
        tensor.virtual_flag = True
        tensor_list.append(tensor)
    return tensor_list


def _to_tensor(elem, scaling_sens=None):
    """Convert numpy to tensor, adapt to feed the data from host solution."""
    lst = []
    if not isinstance(elem, (tuple, list)):
        elem = [elem]
    for data in elem:
        if not isinstance(data, np.ndarray):
            if scaling_sens:
                elem_tuple = tuple(elem) + (Tensor(scaling_sens, mstype.float32),)
            else:
                elem_tuple = tuple(elem)
            return elem_tuple
        lst.append(Tensor(data))
    if scaling_sens:
        lst.append(Tensor(scaling_sens, mstype.float32))

    return lst[0] if len(lst) == 1 else tuple(lst)


def _construct_input_tensors(dataset_types, dataset_shapes, device_number=1):
    """Construct tensor list to initialize the network which implemented in dataset sink."""
    tensor_list_run = _construct_tensor_list(dataset_types, dataset_shapes, batch_expand_num=1)
    tensor_list_compile = _construct_tensor_list(dataset_types, dataset_shapes, batch_expand_num=device_number)
    return tensor_list_run, tensor_list_compile


def _check_to_numpy(plugin, tensor, prim=None):
    """Check the tensor and return a numpy.ndarray."""
    np_value = tensor.asnumpy()
    np_value = np_value.copy()
    summary_name = plugin.capitalize() + "Summary" if prim else "SummaryRecord"
    if plugin == 'scalar':
        if np_value.size == 1:
            return np_value
        raise ValueError(
            f'For "{summary_name}", the v rank must be less than or equal to 1, but got {len(np_value)}.')
    if plugin == 'image':
        if np_value.ndim == 4:
            return np_value
        raise ValueError(f'For "{summary_name}", the tensor seems not to hold a valid image.')
    if plugin in ('tensor', 'histogram'):
        if np_value.ndim > 0:
            return np_value
        raise ValueError(f'For "{summary_name}", the value should not be empty.')
    return np_value


def check_summary_param(summary_name, tag, tensor):
    """Checks the tag is valid for summary."""
    plugin = summary_name.split('Summary')[0].lower()
    try:
        if not isinstance(tag, str) or not tag:
            raise TypeError(f'For "{summary_name}", the name must be valid string, but got "{tag}".')
        if not isinstance(tensor, (Tensor, Tensor_)):
            raise TypeError(f'For "{summary_name}", the parameter "value" expect to be Tensor, '
                            f'but got {type(tensor).__name__}')
        _check_to_numpy(plugin, tensor, prim=True)
    except TypeError as err:
        raise TypeError(err) from err
    except ValueError as err:
        raise ValueError(err) from err
    finally:
        debug_ops.SUMMARY_TENSOR_CACHE = []


def _check_lineage_value(plugin, value):
    """Check the lineage value."""

    def raises(plugin, prototype):
        raise TypeError(f'Plugin {repr(plugin)} expects a {prototype.__name__} value.')

    if plugin == 'dataset_graph' and not isinstance(value, DatasetGraph):
        raises(plugin, DatasetGraph)

    if plugin == 'eval_lineage' and not isinstance(value, EvaluationLineage):
        raises(plugin, EvaluationLineage)

    if plugin == 'train_lineage' and not isinstance(value, TrainLineage):
        raises(plugin, TrainLineage)

    if plugin == 'custom_lineage_data' and not isinstance(value, UserDefinedInfo):
        raises(plugin, UserDefinedInfo)


def check_value_type(arg_name, arg_value, valid_types):
    """Checks whether a value is instance of some types."""
    valid_types = tuple(valid_types) if isinstance(valid_types, Iterable) else (valid_types,)
    is_valid = True

    # bool is subclass of int, so for a bool value, we need to extra check
    if isinstance(arg_value, int) and isinstance(arg_value, bool) and bool not in valid_types:
        is_valid = False

    if not isinstance(arg_value, valid_types):
        is_valid = False

    if not is_valid:
        raise TypeError(f'For `{arg_name}` the type should be a valid type of {[t.__name__ for t in valid_types]}, '
                        f'but got {type(arg_value).__name__}.')


def read_proto(file_name, proto_format="MINDIR", display_data=False):
    """
    Read protobuf file.

    Args:
        file_name (str): File name.
        proto_format (str): Proto format {MINDIR, CKPT, CKPT_STRATEGY}.  Default: MINDIR.
        display_data (bool): Whether display data. Default: ``False``.

    Returns:
        Object, proto object.
    """
    Validator.check_file_name_by_regular(file_name)
    file_name = os.path.realpath(file_name)
    if proto_format == "MINDIR":
        model = mindir_model()
    elif proto_format == "CKPT":
        model = Checkpoint()
    elif proto_format == "CKPT_STRATEGY":
        model = ckpt_strategy()
    else:
        raise ValueError("Unsupported proto format.")

    try:
        with open(file_name, "rb") as f:
            pb_content = f.read()
            model.ParseFromString(pb_content)
    except BaseException as e:
        logger.critical(f"Failed to phase the file: {file_name} as format: {proto_format},"
                        f" please check the correct file and format.")
        raise ValueError(e.__str__()) from e
    finally:
        pass

    if proto_format == "MINDIR" and not display_data:
        for param_proto in model.graph.parameter:
            param_proto.raw_data = b'\0'

    if proto_format == "CKPT" and not display_data:
        for element in model.value:
            if element.tensor.ByteSize() != 0:
                element.tensor.tensor_content = b'\0'
            else:
                for ele in element.maptensor.tensor:
                    ele.tensor_content = b'\0'

    return model


def parse_strategy_ckpt(file_name):
    """
    Parses a strategy ckpt layout file and returns the rank location dict.

    Args:
        file_name (str):Strategy ckpt file name.

    Returns:
        Dict, layout dict. Key is parameter name, value is (dev_matrix, tensor_map).

    Examples:
        >>> from mindspore.train.utils import parse_strategy_ckpt
        >>> layout_dict = parse_strategy_ckpt("/path/to/strategy.ckpt")
        {"param1": [[4, 4], [0, -1]], "param2": [[4, 4], [-1, 0]],,,,}
    """
    model = ckpt_strategy()
    with open(file_name, "rb") as f:
        pb_content = f.read()
        model.ParseFromString(pb_content)
    layout_dict = {}
    for param in model.parallel_layout_item:
        dev_matrix = []
        tensor_map = []
        for ele in param.parallel_layouts.dev_matrix[0].ListFields()[0][1]:
            dev_matrix.append(ele)

        for ele in param.parallel_layouts.tensor_map[0].ListFields()[0][1]:
            tensor_map.append(ele)
        layout_dict[param.param_name] = [dev_matrix, tensor_map, param.parallel_layouts.opt_weight_shard_step,
                                         param.parallel_layouts.opt_weight_shard_size]
    return layout_dict


def _get_strategy_opt_shard(param_redundancy_dict, parameter_layout_opt_shard):
    """Strategy ckpt append opt shard."""
    for key, value in parameter_layout_opt_shard.items():
        if value[1] != 0:
            param_redundancy_ranks = param_redundancy_dict.get(key)
            if value[1] != -1:
                opt_para_num = value[1]
            elif param_redundancy_ranks:
                opt_para_num = len(param_redundancy_ranks) * len(param_redundancy_ranks[0]) // value[0]
            else:
                raise ValueError(f"For get_parameter_redundancy, the format of the parallel communication domain for "
                                 f"the optimizer is incorrect.")
            res = []
            for param_ranks in param_redundancy_ranks:
                if len(param_ranks) % opt_para_num == 0:
                    for i in range(0, opt_para_num):
                        res.append(param_ranks[i::opt_para_num])
            param_redundancy_dict[key] = tuple(res)


def _get_layout_opt_shard(layout_obj, param_redundancy_dict):
    """Layout ckpt append opt shard."""
    for key, value in layout_obj.items():
        if value[5]:
            world_groups = ("hccl_world_group", "nccl_world_group", "mccl_world_group")
            if value[5] in world_groups:
                opt_para_num = get_group_size()
            elif "-" in value[5]:
                opt_para_str = value[5].split("-")[0]
                opt_para_num = int(opt_para_str)
            else:
                raise ValueError(f"For get_parameter_redundancy, the format of the parallel communication domain for "
                                 f"the optimizer is incorrect.")
            param_redundancy_ranks = param_redundancy_dict.get(key)
            res = []
            for param_ranks in param_redundancy_ranks:
                if len(param_ranks) % opt_para_num == 0:
                    for i in range(0, opt_para_num):
                        res.append(param_ranks[i::opt_para_num])
            param_redundancy_dict[key] = tuple(res)


def _get_parameter_redundancy_without_opt_shard(parameter_layout, param_redundancy_dict, initial_rank):
    """Get parameter redundancy without opt shard."""
    for key, (slices, deploy_loc, *_) in parameter_layout.items():
        redundancy_matrix = np.zeros(shape=slices + [len(slices)], dtype=np.int8)
        for i in deploy_loc:
            internal_slice = tuple(slice(None) for _ in range(i))
            for j in range(slices[-i - 1]):
                if i == -1:
                    continue
                else:
                    redundancy_matrix[(..., j) + internal_slice + (i,)] = j
        locate_list = redundancy_matrix.reshape((-1, len(slices))).tolist()
        redundancy_dict = {}
        for index, locate in enumerate(locate_list):
            redundancy_dict.setdefault(tuple(locate), []).append(index + initial_rank)
        redundancy_list = []
        for _, indices in sorted(redundancy_dict.items()):
            redundancy_list.append(tuple(indices))
        param_redundancy_dict[key] = tuple(redundancy_list)


def _get_initial_rank(parameter_layout):
    """Get the initial rank of pp."""
    for k, _ in parameter_layout.items():
        dev_matrix = parameter_layout[k][0]
        break
    dev_num = 1
    if dev_matrix:
        for i in dev_matrix:
            dev_num *= i
    rank_id = get_rank()
    initial_rank = (rank_id // dev_num) * dev_num
    return initial_rank


def _get_pp_size_from_redundancy_map(param_redundancy):
    """Get pp size from redundancy map."""
    for _, v in param_redundancy.items():
        return len(v) * len(v[0])


def get_parameter_redundancy(layout_obj, initial_rank=None):
    """
    Get parameter redundancy map.

    Args:
        layout_obj (Union[str, layout): File name of `strategy.ckpt` or net.parameter_layout_dict.
        initial_rank (int): Start rank id for each pipeline. Default: ``None``.

    Returns:
        Dict, dict of parameter redundancy info.

    Examples:
        >>> from mindspore.train.utils import get_parameter_redundancy
        >>> param_redundancy_dict = get_parameter_redundancy("/path/to/strategy.ckpt", initial_rank=0)
        {'param1': ((0, 1, 2, 3, 4, 5, 6, 7),),
         'param2': ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)),
         'param3': ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)),
         'param4': ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15))}
    """
    if isinstance(layout_obj, str):
        parameter_layout_total = parse_strategy_ckpt(layout_obj)
        parameter_layout = {}
        parameter_layout_opt_shard = {}
        for key, value in parameter_layout_total.items():
            parameter_layout[key] = value[0:2]
            parameter_layout_opt_shard[key] = value[2:]
    elif isinstance(layout_obj, Cell):
        from mindspore.communication.management import get_process_group_ranks
        groups_ranks = (tuple(get_process_group_ranks()),)
        param_redundancy_dict = {param.name: groups_ranks for _, param in layout_obj.parameters_and_names()}
        sorted_param_redundancy_dict = {key: param_redundancy_dict[key] for key in sorted(param_redundancy_dict.keys())}
        return sorted_param_redundancy_dict
    else:
        parameter_layout = {}
        for k, v in layout_obj.items():
            parameter_layout[k] = v[:2]

    param_redundancy_dict = {}

    if initial_rank is None:
        initial_rank = _get_initial_rank(parameter_layout)

    _get_parameter_redundancy_without_opt_shard(parameter_layout, param_redundancy_dict, initial_rank)

    if isinstance(layout_obj, str):
        _get_strategy_opt_shard(param_redundancy_dict, parameter_layout_opt_shard)
    else:
        _get_layout_opt_shard(layout_obj, param_redundancy_dict)

    sorted_param_redundancy_dict = {key: param_redundancy_dict[key] for key in sorted(param_redundancy_dict.keys())}
    return sorted_param_redundancy_dict


def _collect_settings_by_rank(redundancy_map):
    """
    Collect parameter redundancy map by rank id.

    {"param1":((1,3,5,7),(2,4,6,8)),"param2":((1,3,5,7),(2,4,6,8))}
    ->{(1,3,5,7):{"param1", "param2"},(2,4,6,8):{"param1", "param2"}}
    """
    redundancy_map_reversed = {}
    for key, redundancy in redundancy_map.items():
        for index, item in enumerate(redundancy):
            redundancy_map_reversed.setdefault(item, []).append(
                (key, index))
    return redundancy_map_reversed


def _restructure(input_dict):
    """
    Flatten and reorganize the nested dictionary structure."""
    if all(not isinstance(item, tuple) for item in input_dict):
        return input_dict
    res_dict = {}
    for key, values in input_dict.items():
        for index, value in enumerate(values):
            res_dict.setdefault(key[index % len(key)], []).append(value)
    return _restructure(res_dict)


def _rotate_list_elements(i, input_list):
    """Rotate element list."""
    rotated_list = [input_list[(i + j) % len(input_list)] for j in
                    range(len(input_list))]
    return rotated_list


def remove_param_redundancy(param_redundancy_dict, keep_redundancy=1):
    """
    Remove parameter redundancy, get the single parameter for each rank id.
    Args:
        param_redundancy_dict (Dict): Parameter redundancy dict.
        keep_redundancy (Int): Keep redundancy number.

    Returns:
        Dict, single parameter for each rank id. Key is rank_id, value is set(params).

    Examples:
        >>> from mindspore.train.utils import get_parameter_redundancy, remove_param_redundancy
        >>> param_redundancy_dict = get_parameter_redundancy("/path/to/strategy.ckpt")
        >>> single_parameter = remove_param_redundancy(param_redundancy_dict)
        {0: {param1, param3}, 1: {param2, param4},,,}}
    """
    redundancy_dict_reversed = _collect_settings_by_rank(param_redundancy_dict)
    sorted_layouts = {}
    for device_layout, layer_names_list in redundancy_dict_reversed.items():
        sorted_layer_names = [item[0] for item in layer_names_list]
        sorted_layouts[device_layout] = sorted_layer_names
    result = {}
    for i in range(keep_redundancy):
        rotated_layouts = {tuple(_rotate_list_elements(i, key)): value for
                           key, value in sorted_layouts.items()}
        restructured_layouts = _restructure(rotated_layouts)
        for key, value in restructured_layouts.items():
            result.setdefault(key, set()).update(set(value))
    return result


def parse_hccl_file(hccl_file_path):
    """
    Parses an HCCL configuration JSON file, return a dict key is rank_id, value is device_ip.

    Args:
        hccl_file_path (str): The path to the HCCL configuration JSON file.

    Returns:
        Dict: A Dict, key is rank_id, value is device_ip.

    Examples:
        >>> from mindspore.train.utils import parse_hccl_file
        >>> rankid_dict = parse_hccl_file("/path/to/hccl.json")
        {0: "10.11.10.163", 1: "10.11.10.164", 2: "10.11.10.165", 3: "10.11.10.166",,,,}
    """
    with open(hccl_file_path) as f:
        hccl_dict = json.load(f)
    server_list = hccl_dict["server_list"]
    rankid_dict = {}
    for server in server_list:
        device_list = server["device"]
        for device in device_list:
            rankid_dict[int(device["rank_id"])] = device["device_ip"]

    return rankid_dict


def _progress_bar(iterable, total=None):
    """
    Decorate an iterable object, returning an iterator which acts exactly
    like the original iterable, but prints a dynamically updating
    progressbar every time a value is requested.
    """
    if total is None:
        total = len(iterable)

    start_time = time.time()

    def print_progress_bar(iteration):
        percent = f"{100 * (iteration / float(total)):.1f}"
        bar_length = 40
        filled_length = int(bar_length * iteration // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time / iteration * total
        remaining_time = estimated_total_time - elapsed_time

        elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        remaining_time_str = time.strftime("%H:%M:%S", time.gmtime(remaining_time))

        sys.stdout.reconfigure(encoding="utf-8")
        print(f'\r{percent}%|{bar}|[{elapsed_time_str}<{remaining_time_str}]', end='')
        if iteration == total:
            print()

    for i, item in enumerate(iterable, start=1):
        yield item
        print_progress_bar(i)


def _load_and_transform(path, name_map, load_func, transform_func=None):
    """use load_func to load and use transform_func to convert"""
    if load_func is not None:
        param_dict = load_func(path)
    else:
        param_dict = path
    transform_dict = {}
    for k, v in param_dict.items():
        new_name = name_map.get(k, k) if name_map is not None else k
        if transform_func is not None:
            transform_dict[new_name] = transform_func(v, new_name)
        else:
            transform_dict[new_name] = v
    return transform_dict
