# Copyright 2023-2024 Huawei Technologies Co., Ltd
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
"""Utils of auto parallel"""
import os
from time import perf_counter
from importlib import import_module
import numpy as np
import mindspore as ms
from mindspore import context, log as logger
from mindspore._c_expression import reset_op_id, reset_op_id_with_offset
from mindspore.common.tensor import Tensor
from mindspore.common.dtype import _dtype_to_nptype
from mindspore.common import dtype as mstype
from mindspore.communication.management import get_group_size, get_rank
from mindspore.communication._comm_helper import _is_initialized
from mindspore.parallel.shard import Layout
from mindspore.parallel._auto_parallel_context import auto_parallel_context, _set_auto_parallel_context, \
    _reset_auto_parallel_context
from mindspore.common.seed import get_seed
from mindspore._c_expression import GraphExecutor_, TensorPy as Tensor_
from mindspore.parallel._tensor import _load_tensor_by_layout, _load_tensor_shape_by_layout

SUPPORTED_TUPLE_IN_TUPLE_STRATEGY = ["GroupedMatmul", "FusedInferAttentionScore", "Custom", "Index"]


# disable pylint too broad Exception
# pylint: disable=W0212
def _init_auto_parallel_context(net):
    """Parse the member variables of AutoParallel(cell) to the auto parallel context. """
    if net is None or net.__class__.__name__ != "AutoParallel":
        pass
    else:
        parallel_mode = "semi_auto_parallel"
        search_mode = "recursive_programming"
        if net._device_num == 1:
            parallel_mode = "stand_alone"
        elif net._parallel_mode in ["recursive_programming", "sharding_propagation"]:
            search_mode = net._parallel_mode
            parallel_mode = "auto_parallel"
        params = {
            "auto_parallel_new_interface": True,
            "init_param_in_compile": net._init_param_in_compile,
            "device_num": net._device_num,
            "global_rank": net._global_rank,
            "parallel_mode": parallel_mode,
            "search_mode": search_mode,
            "comm_fusion": net._comm_fusion_config,
            "strategy_ckpt_load_file": net._load_strategy_file_path,
            "strategy_ckpt_save_file": net._save_strategy_file_path,
            "strategy_ckpt_config": {
                "load_file": net._load_strategy_file_path,
                "save_file": net._save_strategy_file_path,
                "only_trainable_params": net._only_trainable_params
            },
            "dataset_strategy": net._dataset_strategy_config,
            "full_batch": net._full_batch,
            "force_fp32_communication": net._force_fp32_communication,
            "enable_alltoall": net._enable_alltoall,
            "parameter_broadcast": net._parameter_broadcast,
            "group_ckpt_save_file": net._group_ckpt_save_file,
            "dump_local_norm": net._dump_local_norm,
            "dump_local_norm_path": net._dump_local_norm_path,
            "dump_device_local_norm": net._dump_device_local_norm,
            "gradients_mean": net._gradients_mean,
            "gradient_fp32_sync": net._gradient_fp32_sync,
            "loss_repeated_mean": net._loss_repeated_mean
        }

        # hsdp
        params["enable_parallel_optimizer"] = net._enable_parallel_optimizer
        if params["enable_parallel_optimizer"]:
            parallel_optimizer_config = {}
            if net._parallel_optimizer_threshold != -1:
                parallel_optimizer_config["parallel_optimizer_threshold"] = net._parallel_optimizer_threshold
            if net._optimizer_weight_shard_size != -1:
                parallel_optimizer_config["optimizer_weight_shard_size"] = net._optimizer_weight_shard_size
            parallel_optimizer_config["optimizer_level"] = net._optimizer_level
            params['parallel_optimizer_config'] = parallel_optimizer_config

        # pipeline
        params["pipeline_stages"] = net._pipeline_stages
        if params["pipeline_stages"] > 1:
            params['pipeline_result_broadcast'] = net._pipeline_result_broadcast
            params['pipeline_config'] = {
                "pipeline_interleave": net._pipeline_interleave,
                "pipeline_scheduler": net._pipeline_scheduler
            }

        # set_op_strategy_config
        if parallel_mode == "auto_parallel" and search_mode == "sharding_propagation":
            from mindspore.parallel.checkpoint_transform import set_op_strategy_config
            if net._load_operator_strategy_file != "":
                set_op_strategy_config(mode="LOAD", path=net._load_operator_strategy_file)
            if net._save_operator_strategy_file != "":
                set_op_strategy_config(mode="SAVE", path=net._save_operator_strategy_file)

        _set_auto_parallel_context(**params)
        net.transformer_opt(net._transformer_opt_config)


def _clear_auto_parallel_context(net):
    if net is None or net.__class__.__name__ != "AutoParallel":
        pass
    else:
        _reset_auto_parallel_context()
        net.transformer_opt(None)


def _get_auto_parallel_net(net):
    for _, cell in net.cells_and_names():
        if type(cell).__name__ == 'AutoParallel':
            return cell
    return net


def _parallel_mode_map(parallel_mode):
    """Map parallel mode."""
    parallel_mode_map = {
        "sharding_propagation": "auto_parallel",
        "recursive_programming": "auto_parallel",
        "semi_auto": "semi_auto_parallel"
    }
    parallel_mode_res = parallel_mode_map.get(parallel_mode, 'Not Exits')
    if parallel_mode_res == 'Not Exits':
        raise ValueError("Invalid parallel_mode input, expect one of 'semi_auto', 'sharding_propagation', "
                         "'recursive_programming', but got the value: {}.".format(parallel_mode))
    return parallel_mode_res



def _get_parallel_mode():
    """Get parallel mode."""
    return auto_parallel_context().get_parallel_mode()


def _is_sharding_propagation():
    """Is sharding propagation."""
    return (auto_parallel_context().get_strategy_search_mode() == "sharding_propagation") or (
        auto_parallel_context().get_sharding_propagation())


def _is_in_auto_parallel_mode():
    return _get_parallel_mode() in [ms.ParallelMode.SEMI_AUTO_PARALLEL, ms.ParallelMode.AUTO_PARALLEL]


def _is_parallel_mode():
    if not _is_initialized():
        return False
    if os.getenv("RUN_MODE") != "predict":
        return False
    if get_group_size() > 1 and _get_parallel_mode() == ms.ParallelMode.STAND_ALONE:
        return True
    return False


def _is_in_data_parallel_mode():
    return _get_parallel_mode() == ms.ParallelMode.DATA_PARALLEL


def _is_in_hybrid_parallel_mode():
    return _get_parallel_mode() == ms.ParallelMode.HYBRID_PARALLEL


def _get_full_batch():
    """Get whether to use full_batch."""
    return auto_parallel_context().get_full_batch()


def _get_pipeline_stages():
    """Get pipeline stages"""
    return auto_parallel_context().get_pipeline_stages()


def _check_full_batch():
    """
    full_batch could only be used under semi_auto_parallel or auto_parallel, check it.

    Raises:
        RuntimeError: Using full_batch under neither semi_auto_parallel nor auto_parallel.
    """
    parallel_mode = _get_parallel_mode()
    full_batch = _get_full_batch()
    if ((parallel_mode not in ("semi_auto_parallel", "auto_parallel")) and full_batch):
        raise RuntimeError("full_batch could only be used under semi_auto_parallel or auto_parallel.")


def _need_to_full():
    """Check whether to convert input to full shape or tensor."""
    if _get_parallel_mode() not in ("semi_auto_parallel", "auto_parallel"):
        return False
    dataset_strategy = context.get_auto_parallel_context("dataset_strategy")
    if dataset_strategy and dataset_strategy not in ("data_parallel", "full_batch"):
        return True
    return not _get_full_batch()


class ParallelParamInitProfCtx:
    """Collect parallel param initialization performance context mgr."""

    def __init__(self, parameter, func_name):
        self.parameter = parameter
        self.func_name = func_name
        self.start_timestamp = None

    def __enter__(self):
        self.start_timestamp = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        end_timestamp = perf_counter()
        duration = end_timestamp - self.start_timestamp
        if os.getenv("MS_DEV_PARAM_INIT_PROF_COLLECT"):
            logger.warning(f"{self.func_name}: {self.parameter.name}, shape: {self.parameter.shape}, "
                           f"sliced: {self.parameter.sliced}, duration: {duration}")


def _slice_parameter(parameter, phase, layout):
    """Slice python parameter obj according to the layout."""
    new_interface_flag = auto_parallel_context().get_auto_parallel_new_interface()
    init_param_in_compile = auto_parallel_context().get_init_param_in_compile()
    if not new_interface_flag:
        if getattr(parameter, "init_param", False) and parameter.has_init:
            if layout is None:
                parameter.sliced = True
                return
            if not parameter.sliced:
                rank = get_rank()
                new_tensor_shape = _load_tensor_shape_by_layout(parameter, layout, rank)
                parameter.shape = new_tensor_shape
                if hasattr(parameter.init_mode, "shape") and parameter.init_mode.shape != parameter.shape:
                    parameter.init_mode.shape = new_tensor_shape
                parameter.sliced = True
        else:
            graph_executor = GraphExecutor_.get_instance()
            new_param = parameter.init_data(layout, set_sliced=True)
            parameter = new_param
            graph_executor.updata_param_node_default_input(phase, {parameter.name: parameter})
            if layout is None:
                parameter.sliced = True
                return
            if not parameter.sliced:
                rank = get_rank()
                new_tensor = _load_tensor_by_layout(parameter, layout, rank)
                parameter.set_data(new_tensor, True)
    else:
        if init_param_in_compile or parameter.has_init is False:
            graph_executor = GraphExecutor_.get_instance()
            new_param = parameter.init_data(layout, set_sliced=True)
            parameter = new_param
            graph_executor.updata_param_node_default_input(phase, {parameter.name: parameter})
            if layout is None:
                parameter.sliced = True
                return
            if not parameter.sliced:
                rank = get_rank()
                new_tensor = _load_tensor_by_layout(parameter, layout, rank)
                parameter.set_data(new_tensor, True)
        else:
            if layout is None:
                parameter.sliced = True
                return
            if not parameter.sliced:
                rank = get_rank()
                new_tensor_shape = _load_tensor_shape_by_layout(parameter, layout, rank)
                parameter.shape = new_tensor_shape
                if hasattr(parameter.init_mode, "shape") and parameter.init_mode.shape != parameter.shape:
                    parameter.init_mode.shape = new_tensor_shape
                parameter.sliced = True


def _slice_tensor(tensor, layout, rank_id):
    """Slice python tensor obj according to the layout."""
    new_tensor = _load_tensor_by_layout(tensor, layout, rank_id)
    return new_tensor


def _init_optimizer_state(parameter, phase):
    """init optimizer state"""
    if not parameter.has_init:
        return
    graph_executor = GraphExecutor_.get_instance()
    new_param = parameter.init_data()
    parameter = new_param
    graph_executor.updata_param_node_default_input(phase, {parameter.name: parameter})


def _to_full_shape_layout(shapes, dataset_strategy):
    """to full shape for layout"""
    new_shapes = []
    for index, shape in enumerate(shapes):
        layout = dataset_strategy[index]
        layout_dict = layout.to_dict()
        devmat = layout_dict["device_matrix"]
        tensormap = layout_dict["tensor_map"]
        new_shape = []
        for i, item in enumerate(shape):
            correspond_tensor_map = tensormap[i]
            shard_size = 1
            if isinstance(correspond_tensor_map, tuple):
                for value in correspond_tensor_map:
                    if value != -1:
                        shard_size *= devmat[len(devmat) - value - 1]
            else:
                if correspond_tensor_map != -1:
                    shard_size *= devmat[len(devmat) - correspond_tensor_map - 1]
            if item > 0:
                new_shape += (item * shard_size,)  # static shape
            else:
                new_shape += (item,)  # dynamic shape
        new_shapes.append(new_shape)
    return new_shapes


def _to_full_shapes(shapes, device_num):
    """Expanding batch dimension according to device_num, adapt to mindspore minddata graph solution."""
    new_shapes = []
    dataset_strategy = ()
    if context.get_auto_parallel_context("dataset_strategy") not in ("data_parallel", "full_batch"):
        dataset_strategy = context.get_auto_parallel_context("dataset_strategy")
    if dataset_strategy:
        if len(shapes) != len(dataset_strategy):
            raise ValueError("The input shapes size {} is not equal to "
                             "dataset strategy size {}".format(len(shapes), len(dataset_strategy)))
        if isinstance(dataset_strategy[0], Layout):
            return _to_full_shape_layout(shapes, dataset_strategy)
        for index, shape in enumerate(shapes):
            if len(shape) != len(dataset_strategy[index]):
                raise ValueError("The input shapes item size {} is not equal to "
                                 "dataset strategy item size {}".format(len(shape), len(dataset_strategy[index])))
            new_shape = []
            for i, item in enumerate(shape):
                if item > 0:
                    new_shape += (item * dataset_strategy[index][i],)  # static shape
                else:
                    new_shape += (item,)  # dynamic shape
            new_shapes.append(new_shape)
        return new_shapes
    for shape in shapes:
        shape_v = []
        for i, item in enumerate(shape):
            if i == 0 and item > 0:
                shape_v += (item * device_num,)  # only for static shape
            else:
                shape_v += (item,)
        new_shapes.append(shape_v)
    return new_shapes


def _origin_shapes(shapes):
    """resume origin shape after full shape."""
    if _need_to_full():
        device_num = _get_device_num() // _get_pipeline_stages()
    else:
        return shapes
    new_shapes = []
    dataset_strategy = ()
    if context.get_auto_parallel_context("dataset_strategy") not in ("data_parallel", "full_batch"):
        dataset_strategy = context.get_auto_parallel_context("dataset_strategy")
    if dataset_strategy:
        if len(shapes) != len(dataset_strategy):
            raise ValueError("The input shapes size {} is not equal to "
                             "dataset strategy size {}".format(len(shapes), len(dataset_strategy)))
        for index, shape in enumerate(shapes):
            if len(shape) != len(dataset_strategy[index]):
                raise ValueError("The input shapes item size {} is not equal to "
                                 "dataset strategy item size {}".format(len(shape), len(dataset_strategy[index])))
            new_shape = []
            for i, item in enumerate(shape):
                if item > 0:
                    new_shape += (item // dataset_strategy[index][i],)  # static shape
                else:
                    new_shape += (item,)  # dynamic shape
            new_shapes.append(new_shape)
        return new_shapes
    for shape in shapes:
        shape_v = []
        for i, item in enumerate(shape):
            if i == 0 and item > 0:
                shape_v += (item // device_num,)  # only for static shape
            else:
                shape_v += (item,)
        new_shapes.append(shape_v)
    return new_shapes


def _dynamic_shape_for_dataset(dataset_shapes, dynamic_shapes):
    """convert static dataset shapes to dynamic shape"""
    if len(dataset_shapes) != len(dynamic_shapes):
        raise ValueError("The dataset shapes size of {} is not equal to "
                         "dynamic shapes size of {}".format(dataset_shapes, dynamic_shapes))
    ret = dataset_shapes
    for i in range(len(dynamic_shapes)):
        if len(dataset_shapes[i]) != len(dynamic_shapes[i]):
            raise ValueError("The dataset shapes size of {} is not equal to "
                             "dynamic shapes size of {}".format(dataset_shapes, dynamic_shapes))
        for j in range(len(dynamic_shapes[i])):
            if dynamic_shapes[i][j] == -1:
                ret[i][j] = -1
    return ret


def _to_full_tensor(elem, global_device_num, global_rank, scaling_sens=None):
    """Convert numpy to tensor, expanding batch dimension according to device_num, adapt to feed the data
       from host solution.
    """
    lst = []
    device_num = global_device_num // _get_pipeline_stages()
    stage_rank = global_rank % device_num
    if not isinstance(elem, (tuple, list)):
        elem = [elem]
    if stage_rank >= device_num:
        raise ValueError("The global rank must be smaller than device number, the global rank is {}, "
                         "the device num is {}".format(stage_rank, device_num))
    dataset_strategy = ()
    if context.get_auto_parallel_context("dataset_strategy") not in ("data_parallel", "full_batch"):
        dataset_strategy = context.get_auto_parallel_context("dataset_strategy")
    if elem and dataset_strategy:
        if len(elem) != len(dataset_strategy):
            raise ValueError("The input size {} is not equal to "
                             "dataset strategy size {}".format(len(elem), len(dataset_strategy)))
    for index, data in enumerate(elem):
        if isinstance(data, np.ndarray):
            data = Tensor(data)
        if not isinstance(data, Tensor):
            raise ValueError("elements in tensors must be Tensor")
        shape_ = data.shape
        type_ = data.dtype
        new_shape = ()
        if not dataset_strategy:
            batchsize_per_device = 1
            for i, item in enumerate(shape_):
                if i == 0:
                    new_shape += (item * device_num,)
                    batchsize_per_device = item
                else:
                    new_shape += (item,)
            new_tensor_numpy = np.zeros(new_shape, _dtype_to_nptype(type_))  # pylint:disable=protected-access
            start = stage_rank * batchsize_per_device
            new_tensor_numpy[start: start + batchsize_per_device] = data.asnumpy()
        else:
            if len(shape_) != len(dataset_strategy[index]):
                raise ValueError("The input shapes item size {} is not equal to "
                                 "dataset strategy item size {}".format(len(shape_), len(dataset_strategy[index])))
            slice_index = ()
            for i, item in enumerate(shape_):
                new_shape += (item * dataset_strategy[index][i],)
                start = (stage_rank % dataset_strategy[index][i]) * item
                end = (stage_rank % dataset_strategy[index][i] + 1) * item
                s = slice(start, end, 1)
                slice_index += (s,)
            new_tensor_numpy = np.zeros(new_shape, _dtype_to_nptype(type_))  # pylint:disable=protected-access
            new_tensor_numpy[slice_index] = data.asnumpy()
        new_tensor = Tensor(new_tensor_numpy, dtype=type_)
        lst.append(new_tensor)
    if scaling_sens:
        lst.append(Tensor(scaling_sens, mstype.float32))
    return tuple(lst)


def _get_gradients_mean():
    """Get if using gradients_mean."""
    return auto_parallel_context().get_gradients_mean()


def _get_device_num():
    """Get the device num."""
    parallel_mode = auto_parallel_context().get_parallel_mode()
    if parallel_mode == "stand_alone":
        device_num = 1
        return device_num

    if auto_parallel_context().get_device_num_is_set() is False:
        device_num = get_group_size()
    else:
        device_num = auto_parallel_context().get_device_num()
    return device_num


def _get_stage_device_num():
    """Get the device number of each pipeline stage"""
    return _get_device_num() // _get_pipeline_stages()


def _get_global_rank():
    """Get the global rank."""
    parallel_mode = auto_parallel_context().get_parallel_mode()
    if parallel_mode == "stand_alone":
        global_rank = 0
        return global_rank

    if auto_parallel_context().get_global_rank_is_set() is False:
        global_rank = get_rank()
    else:
        global_rank = auto_parallel_context().get_global_rank()
    return global_rank


def _get_parameter_broadcast():
    """Get the parameter broadcast."""
    parallel_mode = auto_parallel_context().get_parallel_mode()
    parameter_broadcast = auto_parallel_context().get_parameter_broadcast()

    if parallel_mode in ("data_parallel", "hybrid_parallel") and parameter_broadcast is False and get_seed() is None:
        logger.warning("You are suggested to use mindspore.context.set_auto_parallel_context(parameter_broadcast=True)"
                       " or mindspore.common.set_seed() to share parameters among multi-devices.")

    return parameter_broadcast


def _get_enable_parallel_optimizer():
    """Get if using parallel optimizer."""
    return auto_parallel_context().get_enable_parallel_optimizer()


def _get_grad_accumulation_shard():
    """Get if using parallel shard."""
    return auto_parallel_context().get_grad_accumulation_shard()


def _device_number_check(parallel_mode, device_number):
    """
    Check device num.

    Args:
        parallel_mode (str): The parallel mode.
        device_number (int): The device number.
    """
    if parallel_mode == "stand_alone" and device_number != 1:
        raise ValueError("If parallel_mode is stand_alone, device_number must be 1, "
                         "device_number: {0}, parallel_mode:{1}".format(device_number, parallel_mode))


def _parameter_broadcast_check(parallel_mode, parameter_broadcast):
    """
    Check parameter broadcast.

    Note:
        If parallel mode is semi_auto_parallel or auto_parallel, parameter broadcast is not supported. Using the same
        random seed to make sure parameters on multiple devices are the same.

    Args:
        parallel_mode (str): The parallel mode.
        parameter_broadcast (bool): The parameter broadcast.

    Raises:
        ValueError: If parameter is broadcasted
                    but the parallel mode is "stand_alone" or "semi_auto_parallel" or "auto_parallel").
    """
    if parameter_broadcast is True and parallel_mode in ("stand_alone", "semi_auto_parallel", "auto_parallel"):
        raise ValueError("stand_alone, semi_auto_parallel and auto_parallel "
                         "do not support parameter broadcast, parallel_mode: {0}, parameter_broadcast:{1}"
                         .format(parallel_mode, parameter_broadcast))


def _get_python_op(op_name, op_path, instance_name, arglist):
    """Get python operator."""
    module = import_module(op_path)
    cls = getattr(module, op_name)
    if op_path != "mindspore.ops.functional":
        # The AllGather attrs contains group_name and group_ranks, pop group_ranks.
        if op_name == "AllGather" and len(arglist) == 2:
            arglist.pop()
        op = cls(*arglist)
    else:
        op = cls
    op.set_prim_instance_name(instance_name)
    return op


def _reset_op_id():
    """Reset op id."""
    reset_op_id()


def _reset_op_id_with_offset():
    """Reset op id with offset."""
    reset_op_id_with_offset()


def _parallel_predict_check():
    """validate parallel model prediction"""
    if _is_in_auto_parallel_mode():
        dataset_strategy = context.get_auto_parallel_context("dataset_strategy")
        is_shard_dataset_mp = (dataset_strategy and dataset_strategy not in ("data_parallel", "full_batch"))
        if not context.get_auto_parallel_context("full_batch") and not is_shard_dataset_mp:
            logger.warning('Using non full-batch dataset in model prediction may lead to incorrect data.')


def _check_similar_layout(tensor_layout1, tensor_layout2):
    """check if two tensor layouts are same"""
    if tensor_layout1[1] != tensor_layout2[1]:
        return False
    for i in tensor_layout1[1]:
        if i == -1:
            continue
        if tensor_layout1[0][-1 - i] != tensor_layout2[0][-1 - i]:
            return False
    return True


def _check_same_layout(tensor_layout1, tensor_layout2):
    """check if two tensor layouts are same"""
    return tensor_layout1[0] == tensor_layout2[0] and tensor_layout1[1] == tensor_layout2[1]


def _remove_repeated_slices(tensor_layout):
    """generate unrepeated tensor layout"""
    import copy
    new_tensor_layout = copy.deepcopy(tensor_layout)
    dev_mat = tensor_layout[0][:]
    tensor_map = tensor_layout[1]
    for dim in range(len(dev_mat)):
        if dim not in tensor_map:
            dev_mat[-1 - dim] = 1
    new_tensor_layout[0] = dev_mat
    return new_tensor_layout


def _infer_rank_list(train_map, predict_map=None):
    """
    infer checkpoint slices to be loaded.
    map value format: [dev_mat, tensor_map, param_split_shape, field_size, opt_shard_stride, opt_shard_size]
    """
    ret = {}
    if _get_pipeline_stages() > 1:
        local_rank = int(_get_global_rank() % (_get_device_num() / _get_pipeline_stages()))
    else:
        local_rank = _get_global_rank()
    for param_name in train_map:
        train_layout = train_map[param_name]
        train_dev_mat = train_layout[0]
        dev_num = np.array(train_dev_mat).prod()
        new_train_layout = _remove_repeated_slices(train_layout)
        array = np.arange(dev_num).reshape(train_dev_mat)
        index = ()
        for i in new_train_layout[0]:
            if i == 1:
                index = index + (0,)
            else:
                index = index + (slice(None),)
        rank_list = array[index].flatten()
        if not predict_map:
            ret[param_name] = (rank_list, False)
            continue
        if param_name not in predict_map:
            logger.warning("predict_map does not contain %s", param_name)
            continue
        predict_layout = predict_map[param_name]
        dev_num = np.array(predict_layout[0]).prod()
        # optimization pass
        if _check_same_layout(train_layout, predict_layout):
            ret[param_name] = ([local_rank], True)
            continue
        if _check_similar_layout(train_layout, predict_layout):
            if len(rank_list) == 1:
                ret[param_name] = (rank_list, True)
            elif len(rank_list) == dev_num:
                ret[param_name] = ([rank_list[local_rank]], True)
            else:
                ret[param_name] = (rank_list, False)
        else:
            ret[param_name] = (rank_list, False)
    return ret


def _handle_symbol_inputs(symbol_inputs):
    """handle symbol inputs"""
    dataset_strategy = ()
    divisor_key = "divisor"
    # dataset strategy is set
    if context.get_auto_parallel_context("dataset_strategy") not in ("data_parallel", "full_batch"):
        dataset_strategy = context.get_auto_parallel_context("dataset_strategy")
    if dataset_strategy:
        if len(symbol_inputs) != len(dataset_strategy):
            raise ValueError("The symbol_inputs size {} is not equal to "
                             "dataset strategy size {}".format(len(symbol_inputs), len(dataset_strategy)))
        for index, shape in enumerate(symbol_inputs):
            dataset_ele_s = dataset_strategy[index]
            if len(shape) != len(dataset_ele_s):
                raise ValueError("The symbol_inputs item size {} is not equal to "
                                 "dataset strategy item size {}".format(len(shape), len(dataset_ele_s)))

            for i, item in enumerate(shape):
                if isinstance(item, dict):  # symbol
                    symbol_inputs[index][i][divisor_key] = symbol_inputs[index][i][divisor_key] * dataset_ele_s[i]
                else:  # common shape
                    symbol_inputs[index][i] = item * dataset_ele_s[i]

        return symbol_inputs

    # full batch is set
    device_num = _get_device_num() // _get_pipeline_stages()
    for index, shape in enumerate(symbol_inputs):
        for i, item in enumerate(shape):
            if i == 0 and isinstance(item, dict):  # symbol
                symbol_inputs[index][i][divisor_key] = symbol_inputs[index][i][divisor_key] * device_num

    return symbol_inputs


def _no_need_to_change_symbols(shapes):
    """no need to handle the symbol if full_batch is true or it's not parallel mode"""
    if not _need_to_full():
        return True

    # if static shape, return
    is_dynamic_shape = False
    for shape in shapes:
        if any(i < 0 for i in shape):
            is_dynamic_shape = True
            break
    if is_dynamic_shape is False:
        return True

    return False


def _change_symbols_for_parallel(shapes, symbol_inputs=None):
    """create or modify symbol inputs"""
    if _no_need_to_change_symbols(shapes) is True:
        return symbol_inputs
    # the symbol_inputs is [[{'divisor': 8}, 16], [{'divisor': 8}, 16]]
    # the dataset_shapes is [(-1, 16), (-1, 16)]
    # if symbol_inputs is [None, None, ..., None], reset it
    if symbol_inputs is not None and all(s is None for s in symbol_inputs):
        symbol_inputs = []

    # if symbol inputs is none or empty, create default symbol inputs
    # if symbol inputs is not none, handle the empty symbol
    divisor_key = "divisor"
    if symbol_inputs is None or bool(symbol_inputs) is False:
        symbol_inputs = [list(shape) for shape in shapes]  # tuple to list
        for i, s in enumerate(symbol_inputs):
            for j, item in enumerate(s):
                if item == -1:
                    symbol_inputs[i][j] = {divisor_key: 1}
    else:
        for i, s in enumerate(symbol_inputs):
            # the symbol_inputs may be [None, [{'divisor': 8}, 16]]
            # and the dataset_shapes is [(-1, 16), (-1, 16)], need to handle None
            if s is None:
                symbol_inputs[i] = shapes[i]
                for k, item in enumerate(symbol_inputs[i]):
                    if item == -1:
                        symbol_inputs[i][k] = {divisor_key: 1}
                s = symbol_inputs[i]
            for j, item in enumerate(s):
                if isinstance(item, dict) and bool(item) is False:  # the item is empty
                    symbol_inputs[i][j] = {divisor_key: 1}

    return _handle_symbol_inputs(symbol_inputs)


def _grads_divided_by_device_num_if_recomputation(grads):
    """
    If in pynative parallel and full_batch is True, divide grads by device num to ensure that the gradients is correct.
    """
    if not _get_full_batch():
        return grads

    device_num = _get_device_num()
    logger.info(f"In PyNative mode, when parallel mode is in "
                f"({context.ParallelMode.SEMI_AUTO_PARALLEL}, {context.ParallelMode.AUTO_PARALLEL}) and "
                f"full_batch is Ture, the gradients will be automatically divided by device_num({device_num}).")

    if not isinstance(grads, (tuple, Tensor, Tensor_)):
        raise ValueError(f"The type of grads must be either Tuple[Tensor] or Tensor, but got {type(grads)}.")

    if isinstance(grads, tuple):
        new_grads = ()
        if grads:
            device_num_tensor = Tensor(device_num, grads[0].dtype)
            for grad in grads:
                new_grads += (grad / device_num_tensor,)
    else:
        device_num_tensor = Tensor(device_num, grads.dtype)
        new_grads = grads / device_num_tensor
    return new_grads


def _check_rank(cur_rank, initial_rank, pipeline_stages):
    """
    Check parameter for parameter_broadcast.
    """
    if cur_rank != get_rank():
        raise ValueError(f"For parameter broadcast, the cur_rank: {cur_rank} is wrong.")
    if initial_rank % (get_group_size() / pipeline_stages) != 0:
        raise ValueError(f"For parameter broadcast, the initial_rank: {initial_rank} is wrong.")
