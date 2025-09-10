# Copyright 2020-2024 Huawei Technologies Co., Ltd
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
"""Model."""
from __future__ import absolute_import

from collections.abc import Iterable
from functools import wraps

import sys
import os
import math
import copy
import importlib
import time
import numpy as np

import mindspore
from mindspore import log as logger
from mindspore.train.serialization import save_checkpoint, load_checkpoint
from mindspore.train.callback._checkpoint import ModelCheckpoint, _chg_ckpt_file_name_if_same_exist
from mindspore.common.tensor import Tensor
from mindspore.train.metrics import get_metrics, get_metric_fn
from mindspore._checkparam import check_input_data, check_output_data
from mindspore import _checkparam as Validator
from mindspore.train.callback import _InternalCallbackParam, RunContext, _CallbackManager, Callback, TimeMonitor,\
    TrainFaultTolerance
from mindspore.train.callback import __all__ as internal_cb_names
from mindspore.train.callback._cluster_monitor import ClusterMonitor
from mindspore import context
from mindspore.parallel._utils import _get_parallel_mode, _get_device_num, _get_parameter_broadcast, \
    _device_number_check, _parameter_broadcast_check, _parallel_predict_check, \
    _reset_op_id_with_offset
from mindspore.parallel._ps_context import _is_role_worker, _is_role_pserver, _is_ps_mode, \
    _cache_enable, _enable_distributed_mindrt
from mindspore.train.metrics import Loss
from mindspore.log import vlog_print
from mindspore import nn
from mindspore.boost import AutoBoost
from mindspore.context import ParallelMode
from mindspore.parallel._recovery_context import _set_recovery_context, _get_recovery_context
from mindspore.train.dataset_helper import DatasetHelper, connect_network_with_dataset
from mindspore.common.api import _pynative_executor, ARG_SPECIFIED, TOTAL_ARG_LEN
from mindspore.dataset.core.config import get_debug_mode
from mindspore.dataset.engine.datasets import _set_training_dataset, _reset_training_dataset
from mindspore.train import amp
from mindspore._c_expression import _framework_profiler_step_start, _framework_profiler_step_end
from mindspore._c_expression import _get_optimzer_timestamps
from mindspore._c_expression import clean_tdt_channel, _clean_rootinfo

from mindspore.parallel._utils import _init_auto_parallel_context, _clear_auto_parallel_context
from .serialization import load_param_into_net

def _transfer_tensor_to_tuple(inputs):
    """
    If the input is a tensor, convert it to a tuple. If not, the output is unchanged.
    """
    if isinstance(inputs, Tensor):
        return (inputs,)

    return inputs


class _StepSync(Callback):
    @staticmethod
    def step_end(run_context):
        _pynative_executor.sync()


class _FrameworkProfilerCallback(Callback):
    """
    Profiler callback of framework for training.
    """

    def step_begin(self, run_context):
        _framework_profiler_step_start()

    def step_end(self, run_context):
        _framework_profiler_step_end()


def _save_final_ckpt(func):
    """
    Decorator function, which saves the current checkpoint when an exception occurs during training.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        obj = None
        if kwargs.get('callbacks') and isinstance(kwargs.get('callbacks'), ModelCheckpoint):
            obj = kwargs.get('callbacks')
        if kwargs.get('callbacks') and isinstance(kwargs.get('callbacks'), list):
            for item in kwargs.get('callbacks'):
                if isinstance(item, ModelCheckpoint):
                    obj = item
        if obj and obj._config and obj._config.exception_save:
            try:
                func(self, *args, **kwargs)
            except BaseException as e:
                # pylint: disable=W0212
                prefix = _chg_ckpt_file_name_if_same_exist(obj._directory, obj._exception_prefix, True)
                cur_ckpoint_file = prefix + "-" + str(self._current_epoch_num) + "_" \
                                   + str(self._current_step_num) + "_breakpoint.ckpt"
                cur_file = os.path.join(obj._directory, cur_ckpoint_file)
                if "epoch_num" in obj._append_dict:
                    obj._append_dict["epoch_num"] = obj._append_epoch_num + self._current_epoch_num
                if "step_num" in obj._append_dict:
                    obj._append_dict["step_num"] = obj._append_step_num + self._current_step_num
                save_checkpoint(self._train_network, cur_file, obj._config.integrated_save, obj._config.async_save,
                                obj._append_dict, obj._config.enc_key, obj._config.enc_mode)
                raise e
        else:
            func(self, *args, **kwargs)

    return wrapper


def _handle_exception_info(obj, uce_env, tft, e):
    """handle exception info"""
    logger.info("uce wrapper caught RuntimeError")
    if not uce_env:
        logger.error("uce wrapper caught RuntimeError but uce not enable, enter MindIO TTP process.",
                     exc_info=True)
        if tft:
            tft.tft_report_error(tft.ReportState.RS_UNKNOWN.value)
        raise e
    e_str = str(e)
    logger.warning("uce wrapper caught RuntimeError e_str:{}".format(e_str))
    if "UCEError" in e_str:
        logger.info("uce wrapper report UCEError")
        obj.is_uce_rank = True
        # if error is HBM_MULTI_BIT_ECC_ERROR
        if "error_code=507054" in e_str:
            hbm_error_time, optimize_start, optimizer_end = _get_optimzer_timestamps()
            can_repair = tft.tft_can_do_uce_repair(hbm_error_time, optimize_start, optimizer_end)
            logger.info(f"UCEError of type HBM_MULTI_BIT_ECC_ERROR occurs, \
                        hbm_error_time={hbm_error_time}, optimize_start={optimize_start}, \
                        optimizer_end={optimizer_end}, can_repair={can_repair}")
            if not can_repair:
                logger.error(f"Caught UCEError of type HBM_MULTI_BIT_ECC_ERROR but can not repair, "
                             f"hbm_error_time={hbm_error_time}, optimize_start={optimize_start}, "
                             f"optimizer_end={optimizer_end}", exc_info=True)
                tft.tft_report_error(tft.ReportState.RS_UNKNOWN.value)
                raise e
        tft.tft_report_error(tft.ReportState.RS_UCE.value)
    elif "HCCEError" in e_str:
        logger.warning("uce wrapper caught HCCEError")
        tft.tft_report_error(tft.ReportState.RS_HCCL_FAILED.value)
    elif "ForceStopError" in e_str:
        logger.warning("uce wrapper caught RuntimeError ForceStopError")
        force_stop_err = tft.ReportState.RS_NORMAL.value
        tft.tft_report_error(force_stop_err)
    elif "ARF FINISH" in e_str:
        logger.warning(f"ARF FINISH")
        _set_recovery_context(is_arf=True)
        tft.tft_report_error(tft.ReportState.RS_PREREPAIR_FINISH.value)
    else:
        logger.error("uce wrapper caught other RuntimeError, enter MindIO TTP process.", exc_info=True)
        tft.tft_report_error(tft.ReportState.RS_UNKNOWN.value)
        raise e


def _handle_training_result_error(model, tft_obj):
    """
    Handle training result error for resuming training.
    """
    ckpt_load_fn = tft_obj.ckpt_load_func
    train_network = tft_obj.cb_params.train_network
    logger.warning("Process training result error start.")
    # 1. Clear tdt channel
    logger.warning("Clean tdt channel.")
    clean_tdt_channel()

    # 2. Load checkpoint
    logger.warning("Load checkpoint.")
    new_param_dict, remove_redundancy = ckpt_load_fn()
    param_not_load, ckpt_not_load = load_param_into_net(train_network, new_param_dict, True, remove_redundancy)
    logger.warning(f"param_not_load: {param_not_load}")
    logger.warning(f"ckpt_not_load: {ckpt_not_load}")
    resume_epoch = new_param_dict.get('epoch_num')
    resume_step = new_param_dict.get('step_num')
    model._initial_step = int(resume_step.asnumpy())
    logger.warning("Process training result error end.")
    return (resume_epoch, resume_step)


def _calc_cb_initial_step(org_epoch, org_step, *args, **kwargs):
    """calculate initial step for callback"""
    train_dataset = args[1]
    dataset_sink_mode = args[3] if len(args) > 3 else kwargs.get('dataset_sink_mode', True)
    sink_size = args[4] if len(args) > 4 else kwargs.get('sink_size', -1)

    cb_initial_step = 0
    if dataset_sink_mode:
        train_dataset.set_init_step(org_epoch)
        dataset_size = train_dataset.get_dataset_size()
        if sink_size != -1:
            cb_initial_step = org_epoch * sink_size + org_step
        else:
            cb_initial_step = org_epoch * dataset_size + org_step
    else:
        train_dataset.set_init_step(org_step)
        cb_initial_step = org_step
    if hasattr(train_dataset, '_dataset_helper'):
        dataset_helper = train_dataset._dataset_helper
        _reset_training_dataset(cb_initial_step, dataset_helper.iter.dataset.get_dataset_size())
    return cb_initial_step


def _update_ckpt_callback_info(resume_train_step, **kwargs):
    """
    Update checkpoint callback internal state
    """
    ckpt_obj = None
    if kwargs.get('callbacks') and isinstance(kwargs.get('callbacks'), ModelCheckpoint):
        ckpt_obj = kwargs.get('callbacks')
    if kwargs.get('callbacks') and isinstance(kwargs.get('callbacks'), list):
        for item in kwargs.get('callbacks'):
            if isinstance(item, ModelCheckpoint):
                ckpt_obj = item
    if ckpt_obj is not None:
        ckpt_obj._last_triggered_step = 0
        ckpt_obj._append_step_num = resume_train_step


def _handle_tft(func):
    """
    Decorator function, which starts uce handle process when an exception occurs during training.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        obj = None
        if kwargs.get('callbacks') and isinstance(kwargs.get('callbacks'), TrainFaultTolerance):
            obj = kwargs.get('callbacks')
        if kwargs.get('callbacks') and isinstance(kwargs.get('callbacks'), list):
            for item in kwargs.get('callbacks'):
                if isinstance(item, TrainFaultTolerance):
                    obj = item
        if obj:
            tft_env = os.getenv("MS_ENABLE_TFT", "")
            uce_env = "UCE:1" in tft_env or "ARF:1" in tft_env or "HCCE:1" in tft_env
            tre_env = "TRE:1" in tft_env
            while True:
                try:
                    return func(self, *args, **kwargs)
                except RuntimeError as e:
                    if tre_env and 'TREError' in str(e):
                        _, resume_step = _handle_training_result_error(self, obj)
                        repair_step = int(resume_step.asnumpy())
                        _update_ckpt_callback_info(repair_step, **kwargs)
                        logger.warning(f'Resume training after TREError from step {repair_step}.')
                    else:
                        _handle_exception_info(obj, uce_env, obj.tft, e)
                        ret = obj.tft.tft_wait_next_action()
                        if ret == obj.tft.Action.EXIT.value:
                            raise e
                        repair_step = obj.tft.tft_get_repair_step()
                        logger.warning(
                            "uce wrapper caught repair finish REPAIR STEP: {} batch_num:{}".format(repair_step,
                                                                                                   self.batch_num))
                    initial_epoch = int(repair_step / self.batch_num)
                    initial_step = repair_step % self.batch_num
                    kwargs["initial_epoch"] = initial_epoch
                    cb_initial_step = _calc_cb_initial_step(initial_epoch, initial_step, *args, **kwargs)
                    if not self.enable_tre:
                        kwargs["initial_step"] = cb_initial_step
                        self._initial_step = 0
                    # reset all accu grads to zero
                    obj._reset_acc_grads()
                    logger.warning(
                        "uce wrapper repair complete initial_epoch: {}, cb_initial_step: {} ".format(initial_epoch,
                                                                                                     cb_initial_step))
                    continue
                except BaseException as e:
                    if obj.tft:
                        logger.error("uce wrapper caught BaseException error, enter MindIO TTP process.", exc_info=True)
                        obj.tft.tft_report_error(obj.tft.ReportState.RS_UNKNOWN.value)
                    raise e
        else:
            return func(self, *args, **kwargs)

    return wrapper


def _check_tft():
    """Check if TFT is supported"""
    tft_env = os.getenv("MS_ENABLE_TFT")
    device_target = context.get_context("device_target")
    if tft_env and device_target == "Ascend":
        from mindspore._c_expression import MSContext
        ascend_target = MSContext.get_instance().get_ascend_soc_version()
        if ascend_target == 'ascend910':
            raise ValueError("TFT is not supported when using ascend910")
        jit_level = context.get_context("jit_level")
        if jit_level == "O2" and ("UCE:1" in tft_env or "ARF:1" in tft_env):
            raise ValueError("TFT is not supported when using jit_level == O2")


def _append_ccae(callbacks):
    """Add cluster monitoring when CCAE is enabled."""
    perf_config = os.getenv("PERF_DUMP_CONFIG")
    if perf_config is None:
        return callbacks
    pairs = perf_config.split(',')
    perf_config_dict = {}
    for pair in pairs:
        key, value = pair.split(':')
        if value.lower() == 'true':
            perf_config_dict[key] = True
        elif value.lower() == 'false':
            perf_config_dict[key] = False
        elif value.isdigit():
            perf_config_dict[key] = int(value)
        else:
            perf_config_dict[key] = value
    if perf_config_dict.get("enable", False):
        if callbacks is None:
            callbacks = ClusterMonitor()
        elif isinstance(callbacks, list):
            callbacks.append(ClusterMonitor())
        else:
            callbacks = [callbacks, ClusterMonitor()]
    return callbacks


def _get_arg_infos(inputs):
    """Get compile argument information from inputs.

    Args:
        inputs (Union[list, tuple, dict]): Argument got from cell which is set by `set_inputs`.

    Raises:
        RuntimeError: inputs is not a list, tuple or dict.
        RuntimeError: inputs is a dict without necessary keys and values.

    Returns:
        _type_: _description_
    """
    if isinstance(inputs, (list, tuple)):
        arg_specified = [[idx, arg] for idx, arg in enumerate(inputs)]
        arg_len = len(inputs)
    elif isinstance(inputs, dict):
        arg_specified = inputs.get(ARG_SPECIFIED, None)
        arg_len = inputs.get(TOTAL_ARG_LEN, None)
        if arg_specified is None or arg_len is None:
            raise RuntimeError(
                "The incremental inputs should be processed(with \"%s\" and \"%s\"), but got %s." %
                (ARG_SPECIFIED, TOTAL_ARG_LEN, str(inputs)))
    else:
        raise RuntimeError("inputs should be a list/tuple or a dict, but got %s!" % str(inputs))

    return arg_len, arg_specified


def _merge_inputs(inputs1, inputs2):
    """Merge two processed inputs to a new inputs for latter setting cell's inputs."""
    is_fullmode1 = isinstance(inputs1, (list, tuple))
    is_fullmode2 = isinstance(inputs2, (list, tuple))

    if is_fullmode1 and is_fullmode2:
        return [*inputs1, *inputs2]

    arg_len1, arg_specified1 = _get_arg_infos(inputs1)
    arg_len2, arg_specified2 = _get_arg_infos(inputs2)

    res_arg_len = arg_len1 + arg_len2
    res_arg_specified = []
    res_arg_specified.extend(arg_specified1)
    # The second inputs should add offset before merging.
    for idx, arg in arg_specified2:
        res_arg_specified.append([idx + arg_len1, arg])

    return {ARG_SPECIFIED: res_arg_specified, TOTAL_ARG_LEN: res_arg_len}


def _process_loss_inputs(loss_inputs):
    """Process loss's inputs whose first input should be dropped for train or eval.

    Args:
        loss_inputs (Union[list, tuple, dict]): Arguments save by `set_inputs` or `jit`.

    Raises:
        RuntimeError: inputs is not a list, tuple or dict.
        RuntimeError: inputs is a dict without necessary keys and values.

    Returns:
        list, tuple or dict: Arguments for latter setting.
    """
    # For train or eval, the first input of loss is the inner-tensor, so drop it.
    res = None
    if isinstance(loss_inputs, (list, tuple)):
        res = [*loss_inputs]
        res.pop(0)
    elif isinstance(loss_inputs, dict):
        loss_arg_specified = loss_inputs.get(ARG_SPECIFIED, None)
        loss_arg_len = loss_inputs.get(TOTAL_ARG_LEN, None)
        if loss_arg_specified is None or loss_arg_len is None:
            raise RuntimeError(
                "The loss incremental inputs should be processed(with \"%s\" and \"%s\"), but got %s." %
                (ARG_SPECIFIED, TOTAL_ARG_LEN, str(loss_inputs)))
        res_loss_arg_specified = []
        for idx, arg in loss_arg_specified:
            if idx == 0:
                continue
            res_loss_arg_specified.append([idx, arg])
        res = {ARG_SPECIFIED: res_loss_arg_specified, TOTAL_ARG_LEN: loss_arg_len - 1}
    else:
        raise RuntimeError("loss_inputs should be a list/tuple or a dict, but got %s!" % str(loss_inputs))

    return res


def _set_with_processed_inputs(network, inputs):
    """Save set inputs for computation graph with processed inputs.

    Args:
        network (nn.Cell): Target cell.
        inputs (Union[list, tuple, dict]): Inputs argument got from other cell.

    Raises:
        RuntimeError: network is not a nn.Cell.
        RuntimeError: inputs is not a list, tuple or dict.
    """
    Validator.check_value_type('network', network, nn.Cell)
    if isinstance(inputs, (list, tuple)):
        network.set_inputs(*inputs)
    elif isinstance(inputs, dict):
        network.set_inputs(**inputs)
    else:
        raise RuntimeError(
            "Reset inputs from a process inputs, should be a list/tuple or a dict, but got %s!" % str(inputs))


def _check_tft_reset_dataset():
    env_tft = os.getenv("MS_ENABLE_TFT", "")
    return any([v in env_tft for v in ["TRE:1", "UCE:1", "HCCE:1", "ARF:1"]])


class Model:
    """
    High-Level API for training or inference.

    `Model` groups layers into an object with training and inference features based on the arguments.

    Note:
        - If use mixed precision functions, need to set parameter `optimizer` at the same time,
          otherwise mixed precision functions do not take effect.
          When uses mixed precision functions, `global_step` in optimizer may be different from `cur_step_num`
          in Model.
        - After using `custom_mixed_precision` or `auto_mixed_precision` for precision conversion, it is not supported
          to perform the precision conversion again. If  `Model` is used to train a converted network, `amp_level`
          need to be configured to ``O0`` to avoid the duplicated accuracy conversion.

    Args:
        network (Cell): A training or testing network.
        loss_fn (Cell): Objective function. If `loss_fn` is None, the `network` should contain the calculation of loss.
                        Default: ``None`` .
        optimizer (Cell): Optimizer for updating the weights. If `optimizer` is None, the `network` needs to
                          do backpropagation and update weights. Default: ``None`` .
        metrics (Union[dict, set]): A Dictionary or a set of metrics for model evaluation.
                                    eg: {'accuracy', 'recall'}. Default: ``None`` .
        eval_network (Cell): Network for evaluation. If not defined, `network` and `loss_fn` would be wrapped as
                             `eval_network` . Default: ``None`` .
        eval_indexes (list): It is used when eval_network is defined. If `eval_indexes` is None by default, all outputs
                             of the `eval_network` would be passed to metrics. If `eval_indexes` is set, it must contain
                             three elements: the positions of loss value, predicted value and label in outputs of the
                             `eval_network`. In this case, the loss value will be passed to the `Loss` metric, the
                             predicted value and label will be passed to other metrics.
                             :func:`mindspore.train.Metric.set_indexes` is recommended instead of `eval_indexes`.
                             Default: ``None`` .
        amp_level (str): Option for argument `level` in :func:`mindspore.amp.build_train_network`, level for mixed
            precision training. Supports ["O0", "O1", "O2", "O3", "auto"]. Default: ``"O0"`` .

            For details on `amp_level` , refer to :func:`mindspore.amp.auto_mixed_precision`.

            The BatchNorm strategy can be changed by `keep_batchnorm_fp32` settings in `kwargs`. `keep_batchnorm_fp32`
            must be a bool. The loss scale strategy can be changed by `loss_scale_manager` setting in `kwargs`.
            `loss_scale_manager` should be a subclass of :class:`mindspore.amp.LossScaleManager`.

        boost_level (str): Option for argument `level` in `mindspore.boost`, level for boost mode
            training. Supports ["O0", "O1", "O2"]. Default: ``"O0"`` .

            - "O0": Do not change.
            - "O1": Enable the boost mode, the performance is improved by about 20%, and
              the accuracy is the same as the original accuracy.
            - "O2": Enable the boost mode, the performance is improved by about 30%, and
              the accuracy is reduced by less than 3%.

            If you want to config boost mode by yourself, you can set boost_config_dict as `boost.py`.
            In order for this function to work, you need to set the parameter `optimizer`, along with
            at least one of the parameter `eval_network` or performance `metrics`.

            Notice: The current optimization enabled by default only applies to some networks, and not all networks
            can obtain the same benefits.  It is recommended to enable this function on
            the Graph mode + Ascend platform, and for better acceleration,
            refer to :class:`mindspore.boost.AutoBoost` to configure
            boost_config_dict.

    Examples:
        >>> from mindspore import nn
        >>> from mindspore.train import Model
        >>>
        >>> # Define the network structure of LeNet5. Refer to
        >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
        >>> net = LeNet5()
        >>> loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True)
        >>> optim = nn.Momentum(params=net.trainable_params(), learning_rate=0.1, momentum=0.9)
        >>> model = Model(net, loss_fn=loss, optimizer=optim, metrics=None)
        >>> model.train_network
        >>> model.predict_network
        >>> model.eval_network
        >>> # Create the dataset taking MNIST as an example. Refer to
        >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/mnist.py
        >>> dataset = create_dataset()
        >>> model.train(2, dataset)
    """

    def __init__(self, network, loss_fn=None, optimizer=None, metrics=None, eval_network=None, eval_indexes=None,
                 amp_level="O0", boost_level="O0", **kwargs):
        self._network = network
        _init_auto_parallel_context(self._network)
        self._loss_fn = loss_fn
        self._optimizer = optimizer
        self._loss_scale_manager = None
        self._loss_scale_manager_set = False
        self._keep_bn_fp32 = None
        self._check_kwargs(kwargs)
        self._amp_level = amp_level
        self._boost_level = boost_level
        self._eval_network = eval_network
        self._process_amp_args(kwargs)
        self._parallel_mode = _get_parallel_mode()
        self._device_number = _get_device_num()
        self._parameter_broadcast = _get_parameter_broadcast()
        self._metrics = metrics

        self._check_amp_level_arg(optimizer, amp_level)
        self._check_for_graph_cell(kwargs)
        self._build_boost_network(kwargs)
        self._train_network = self._build_train_network()
        self._train_network._jit_config_dict = network.jit_config_dict
        self._build_eval_network(metrics, self._eval_network, eval_indexes)
        self._build_predict_network()
        self._current_epoch_num = 0
        self._current_step_num = 0
        self.epoch_iter = 0
        self.enable_recovery = False
        self._backbone_is_train = True
        self.need_load_ckpt = False
        self._lite_full_predictor = None
        self._lite_incremental_predictor = None
        self._mindspore_lite = None
        self._lite_infer = True  # if backend lite infer fails, set False
        self._mindspore_lite_model_group_id = id(self) & 0xFFFF
        self.batch_num = -1
        self.enable_tre = "TRE:1" in os.getenv("MS_ENABLE_TFT", "")
        self.enable_hcce = "HCCE:1" in os.getenv("MS_ENABLE_TFT", "")
        self._initial_step = None
        self._need_reset_data = _check_tft_reset_dataset()
        _clear_auto_parallel_context(self._network)

    def _check_for_graph_cell(self, kwargs):
        """Check for graph cell"""
        if not isinstance(self._network, nn.GraphCell):
            return
        if self._amp_level != "O0":
            logger.warning("amp_level will not work when network is a GraphCell.")

        if self._loss_fn is not None or self._optimizer is not None:
            raise ValueError("For 'Model', 'loss_fn' and 'optimizer' should be None when network is a GraphCell, "
                             "but got 'loss_fn': {}, 'optimizer': {}.".format(self._loss_fn, self._optimizer))
        if kwargs:
            raise ValueError("For 'Model', the '**kwargs' argument should be empty when network is a GraphCell.")

    def _process_amp_args(self, kwargs):
        if 'keep_batchnorm_fp32' in kwargs:
            self._keep_bn_fp32 = kwargs['keep_batchnorm_fp32']
        if 'loss_scale_manager' in kwargs:
            self._loss_scale_manager = kwargs['loss_scale_manager']
            self._loss_scale_manager_set = True

    def _check_amp_level_arg(self, optimizer, amp_level):
        """Check amp level arg"""
        if optimizer is None and amp_level != "O0":
            raise ValueError(
                "Auto mixed precision will not work because 'optimizer' is None.Please set amp_level='O0' "
                "to disable auto mixed precision or set 'optimizer' not be None to use auto mixed precision.")

    def _check_kwargs(self, kwargs):
        for arg in kwargs:
            if arg not in ['loss_scale_manager', 'keep_batchnorm_fp32', 'boost_config_dict', 'acc_level']:
                raise ValueError(f"The argument in 'kwargs' should be 'loss_scale_manager' or "
                                 f"'keep_batchnorm_fp32' or 'boost_config_dict' or 'acc_level', but got '{arg}'.")

    def _check_reuse_dataset(self, dataset):
        if not hasattr(dataset, '__model_hash__'):
            dataset.__model_hash__ = hash(self)
        if hasattr(dataset, '__model_hash__') and dataset.__model_hash__ != hash(self):
            raise RuntimeError("The dataset object had been used in other model by model.train(...), "
                               "please create a new dataset.")

    def _build_boost_network(self, kwargs):
        """Build the boost network."""
        boost_config_dict = ""
        if 'boost_config_dict' in kwargs:
            boost_config_dict = kwargs['boost_config_dict']
        if 'acc_level' in kwargs:
            self._boost_level = kwargs['acc_level']
            logger.warning("Next version acc_level will be removed, please replace with boost_level")
        processor = AutoBoost(self._boost_level, boost_config_dict)
        if processor.level not in ["O1", "O2"]:
            return
        if self._optimizer is None:
            logger.warning("In boost mode, the optimizer must be defined.")
            return
        if self._eval_network is None and self._metrics is None:
            logger.warning("In boost mode, the eval_network and metrics cannot be undefined at the same time.")
            return

        self._network, self._optimizer = processor.network_auto_process_train(self._network, self._optimizer)
        if self._eval_network is not None:
            self._eval_network = processor.network_auto_process_eval(self._eval_network)

    def _build_train_network(self):
        """Build train network"""
        network = self._network
        Validator.check_value_type('network', network, nn.Cell)
        if self._loss_scale_manager is not None and self._optimizer is None:
            raise ValueError("The argument 'optimizer' can not be None when set 'loss_scale_manager'.")

        net_inputs = network.get_inputs()
        if self._loss_fn:
            if self._loss_fn.get_inputs() and net_inputs:
                loss_inputs = _process_loss_inputs(self._loss_fn.get_inputs())
                net_inputs = _merge_inputs(net_inputs, loss_inputs)
        if self._optimizer:
            amp_config = {}
            if self._loss_scale_manager_set:
                amp_config['loss_scale_manager'] = self._loss_scale_manager
            if self._keep_bn_fp32 is not None:
                amp_config['keep_batchnorm_fp32'] = self._keep_bn_fp32
            network = amp.build_train_network(network,
                                              self._optimizer,
                                              self._loss_fn,
                                              level=self._amp_level,
                                              boost_level=self._boost_level,
                                              **amp_config)
        elif self._loss_fn:
            network = nn.WithLossCell(network, self._loss_fn)
        # If need to check if loss_fn is not None, but optimizer is None

        if net_inputs is not None:
            _set_with_processed_inputs(network, net_inputs)
        return network

    def _build_eval_network(self, metrics, eval_network, eval_indexes):
        """Build the network for evaluation."""
        self._metric_fns = get_metrics(metrics)
        if not self._metric_fns:
            return

        if eval_network is not None:
            if eval_indexes is not None and not (isinstance(eval_indexes, list) and len(eval_indexes) == 3):
                raise ValueError("The argument 'eval_indexes' must be a list or None. If 'eval_indexes' is a list, "
                                 "length of it must be three. But got 'eval_indexes' {}".format(eval_indexes))

            self._eval_network = eval_network
            self._eval_indexes = eval_indexes
        else:
            if self._loss_fn is None:
                raise ValueError(f"If `metrics` is set, `eval_network` must not be None. Do not set `metrics` if you"
                                 f" don't want an evaluation.\n"
                                 f"If evaluation is required, you need to specify `eval_network`, which will be used in"
                                 f" the framework to evaluate the model.\n"
                                 f"For the simple scenarios with one data, one label and one logits, `eval_network` is"
                                 f" optional, and then you can set `eval_network` or `loss_fn`. For the latter case,"
                                 f" framework will automatically build an evaluation network with `network` and"
                                 f" `loss_fn`.")
            net_inputs = self._network.get_inputs()
            if self._loss_fn.get_inputs() and net_inputs:
                loss_inputs = _process_loss_inputs(self._loss_fn.get_inputs())
                net_inputs = _merge_inputs(net_inputs, loss_inputs)
            self._eval_network = nn.WithEvalCell(self._network, self._loss_fn, self._amp_level in ["O2", "O3", "auto"])
            if net_inputs is not None:
                _set_with_processed_inputs(self._eval_network, net_inputs)
            self._eval_indexes = [0, 1, 2]

    def _build_predict_network(self):
        """Build the network for prediction."""
        self._predict_network = self._network
        # Unlike the cases in build_train_network() and build_eval_network(), 'multi_subgraphs' is not set

    def _clear_metrics(self):
        """Clear metrics local values."""
        for metric in self._metric_fns.values():
            metric.clear()

    def _update_metrics(self, outputs):
        """Update metrics local values."""
        if isinstance(outputs, Tensor):
            outputs = (outputs,)
        if not isinstance(outputs, tuple):
            raise ValueError(f"The argument 'outputs' should be tuple, but got {type(outputs)}.")

        if self._eval_indexes is not None and len(outputs) < 3:
            raise ValueError("The length of 'outputs' must be >= 3, but got {}".format(len(outputs)))

        for metric in self._metric_fns.values():
            if self._eval_indexes is None:
                metric.update(*outputs)
            else:
                if isinstance(metric, Loss):
                    metric.update(outputs[self._eval_indexes[0]])
                else:
                    metric.update(outputs[self._eval_indexes[1]], outputs[self._eval_indexes[2]])

    def _get_metrics(self):
        """Get metrics local values."""
        metrics = dict()
        # There's no need for server to execute eval, just give fake metrics.
        for key, value in self._metric_fns.items():
            if not _is_role_pserver():
                metrics[key] = value.eval()
            else:
                metrics[key] = 1
        return metrics

    def _get_scaling_sens(self):
        """get the scaling sens"""
        scaling_sens = 1
        if self._loss_scale_manager is not None:
            scaling_sens = self._loss_scale_manager.get_loss_scale()
        if self._parallel_mode == ParallelMode.DATA_PARALLEL:
            scaling_sens /= self._device_number
        return scaling_sens

    def _exec_preprocess(self, is_train, dataset, dataset_sink_mode, sink_size=-1, epoch_num=1, dataset_helper=None):
        """Initializes dataset."""
        if is_train:
            network = self._train_network
            phase = 'train'
        else:
            network = self._eval_network
            phase = 'eval'

        if dataset_sink_mode and not is_train:
            dataset.__loop_size__ = 1

        if dataset_helper is None:
            vlog_print("1", "ME", __file__, sys._getframe().f_lineno, "Begin to create DatasetHelper.")
            logger.info("Begin to create DatasetHelper.")
            dataset_helper = DatasetHelper(dataset, dataset_sink_mode, sink_size, epoch_num)

        if dataset_sink_mode:
            vlog_print("1", "ME", __file__, sys._getframe().f_lineno, "Begin to connect network with dataset.")
            logger.info("Begin to connect network with dataset.")
            network = connect_network_with_dataset(network, dataset_helper)

        if (_get_recovery_context("enable_recovery") or self._need_reset_data) and is_train:
            _set_training_dataset(dataset_helper)

        network.set_train(is_train)
        network.phase = phase
        self._backbone_is_train = is_train

        return dataset_helper, network

    def _check_network_mode(self, network, is_train):
        """
        Change network mode if modes of backbone network and current network are not matching.
        """
        if self._backbone_is_train != is_train:
            network.set_train(is_train)
            self._backbone_is_train = is_train
        # Mode train and eval are the same net, network will be set_grad in _build_train_network.
        # But if mode just want to  do predict or eval, must set network set_grad False
        if not is_train:
            network.set_grad(False)
        return network

    def _check_need_ckpt(self, callbacks):
        """Check callback list contain ckpt"""
        need_ckpt = False
        save_ckpt_steps = 1
        last_triggered_step = 0
        for cb in callbacks:
            if isinstance(cb, ModelCheckpoint):
                need_ckpt = True
                cfg_size = cb._get_save_checkpoint_steps
                save_ckpt_steps = save_ckpt_steps if (cfg_size is None or cfg_size >= sys.maxsize) else cfg_size
                last_triggered_step = cb._get_last_trigger_step
                break
        return need_ckpt, save_ckpt_steps, last_triggered_step

    def _store_training_step_info(self, cb_params):
        """
        cache train step info
        :param cb_params: callback params
        :return: none
        """
        if os.environ.get("MS_ENABLE_CKPT_D2H_ASYNC") != "1":
            return
        if context.get_context("device_target") == "Ascend":
            cb_params.need_ckpt, cb_params.save_checkpoint_steps, \
            cb_params.last_triggered_step = self._check_need_ckpt(cb_params.list_callback)
            logger.info(f"need_ckpt:{cb_params.need_ckpt},"
                        f"save_checkpoint_steps:{cb_params.save_checkpoint_steps},"
                        f"cur_step_num:{cb_params.cur_step_num},"
                        f"last_triggered_step:{cb_params.last_triggered_step}")
            context.set_context(ascend_config={"need_ckpt": cb_params.need_ckpt,
                                               "save_checkpoint_steps": cb_params.save_checkpoint_steps,
                                               "cur_step_num": cb_params.cur_step_num,
                                               "last_triggered_step": cb_params.last_triggered_step})

    def _warmup_dataset(self, epoch, train_dataset, sink_size=-1):
        """
        Trigger dataset pipeline running before graph compiling.

        Args:
            epoch (int): Total number of iterations on the data.
            train_dataset (Dataset): A training dataset iterator. If `train_dataset` is defined, training graphs will be
                                     initialized. Default: ``None``.
            sink_size (int): Control the amount of data in each sink. Default: -1.
        """
        if sink_size == -1:
            epoch_num = epoch
        else:
            epoch_num = math.ceil(epoch * sink_size / train_dataset.get_dataset_size())
            train_dataset.__total_batch__ = epoch * sink_size
        dataset_helper = None
        dataset_helper, _ = self._exec_preprocess(is_train=True,
                                                  dataset=train_dataset,
                                                  dataset_sink_mode=True,
                                                  sink_size=sink_size,
                                                  epoch_num=epoch_num,
                                                  dataset_helper=dataset_helper)
        train_dataset._dataset_helper = dataset_helper
        train_dataset._warmup_epoch = epoch

    def _waiting_for_dataset_warmup_ready(self, train_dataset):
        """
        Wait for the dataset to warmup until there is a batch of data available for training on the device side.

        Args:
            train_dataset (Dataset): A training dataset iterator. If `train_dataset` is defined, training graphs will be
                                     initialized. Default: ``None``.
        """
        mbuf_size = train_dataset.__transfer_dataset__.get_mbuf_queue_size()
        while mbuf_size == 0:
            time.sleep(10)
            mbuf_size = train_dataset.__transfer_dataset__.get_mbuf_queue_size()
            if mbuf_size != 0:
                break
            logger.warning(f"Waiting for the dataset warmup, current device queue size: {mbuf_size}")

    def _init(self, train_dataset=None, valid_dataset=None, sink_size=-1, epoch=1, sink_mode=True):
        """
        Initialize compute graphs and data graphs with the sink mode.

        Note:
            Pre-init process only supports `GRAPH_MODE` and `Ascend` target currently.

        Args:
            train_dataset (Dataset): A training dataset iterator. If `train_dataset` is defined, training graphs will be
                                     initialized. Default: ``None``.
            valid_dataset (Dataset): A evaluating dataset iterator. If `valid_dataset` is defined, evaluation graphs
                                     will be initialized, and `metrics` in `Model` can not be None. Default: ``None``.
            sink_size (int): Control the amount of data in each sink. Default: -1.
            epoch (int): Total number of iterations on the data. Default: 1.
        """
        if context.get_context("device_target") != "Ascend":
            raise RuntimeError('Pre-init process only supports Ascend target currently.')

        if not train_dataset and not valid_dataset:
            raise ValueError("The argument 'train_dataset' and 'valid_dataset' can not both be None or empty.")

        vlog_print("1", "ME", __file__, sys._getframe().f_lineno, "Begin to check device number in model.build().")
        logger.info("Begin to check device number in model.build() procedure.")
        _device_number_check(self._parallel_mode, self._device_number)

        if train_dataset:
            if not isinstance(train_dataset, mindspore.dataset.Dataset):
                raise TypeError("The type of 'train_dataset' must be `Dataset`, "
                                "but got {}.".format(type(train_dataset)))
            vlog_print("1", "ME", __file__, sys._getframe().f_lineno,
                       "Begin to check parameter broadcast in model.build().")
            logger.info("Begin to check parameter broadcast in model.build() procedure.")
            _parameter_broadcast_check(self._parallel_mode, self._parameter_broadcast)
            if self._parameter_broadcast:
                self._train_network.set_broadcast_flag()

            vlog_print("1", "ME", __file__, sys._getframe().f_lineno, "Begin to exec preprocess in model.build().")
            logger.info("Begin to exec preprocess in model.build() procedure.")
            train_dataset.__no_send__ = True
            train_dataset_helper, train_network = self._exec_preprocess(is_train=True,
                                                                        dataset=train_dataset,
                                                                        dataset_sink_mode=sink_mode,
                                                                        sink_size=sink_size)
            vlog_print("1", "ME", __file__, sys._getframe().f_lineno, "Begin to warmup dataset in model.build().")
            if sink_mode:
                logger.info("Begin to warmup dataset in model.build() procedure.")
                self._warmup_dataset(epoch, train_dataset, sink_size)

                # Since dataset pipeline has been triggered, delete flag
                delattr(train_dataset, "__no_send__")

                # Waiting for the dataset warmup ready
                vlog_print("1", "ME", __file__, sys._getframe().f_lineno,
                           "Begin waiting for dataset warmup in model.build().")
                logger.info("Begin waiting for dataset warmup in model.build() procedure.")
                self._waiting_for_dataset_warmup_ready(train_dataset)
                vlog_print("1", "ME", __file__, sys._getframe().f_lineno,
                           "The dataset warmup was successful in model.build().")
                logger.info("The dataset warmup was successful in model.build() procedure.")

            if context.get_auto_parallel_context("pipeline_stages") > 1 and valid_dataset:
                train_network.add_flags_recursive(is_first_iteration=True)
            for inputs in train_dataset_helper:
                vlog_print("1", "ME", __file__, sys._getframe().f_lineno,
                           "Begin to compile train network in model.build().")
                logger.info("Begin to compile train network in model.build() procedure.")
                train_network.compile(*inputs)
                self._train_network.parameter_layout_dict = train_network.parameter_layout_dict
                train_dataset.reset()
                break

        if valid_dataset:
            if not isinstance(valid_dataset, mindspore.dataset.Dataset):
                raise TypeError("The type of 'valid_dataset' must be `Dataset`, "
                                "but got {}.".format(type(valid_dataset)))
            if not self._metric_fns:
                raise RuntimeError("If define `valid_dataset`, metric fn can not be None or empty, "
                                   "you should set the argument 'metrics' for model.")

            valid_dataset.__no_send__ = True
            valid_dataset_helper, eval_network = self._exec_preprocess(is_train=False,
                                                                       dataset=valid_dataset,
                                                                       dataset_sink_mode=sink_mode)
            if context.get_auto_parallel_context("pipeline_stages") > 1:
                eval_network.add_flags_recursive(is_first_iteration=False)
            for inputs in valid_dataset_helper:
                vlog_print("1", "ME", __file__, sys._getframe().f_lineno,
                           "Begin to compile eval network in model.build().")
                logger.info("Begin to compile eval network in model.build() procedure.")
                eval_network.compile(*inputs)
                valid_dataset.reset()
                break

    @staticmethod
    def _transform_callbacks(callbacks):
        """Transform callback to a list."""
        if callbacks is None:
            return []

        if isinstance(callbacks, Iterable):
            return list(callbacks)

        return [callbacks]

    @_handle_tft
    @_save_final_ckpt
    def _train(self, epoch, train_dataset, callbacks=None, dataset_sink_mode=True, sink_size=-1, initial_epoch=0,
               valid_dataset=None, valid_frequency=1, valid_dataset_sink_mode=True, initial_step=0):
        """
        Training.

        Args:
            epoch (int): Total number of iterations on the data.
            train_dataset (Dataset): A training dataset iterator. If there is no
                                     loss_fn, a tuple with multiple data (data1, data2, data3, ...) will be
                                     returned and passed to the network. Otherwise, a tuple (data, label) will
                                     be returned. The data and label would be passed to the network and loss
                                     function respectively.
            callbacks (list): List of callback objects which should be executed while training. Default: ``None``.
            dataset_sink_mode (bool): Determine whether the data should be passed through the dataset channel.
                                      Default: ``True``.
                                      Configure pynative mode or CPU, the training process will be performed with
                                      dataset not sink.
            sink_size (int): Control the amount of data in each sink. Default: -1.
            initial_epoch (int): Epoch at which to start train, it used for resuming a previous training run.
                                 Default: 0.
        """
        if self._parameter_broadcast:
            self._train_network.set_broadcast_flag()

        cb_params = _InternalCallbackParam()
        cb_params.cur_step_num = initial_step
        cb_params.train_network = self._train_network
        cb_params.epoch_num = epoch - initial_epoch
        if dataset_sink_mode and sink_size > 0:
            cb_params.batch_num = sink_size
        else:
            cb_params.batch_num = train_dataset.get_dataset_size()
        self.batch_num = cb_params.batch_num
        cb_params.mode = "train"
        cb_params.loss_fn = self._loss_fn
        cb_params.optimizer = self._optimizer
        cb_params.parallel_mode = self._parallel_mode
        cb_params.device_number = self._device_number
        cb_params.train_dataset = train_dataset
        cb_params.list_callback = self._transform_callbacks(callbacks)
        valid_infos = (valid_dataset, valid_frequency, valid_dataset_sink_mode)
        cb_params.list_callback.insert(0, _FrameworkProfilerCallback())
        if context.get_context("mode") == context.PYNATIVE_MODE:
            cb_params.list_callback.insert(0, _StepSync())
        callbacks = cb_params.list_callback
        cb_params.train_dataset_element = None
        cb_params.network = self._network
        # Embedding cache server only run one step.
        if _is_role_pserver() and _cache_enable():
            epoch = 1
        cb_params.last_save_ckpt_step = None
        cb_params.latest_ckpt_file = None
        cb_params.loss_scale_mananger = self._loss_scale_manager
        cb_params.is_arf = _get_recovery_context("is_arf")
        cb_params.initial_step = self._initial_step

        # build callback list
        with _CallbackManager(callbacks) as list_callback:
            self._check_reuse_dataset(train_dataset)
            if not dataset_sink_mode:
                self._train_process(epoch, train_dataset, list_callback, cb_params, initial_epoch,
                                    valid_infos)
            elif context.get_context("device_target") == "CPU":
                logger.info("The CPU cannot support dataset sink mode currently."
                            "So the training process will be performed with dataset not sink.")
                self._train_process(epoch, train_dataset, list_callback, cb_params, initial_epoch,
                                    valid_infos)
            else:
                self._train_dataset_sink_process(epoch, train_dataset, list_callback,
                                                 cb_params, sink_size, initial_epoch, valid_infos)

    @staticmethod
    def _should_eval(epoch, validation_freq):
        return epoch % validation_freq == 0 if isinstance(validation_freq, int) else epoch in validation_freq

    def _train_dataset_sink_process(self, epoch, train_dataset, list_callback=None, cb_params=None,
                                    sink_size=-1, initial_epoch=0, valid_infos=None):
        """
        Training process. The data would be passed to network through dataset channel.

        Args:
            epoch (int): Total number of iterations on the data.
            train_dataset (Dataset): A training dataset iterator. If there is no
                                     loss_fn, a tuple with multiple data (data1, data2, data3, ...) should be
                                     returned and passed to the network. Otherwise, a tuple (data, label) should
                                     be returned. The data and label would be passed to the network and loss
                                     function respectively.
            list_callback (Callback): Executor of callback list. Default: ``None``.
            cb_params (_InternalCallbackParam): Callback parameters. Default: ``None``.
            sink_size (int): Control the amount of data in each sink. Default: -1.
            initial_epoch (int): Epoch at which to start train, it used for resuming a previous training run.
                                 Default: 0.
        """
        is_graph = context.get_context("mode") == context.GRAPH_MODE
        dataset_size = train_dataset.get_dataset_size()
        if dataset_size % sink_size != 0:
            logger.info("In dataset_sink mode (dataset_size % sink_size) should equal to 0, "
                        "it is suggested to pad/drop data or adjust sink_size. "
                        "But got 'dataset_size': {}, 'sink_size': {}.".format(dataset_size, sink_size))
        if sink_size == -1:
            dataset_sink_num = epoch
        else:
            dataset_sink_num = math.ceil(epoch * sink_size / dataset_size)
            train_dataset.__total_batch__ = epoch * sink_size

        cb_params.sink_size = sink_size
        cb_params.dataset_sink_mode = True
        run_context = RunContext(cb_params)
        list_callback.on_train_begin(run_context)
        # used to stop training for early stop, such as stopAtTIme or stopATStep
        dataset_helper = None
        if hasattr(train_dataset, '_dataset_helper'):
            dataset_helper = train_dataset._dataset_helper

        self.epoch_iter = 0
        self._check_enable_recovery()
        # Used to check whether need perform recovery for process which is restarted.
        self._check_need_load_ckpt(cb_params, dataset_size, sink_size)
        # Check whether this process is embedding cache server.
        is_embedding_cache_server = _is_role_pserver() and _cache_enable()

        while self.epoch_iter < (epoch - initial_epoch):
            cb_params.cur_epoch_num = self.epoch_iter + 1 + initial_epoch
            self._current_epoch_num = cb_params.cur_epoch_num
            self._current_step_num = 0
            list_callback.on_train_epoch_begin(run_context)
            dataset_helper, train_network = self._exec_preprocess(is_train=True,
                                                                  dataset=train_dataset,
                                                                  dataset_sink_mode=True,
                                                                  sink_size=sink_size,
                                                                  epoch_num=dataset_sink_num,
                                                                  dataset_helper=dataset_helper)

            cb_params.train_network = train_network
            cb_params.dataset_helper = dataset_helper

            # Perform recovery for process which is restarted.
            self._reset_training_step_for_abnormal_process(cb_params, dataset_helper)
            # Perform recovery for process which is not restarted.
            self._reset_training_step_for_normal_process(cb_params, dataset_helper)

            # For data sink dataset_helper only iter once, other wise iter epoch_size times.
            for inputs in dataset_helper:
                if is_graph:
                    cb_params.cur_step_num += dataset_helper.sink_size()
                else:
                    cb_params.cur_step_num += 1
                self._current_step_num = int((cb_params.cur_step_num - 1) % cb_params.batch_num + 1)
                self._store_training_step_info(cb_params)
                cb_params.train_dataset_element = inputs
                list_callback.on_train_step_begin(run_context)
                train_network = self._check_network_mode(train_network, True)
                outputs = train_network(*inputs)
                cb_params.net_outputs = outputs

                # In disaster recovery scenarios, need not to execute callbacks if this step executes failed.
                need_exec_callback_step_end = not (self.enable_recovery and _get_recovery_context("need_reset"))
                if need_exec_callback_step_end:
                    list_callback.on_train_step_end(run_context)
                if cb_params.is_arf:
                    cb_params.is_arf = False
                    _set_recovery_context(is_arf=False)
                _clean_rootinfo()

                # Embedding cache server only run one step.
                if is_embedding_cache_server:
                    break

            dataset_helper.continue_send()

            # When it's distributed training and using MindRT,
            # the node id should be reset to start from 0.
            # This is to avoid the timeout when finding the actor route tables in 'train' and 'eval' case(or 'fit').
            if _enable_distributed_mindrt():
                _reset_op_id_with_offset()

            self._eval_during_train(valid_infos, cb_params, list_callback)

            # In disaster recovery scenarios, need not to execute callbacks if this epoch executes failed.
            # Embedding cache server need not do epoch end callback, this process only run one step.
            need_exec_callback_epoch_end = not ((self.enable_recovery and _get_recovery_context("need_reset"))
                                                or is_embedding_cache_server)

            if need_exec_callback_epoch_end:
                list_callback.on_train_epoch_end(run_context)
            if "metrics" in cb_params or "eval_results" in cb_params:
                cb_params.pop("metrics", None)
                cb_params.pop("eval_results", None)

            should_stop = run_context.get_stop_requested()
            if should_stop:
                break

            need_reset_to_beginning = self.enable_recovery and _get_recovery_context("need_reset") \
                                      and not _get_recovery_context("latest_ckpt_file")
            self.epoch_iter += 1
            if need_reset_to_beginning:
                self.epoch_iter = 0
                cb_params.cur_step_num = 0

        dataset_helper.stop_send()
        dataset_helper.release()

        list_callback.on_train_end(run_context)

    def _eval_during_train(self, valid_infos, cb_params, list_callback):
        """Exec eval during train process."""
        valid_dataset, valid_frequency, valid_dataset_sink_mode = valid_infos
        if valid_dataset and self._should_eval(cb_params.cur_epoch_num, valid_frequency):
            train_cur_step_num = cb_params.cur_step_num
            train_batch_num = cb_params.batch_num
            train_dataset_sink_mode = cb_params.dataset_sink_mode
            train_net_outputs = cb_params.net_outputs

            eval_callback = []
            for cb in list_callback._callbacks:
                if cb.__class__.__name__ in internal_cb_names:
                    if isinstance(cb, TimeMonitor):
                        eval_callback.append(cb)
                else:
                    eval_callback.append(cb)

            self._eval_in_fit(valid_dataset,
                              callbacks=eval_callback,
                              dataset_sink_mode=valid_dataset_sink_mode,
                              cb_params=cb_params)
            cb_params.mode = "train"
            cb_params.cur_step_num = train_cur_step_num
            cb_params.batch_num = train_batch_num
            cb_params.dataset_sink_mode = train_dataset_sink_mode
            cb_params.net_outputs = train_net_outputs

    def _check_enable_recovery(self):
        """
        Check whether enable recovery and execution mode consistency.
        """

        enable_recovery = _get_recovery_context("enable_recovery") and context.get_context("device_target") == "GPU"
        if not enable_recovery:
            self.enable_recovery = False
        else:
            self.enable_recovery = enable_recovery and _is_role_worker()

    def _check_need_load_ckpt(self, cb_params, dataset_size, sink_size=-1):
        """
        Check whether need to load checkpoint after abnormal process restart.

        Args:
            cb_params (_InternalCallbackParam): Callback parameters.
            dataset_size (int): The number of batches in a dataset.
            sink_size (int): Control the amount of data in each sink. Default: -1.
        """
        if context.get_context("device_target") != "GPU":
            return
        if not self.enable_recovery:
            self.need_load_ckpt = False

        cb_params.latest_ckpt_file = _get_recovery_context("latest_ckpt_file")
        if cb_params.latest_ckpt_file:
            recovery_epoch_num = _get_recovery_context("latest_ckpt_epoch")
            recovery_step_num = _get_recovery_context("latest_ckpt_step")
            dataset_sink_size = sink_size if sink_size > 0 else dataset_size
            cb_params.cur_step_num = (recovery_epoch_num - 1) * dataset_sink_size + recovery_step_num
            cb_params.last_save_ckpt_step = cb_params.cur_step_num
            self.epoch_iter = recovery_epoch_num
            self.need_load_ckpt = True
        else:
            self.need_load_ckpt = False

    def _reset_training_step_for_abnormal_process(self, cb_params, dataset_helper):
        """
        Execute recovery for abnormal exit process when restart.

        Args:
            cb_params (_InternalCallbackParam): Callback parameters.
        """

        if self.need_load_ckpt:
            try:
                load_checkpoint(cb_params.latest_ckpt_file, cb_params.train_network)
            except BaseException as e:
                os.remove(cb_params.latest_ckpt_file)
                raise RuntimeError(e.__str__() + ", load ckpt failed and remove the ckpt: " \
                                   + cb_params.latest_ckpt_file) from e
            _reset_training_dataset(cb_params.cur_step_num, dataset_helper.iter.dataset.get_dataset_size())
            self.need_load_ckpt = False

    def _reset_training_step_for_normal_process(self, cb_params, dataset_helper):
        """
        Execute recovery for normal process when there is process exit abnormally.

        Args:
            cb_params (_InternalCallbackParam): Callback parameters.
            dataset_helper (DatasetHelper): A class to process the MindData dataset,
                it provides the type, shape and queue name of the dataset to wrap the `GetNext`.
        """

        if self.enable_recovery and _get_recovery_context("need_reset"):
            cb_params.latest_ckpt_file = _get_recovery_context("latest_ckpt_file")
            if cb_params.latest_ckpt_file:
                try:
                    load_checkpoint(cb_params.latest_ckpt_file, cb_params.train_network)
                except BaseException as e:
                    os.remove(cb_params.latest_ckpt_file)
                    raise RuntimeError(e.__str__() + ", load ckpt failed and remove the ckpt: "\
                         + cb_params.latest_ckpt_file) from e

                recovery_epoch_num = _get_recovery_context("latest_ckpt_epoch")
                recovery_step_num = _get_recovery_context("latest_ckpt_step")
                cb_params.cur_step_num = (recovery_epoch_num - 1) * dataset_helper.sink_size() + recovery_step_num
                self.epoch_iter = recovery_epoch_num
                cb_params.cur_epoch_num = self.epoch_iter + 1
                cb_params.last_save_ckpt_step = cb_params.cur_step_num
                _reset_training_dataset(cb_params.cur_step_num, dataset_helper.iter.dataset.get_dataset_size())
            else:
                _reset_training_dataset(0, dataset_helper.iter.dataset.get_dataset_size())

            _set_recovery_context(need_reset=False)

    def _train_process(self, epoch, train_dataset, list_callback=None, cb_params=None, initial_epoch=0,
                       valid_infos=None):
        """
        Training process. The data would be passed to network directly.

        Args:
            epoch (int): Total number of iterations on the data.
            train_dataset (Dataset): A training dataset iterator. If there is no
                                     loss_fn, a tuple with multiple data (data1, data2, data3, ...) should be
                                     returned and passed to the network. Otherwise, a tuple (data, label) should
                                     be returned. The data and label would be passed to the network and loss
                                     function respectively.
            list_callback (Callback): Executor of callback list. Default: ``None``.
            cb_params (_InternalCallbackParam): Callback parameters. Default: ``None``.
            initial_epoch (int): Epoch at which to start train, it used for resuming a previous training run.
                                 Default: 0.
        """
        dataset_helper, _ = self._exec_preprocess(is_train=True,
                                                  dataset=train_dataset,
                                                  dataset_sink_mode=False,
                                                  epoch_num=epoch)
        cb_params.dataset_sink_mode = False
        run_context = RunContext(cb_params)
        list_callback.on_train_begin(run_context)
        is_embedding_cache_server = _is_role_pserver() and _cache_enable()

        for i in range(initial_epoch, epoch):
            cb_params.cur_epoch_num = i + 1
            self._current_epoch_num = cb_params.cur_epoch_num
            self._current_step_num = 0

            list_callback.on_train_epoch_begin(run_context)

            for next_element in dataset_helper:
                len_element = len(next_element)
                next_element = _transfer_tensor_to_tuple(next_element)
                if self._loss_fn and len_element != 2:
                    raise ValueError("When 'loss_fn' is not None, 'train_dataset' should return "
                                     "two elements, but got {}, please check the number of elements "
                                     "returned by 'train_dataset'".format(len_element))
                cb_params.cur_step_num += 1
                self._current_step_num = int((cb_params.cur_step_num - 1) % cb_params.batch_num + 1)
                cb_params.train_dataset_element = next_element
                list_callback.on_train_step_begin(run_context)
                self._check_network_mode(self._train_network, True)
                outputs = self._train_network(*next_element)
                cb_params.net_outputs = outputs
                if self._loss_scale_manager and self._loss_scale_manager.get_drop_overflow_update():
                    overflow = outputs[1]
                    overflow = np.all(overflow.asnumpy())
                    self._loss_scale_manager.update_loss_scale(overflow)

                list_callback.on_train_step_end(run_context)
                if cb_params.is_arf:
                    cb_params.is_arf = False
                    _set_recovery_context(is_arf=False)
                _clean_rootinfo()
                # Embedding cache server only run one step.
                if is_embedding_cache_server:
                    break
                should_stop = run_context.get_stop_requested()
                if should_stop:
                    break

            # When it's distributed training and using MindRT,
            # the node id should be reset to start from 0.
            # This is to avoid the timeout when finding the actor route tables in 'train' and 'eval' case(or 'fit').
            if _enable_distributed_mindrt():
                _reset_op_id_with_offset()

            self._eval_during_train(valid_infos, cb_params, list_callback)

            train_dataset.reset()

            # if param is cache enable, flush data from cache to host before epoch end
            self._flush_from_cache(cb_params)

            # Embedding cache server need not do epoch end callback, this process only run one step.
            if not is_embedding_cache_server:
                list_callback.on_train_epoch_end(run_context)
            if "metrics" in cb_params or "eval_results" in cb_params:
                cb_params.pop("metrics", None)
                cb_params.pop("eval_results", None)
            should_stop = run_context.get_stop_requested()
            if should_stop:
                break

        list_callback.on_train_end(run_context)

    def train(self, epoch, train_dataset, callbacks=None, dataset_sink_mode=False, sink_size=-1, initial_epoch=0):
        """
        Training API.

        When setting pynative mode or CPU, the training process will be performed with dataset not sink.

        Note:
            If dataset_sink_mode is True, data will be sent to device. If the device is Ascend, features
            of data will be transferred one by one. The limitation of data transmission per time is 256M.

            When dataset_sink_mode is True, the `step_end` method of the instance of Callback will be called at the end
            of step in PyNative mode, or will be called at the end of epoch in Graph mode.

            If dataset_sink_mode is True, dataset will be bound to this model and cannot be used by other models.

            If sink_size > 0, each epoch of the dataset can be traversed unlimited times until you get sink_size
            elements of the dataset. The next epoch continues to traverse from the end position of the previous
            traversal.

            The interface builds the computational graphs and then executes the computational graphs. However, when
            the `Model.build` is executed first, it only performs the graphs execution.

        Args:
            epoch (int): Total training epochs. Generally, train network will be trained on complete dataset per epoch.
                         If `dataset_sink_mode` is set to True and `sink_size` is greater than 0, each epoch will
                         train `sink_size` steps instead of total steps of dataset.
                         If `epoch` used with `initial_epoch`, it is to be understood as "final epoch".
            train_dataset (Dataset): A training dataset iterator. If `loss_fn` is defined, the data and label will be
                                     passed to the `network` and the `loss_fn` respectively, so a tuple (data, label)
                                     should be returned from dataset. If there is multiple data or labels, set `loss_fn`
                                     to None and implement calculation of loss in `network`,
                                     then a tuple (data1, data2, data3, ...) with all data returned from dataset will be
                                     passed to the `network`.
            callbacks (Optional[list[Callback], Callback]): List of callback objects or callback object,
                                                            which should be executed while training.
                                                            Default: ``None``.
            dataset_sink_mode (bool): Determines whether to pass the data through dataset channel.
                                      Configure pynative mode or CPU, the training process will be performed with
                                      dataset not sink. Default: ``False``.
            sink_size (int): Control the number of steps for each sinking.
                             `sink_size` is invalid if `dataset_sink_mode` is False.
                             If sink_size = -1, sink the complete dataset for each epoch.
                             If sink_size > 0, sink sink_size data for each epoch.
                             Default: -1.
            initial_epoch (int): Epoch at which to start train, it used for resuming a previous training run.
                                 Default: 0.

        Examples:
            >>> import mindspore as ms
            >>> from mindspore import nn
            >>> from mindspore.train import Model
            >>>
            >>> # Create the dataset taking MNIST as an example. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/mnist.py
            >>> dataset = create_dataset()
            >>> # Define the network structure of LeNet5. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
            >>> net = LeNet5()
            >>> loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True)
            >>> loss_scale_manager = ms.FixedLossScaleManager(1024., False)
            >>> optim = nn.Momentum(params=net.trainable_params(), learning_rate=0.1, momentum=0.9)
            >>> model = Model(net, loss_fn=loss, optimizer=optim, metrics=None,
            ...                  loss_scale_manager=loss_scale_manager)
            >>> model.train(2, dataset)
        """
        _init_auto_parallel_context(self._network)
        _check_tft()
        device_target = context.get_context("device_target")
        if _is_ps_mode() and not _cache_enable() and (device_target in ["Ascend", "CPU"]) and dataset_sink_mode:
            logger.info("For PS mode, reset datasink mode to False when using Ascend or CPU backend.")
            dataset_sink_mode = False

        Validator.check_bool(dataset_sink_mode)
        if isinstance(self._train_network, nn.GraphCell) and dataset_sink_mode:
            raise ValueError("Dataset sink mode is currently not supported when training with a GraphCell.")

        if hasattr(train_dataset, '_warmup_epoch') and train_dataset._warmup_epoch != epoch:
            raise ValueError("when use Model.build to initialize model, the value of parameter 'epoch' in Model.build "
                             "should be equal to value in Model.train, but got the value of epoch in build {} and "
                             "the value of epoch in train {} separately."
                             .format(train_dataset._warmup_epoch, epoch))

        # Parameter server and embedding cache mode check.
        if _is_ps_mode():
            if not dataset_sink_mode and _cache_enable():
                raise ValueError("Embedding cache mode should run with 'dataset_sink_mode=True'.")

        self._check_sink_mode_for_ds_debug_mode(dataset_sink_mode)

        Validator.check_is_int(sink_size)
        Validator.check_positive_int(epoch)
        Validator.check_non_negative_int(initial_epoch)
        if initial_epoch >= epoch:
            raise ValueError(f"For 'Model.train', the parameter 'epoch' must bigger than parameter 'initial_epoch',"
                             f" but got the parameter 'epoch' is {epoch}, 'initial_epoch' is {initial_epoch}.")

        dataset_size = train_dataset.get_dataset_size()
        if dataset_size == 0:
            raise ValueError("There is no valid data in dataset, please check dataset file firstly.")
        if sink_size == -1:
            sink_size = dataset_size
        if sink_size < -1 or sink_size == 0:
            raise ValueError("For 'Model.train', The argument 'sink_size' must be -1 or positive, "
                             "but got {}.".format(sink_size))

        _device_number_check(self._parallel_mode, self._device_number)

        callbacks = _append_ccae(callbacks)
        if callbacks:
            self._check_methods_for_custom_callbacks(callbacks, "train")
        self._train(epoch,
                    train_dataset,
                    callbacks=callbacks,
                    dataset_sink_mode=dataset_sink_mode,
                    sink_size=sink_size,
                    initial_epoch=initial_epoch)

        # When it's distributed training and using MindRT,
        # the node id should be reset to start from 0.
        # This is to avoid the timeout when finding the actor route tables in 'train' and 'eval' case(or 'fit').
        if _enable_distributed_mindrt():
            _reset_op_id_with_offset()

        _clear_auto_parallel_context(self._network)

    @staticmethod
    def _check_sink_mode_for_ds_debug_mode(dataset_sink_mode):
        if get_debug_mode() and dataset_sink_mode:
            raise ValueError("Dataset sink mode is not supported when dataset pipeline debug mode is on. "
                             "Please manually turn off sink mode.")

    @staticmethod
    def _check_methods_for_custom_callbacks(callbacks, current_mode):
        """
        Check whether methods of custimized callbacks are valid.

        Args:
            callbacks (Optional[list[Callback], Callback]): List of callback objects or callback object.
            current_mode (str): 'fit', 'train' or 'eval'.
        """
        old_version_methods_names = {'begin', 'end', 'epoch_begin', 'epoch_end', 'step_begin', 'step_end'}
        if not isinstance(callbacks, list):
            callbacks = [callbacks]
        for cb in callbacks:
            cb_name = cb.__class__.__name__
            if cb_name not in internal_cb_names:
                cb_methods_names = set(cb.__class__.__dict__.keys())
                invalid_methods_names = cb_methods_names & old_version_methods_names
                if invalid_methods_names:
                    if current_mode in ["train", "eval"]:
                        logger.warning("For %s callback, %s methods may not be supported in later version, "
                                       "Use methods prefixed with 'on_train' or 'on_eval' instead "
                                       "when using customized callbacks." % (cb_name, invalid_methods_names))
                    else:
                        raise ValueError("For %s callback, %s methods may not be supported in later version, "
                                         "Use methods prefixed with 'on_train' or 'on_eval' instead when "
                                         "using customized callbacks." % (cb_name, invalid_methods_names))

    def fit(self, epoch, train_dataset, valid_dataset=None, valid_frequency=1, callbacks=None,
            dataset_sink_mode=False, valid_dataset_sink_mode=False, sink_size=-1, initial_epoch=0):
        """
        Fit API.

        Evaluation process will be performed during training process if `valid_dataset` is provided.

        More details please refer to :func:`mindspore.train.Model.train` and
        :func:`mindspore.train.Model.eval`.

        Args:
            epoch (int): Total training epochs. Generally, train network will be trained on complete dataset per epoch.
                         If `dataset_sink_mode` is set to True and `sink_size` is greater than 0, each epoch will
                         train `sink_size` steps instead of total steps of dataset.
                         If `epoch` used with `initial_epoch`, it is to be understood as "final epoch".
            train_dataset (Dataset): A training dataset iterator. If `loss_fn` is defined, the data and label will be
                                     passed to the `network` and the `loss_fn` respectively, so a tuple (data, label)
                                     should be returned from dataset. If there is multiple data or labels, set `loss_fn`
                                     to None and implement calculation of loss in `network`,
                                     then a tuple (data1, data2, data3, ...) with all data returned from dataset
                                     will be passed to the `network`.
            valid_dataset (Dataset): Dataset to evaluate the model. If `valid_dataset` is provided, evaluation process
                                     will be performed on the end of training process. Default: ``None`` .
            valid_frequency (int, list): Only relevant if `valid_dataset` is provided.  If an integer, specifies
                         how many training epochs to run before a new validation run is performed,
                         e.g. `valid_frequency=2` runs validation every 2 epochs.
                         If a list, specifies the epochs on which to run validation,
                         e.g. `valid_frequency=[1, 5]` runs validation at the end of the 1st, 5th epochs.
                         Default: ``1`` .
            callbacks (Optional[list[Callback], Callback]): List of callback objects or callback object,
                                                            which should be executed while training.
                                                            Default: ``None`` .
            dataset_sink_mode (bool): Determines whether to pass the train data through dataset channel.
                                      Configure pynative mode or CPU, the training process will be performed with
                                      dataset not sink. Default: ``False`` .
            valid_dataset_sink_mode (bool): Determines whether to pass the validation data through dataset channel.
                                      Default: ``False`` .
            sink_size (int): Control the number of steps for each sinking.
                             `sink_size` is invalid if `dataset_sink_mode` is False.
                             If sink_size = -1, sink the complete dataset for each epoch.
                             If sink_size > 0, sink sink_size data for each epoch.
                             Default: ``-1`` .
            initial_epoch (int): Epoch at which to start train, it useful for resuming a previous training run.
                                 Default: ``0`` .

        Examples:
            >>> from mindspore import nn
            >>> from mindspore.train import Model
            >>>
            >>> # Create the dataset taking MNIST as an example. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/mnist.py
            >>> train_dataset = create_dataset("train")
            >>> valid_dataset = create_dataset("test")
            >>> # Define the network structure of LeNet5. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
            >>> net = LeNet5()
            >>> loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True)
            >>> optim = nn.Momentum(params=net.trainable_params(), learning_rate=0.1, momentum=0.9)
            >>> model = Model(net, loss_fn=loss, optimizer=optim, metrics={"accuracy"})
            >>> model.fit(2, train_dataset, valid_dataset)
        """
        _init_auto_parallel_context(self._network)
        device_target = context.get_context("device_target")
        if _is_ps_mode() and not _cache_enable() and (device_target in ["Ascend", "CPU"]) and dataset_sink_mode:
            logger.info("For PS mode, reset datasink mode to False when using Ascend or CPU backend.")
            dataset_sink_mode = False

        dataset_sink_mode = Validator.check_bool(dataset_sink_mode)
        valid_dataset_sink_mode = Validator.check_bool(valid_dataset_sink_mode)

        if isinstance(self._train_network, nn.GraphCell) and dataset_sink_mode:
            raise ValueError("Dataset sink mode is currently not supported when training with a GraphCell.")

        if hasattr(train_dataset, '_warmup_epoch') and train_dataset._warmup_epoch != epoch:
            raise ValueError("when use Model.build to initialize model, the value of parameter `epoch` in Model.build "
                             "should be equal to value in Model.fit, but got {} and {} separately."
                             .format(train_dataset._warmup_epoch, epoch))

        Validator.check_is_int(sink_size)
        Validator.check_positive_int(epoch)
        Validator.check_non_negative_int(initial_epoch)
        if initial_epoch >= epoch:
            raise ValueError(f"For 'Model.fit', the parameter 'epoch' must bigger than parameter 'initial_epoch',"
                             f" but got the parameter 'epoch' is {epoch}, 'initial_epoch' is {initial_epoch}.")
        dataset_size = train_dataset.get_dataset_size()
        if dataset_size == 0:
            raise ValueError("There is no valid data in dataset, please check dataset file firstly.")
        if sink_size == -1:
            sink_size = dataset_size
        if sink_size < -1 or sink_size == 0:
            raise ValueError("For 'Model.fit', The parameter 'sink_size' must be -1 or positive, "
                             "but got {}.".format(sink_size))

        _device_number_check(self._parallel_mode, self._device_number)

        if not isinstance(valid_frequency, (int, list)):
            raise TypeError(f"For 'Model.fit', the type of 'valid_frequency' must be a list or an integer, but got "
                            f"type {type(valid_frequency)}.")

        if valid_dataset and not self._metric_fns:
            raise ValueError("For 'Model.fit', if valid_dataset is not None, the model argument 'metrics' can not be"
                             "None or empty, you should set the argument 'metrics' for model.")
        if callbacks:
            self._check_methods_for_custom_callbacks(callbacks, "fit")
        self._train(epoch,
                    train_dataset,
                    callbacks=callbacks,
                    dataset_sink_mode=dataset_sink_mode,
                    sink_size=sink_size,
                    initial_epoch=initial_epoch,
                    valid_dataset=valid_dataset,
                    valid_frequency=valid_frequency,
                    valid_dataset_sink_mode=valid_dataset_sink_mode)
        _clear_auto_parallel_context(self._network)

    def build(self, train_dataset=None, valid_dataset=None, sink_size=-1, epoch=1, sink_mode=True):
        """
        Build computational graphs and data graphs with the sink mode.

        .. warning::
            This is an experimental API that is subject to change or deletion.

        Note:
            The interface builds the computational graphs, when the interface is executed first, 'Model.train' only
            performs the graphs execution. Pre-build process only supports `GRAPH_MODE` and `Ascend` target currently.
            It only supports dataset sink mode.

        Args:
            train_dataset (Dataset): A training dataset iterator. If `train_dataset` is defined, training graphs will be
                                     built. Default: ``None`` .
            valid_dataset (Dataset): An evaluating dataset iterator. If `valid_dataset` is defined, evaluation graphs
                                     will be built, and `metrics` in `Model` can not be None. Default: ``None`` .
            sink_size (int): Control the number of steps for each sinking. Default: ``-1`` .
            epoch (int): Control the training epochs. Default: ``1`` .
            sink_mode (bool): Determines whether to pass the data through dataset channel. Default: ``True`` .

        Examples:
            >>> from mindspore import nn
            >>> from mindspore.train import Model
            >>> from mindspore.amp import FixedLossScaleManager
            >>>
            >>> # Create the dataset taking MNIST as an example. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/mnist.py
            >>> dataset = create_dataset()
            >>> # Define the network structure of LeNet5. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
            >>> net = LeNet5()
            >>> loss = nn.SoftmaxCrossEntropyWithLogits()
            >>> loss_scale_manager = FixedLossScaleManager()
            >>> optim = nn.Momentum(params=net.trainable_params(), learning_rate=0.1, momentum=0.9)
            >>> model = Model(net, loss_fn=loss, optimizer=optim, metrics=None,
            ...                  loss_scale_manager=loss_scale_manager)
            >>> model.build(dataset, epoch=2)
            >>> model.train(2, dataset)
        """
        _init_auto_parallel_context(self._network)
        epoch = Validator.check_positive_int(epoch)
        if hasattr(self._train_network, '_is_check_and_refresh') and not self._train_network._is_check_and_refresh:
            self._train_network.check_names_and_refresh_name()
            self._train_network._is_check_and_refresh = True
        vlog_print("1", "ME", __file__, sys._getframe().f_lineno, "Begin to init dataset in model.build().")
        logger.info("Begin to init dataset in model.build() procedure.")
        self._init(train_dataset, valid_dataset, sink_size, epoch, sink_mode)
        vlog_print("1", "ME", __file__, sys._getframe().f_lineno,
                   "The model.build() which contains dataset warmup and network compile is success.")
        logger.info("The model.build() which contains dataset warmup and network compile is success.")
        _clear_auto_parallel_context(self._network)

    def _eval_in_fit(self, valid_dataset, callbacks=None, dataset_sink_mode=True, cb_params=None):
        """
        Evaluation process in :func:`mindspore.train.Model.fit`.

        Args:
            valid_dataset (Dataset): Dataset to evaluate the model. If `valid_dataset` is provided, evaluation process
                                     will be performed on the end of training process. Default: ``None``.
            callbacks (Optional[list[Callback], Callback]): List of callback objects or callback object, which should be
                                     executed while evaluation. Default: ``None``.
            valid_dataset_sink_mode (bool): Determines whether to pass the validation data through dataset channel.
                                     Default: ``True``.
            cb_params (_InternalCallbackParam): Callback parameters. Default: ``None``.
        """
        if isinstance(self._eval_network, nn.GraphCell) and dataset_sink_mode:
            raise ValueError("Sink mode is currently not supported when evaluating with a GraphCell.")

        cb_params.eval_network = self._eval_network
        cb_params.valid_dataset = valid_dataset
        cb_params.batch_num = valid_dataset.get_dataset_size()
        cb_params.mode = "eval"
        cb_params.cur_step_num = 0

        self._clear_metrics()

        if context.get_context("device_target") == "CPU" and dataset_sink_mode:
            dataset_sink_mode = False
            logger.info("CPU cannot support dataset sink mode currently."
                        "So the evaluating process will be performed with dataset non-sink mode.")

        with _CallbackManager(callbacks) as list_callback:
            if dataset_sink_mode:
                return self._eval_dataset_sink_process(valid_dataset, list_callback, cb_params, add_eval_loss=True)
            return self._eval_process(valid_dataset, list_callback, cb_params, add_eval_loss=True)

    def _eval_dataset_sink_process(self, valid_dataset, list_callback=None, cb_params=None, add_eval_loss=False):
        """
        Evaluation. The data would be passed to network through dataset channel.

        Args:
            valid_dataset (Dataset): Dataset to evaluate the model.
            list_callback (Callback): Executor of callback list. Default: ``None``.
            cb_params (_InternalCallbackParam): Callback parameters. Default: ``None``.

        Returns:
            Dict, which returns the loss value and metrics values for the model in the test mode.
        """
        run_context = RunContext(cb_params)

        dataset_helper, eval_network = self._exec_preprocess(is_train=False,
                                                             dataset=valid_dataset,
                                                             dataset_sink_mode=True)
        cb_params.eval_network = eval_network
        cb_params.dataset_sink_mode = True
        list_callback.on_eval_begin(run_context)
        list_callback.on_eval_epoch_begin(run_context)
        for inputs in dataset_helper:
            cb_params.cur_step_num += 1
            inputs = _transfer_tensor_to_tuple(inputs)
            cb_params.eval_dataset_element = inputs
            list_callback.on_eval_step_begin(run_context)
            eval_network = self._check_network_mode(eval_network, False)
            outputs = eval_network(*inputs)
            cb_params.net_outputs = outputs
            list_callback.on_eval_step_end(run_context)
            self._update_metrics(outputs)
            if add_eval_loss:
                eval_loss_fn = get_metric_fn("loss")
                eval_loss_fn.update(outputs[self._eval_indexes[0]])

        list_callback.on_eval_epoch_end(run_context)
        metrics = self._get_metrics()
        cb_params.metrics = metrics
        if add_eval_loss:
            eval_loss = eval_loss_fn.eval()
            cb_params.eval_results = copy.deepcopy(metrics)
            cb_params.eval_results.update({"eval_loss": eval_loss})
        list_callback.on_eval_end(run_context)

        dataset_helper.stop_send()
        dataset_helper.release()

        return metrics

    def _eval_process(self, valid_dataset, list_callback=None, cb_params=None, add_eval_loss=False):
        """
        Evaluation. The data would be passed to network directly.

        Args:
            valid_dataset (Dataset): Dataset to evaluate the model.
            list_callback (Callback): Executor of callback list. Default: ``None``.
            cb_params (_InternalCallbackParam): Callback parameters. Default: ``None``.

        Returns:
            Dict, which returns the loss value and metrics values for the model in the test mode.
        """
        run_context = RunContext(cb_params)
        cb_params.dataset_sink_mode = False
        list_callback.on_eval_begin(run_context)
        dataset_helper, _ = self._exec_preprocess(is_train=False,
                                                  dataset=valid_dataset,
                                                  dataset_sink_mode=False)
        list_callback.on_eval_epoch_begin(run_context)
        for next_element in dataset_helper:
            cb_params.cur_step_num += 1
            next_element = _transfer_tensor_to_tuple(next_element)
            cb_params.eval_dataset_element = next_element
            list_callback.on_eval_step_begin(run_context)
            self._check_network_mode(self._eval_network, False)
            outputs = self._eval_network(*next_element)
            cb_params.net_outputs = outputs
            list_callback.on_eval_step_end(run_context)
            self._update_metrics(outputs)
            if add_eval_loss:
                eval_loss_fn = get_metric_fn("loss")
                eval_loss_fn.update(outputs[self._eval_indexes[0]])
            if run_context.get_stop_requested():
                break

        list_callback.on_eval_epoch_end(run_context)
        valid_dataset.reset()
        metrics = self._get_metrics()
        cb_params.metrics = metrics
        if add_eval_loss:
            eval_loss = eval_loss_fn.eval()
            cb_params.eval_results = copy.deepcopy(metrics)
            cb_params.eval_results.update({"eval_loss": eval_loss})
        list_callback.on_eval_end(run_context)
        return metrics

    def eval(self, valid_dataset, callbacks=None, dataset_sink_mode=False):
        """
        Evaluation API.

        Configure to pynative mode or CPU, the evaluating process will be performed with dataset non-sink mode.

        Note:
            If dataset_sink_mode is True, data will be sent to device. At this point, the dataset will be bound to this
            model, so the dataset cannot be used by other models. If the device is Ascend, features
            of data will be transferred one by one. The limitation of data transmission per time is 256M.

            The interface builds the computational graphs and then executes the computational graphs. However, when
            the `Model.build` is executed first, it only performs the graphs execution.

        Args:
            valid_dataset (Dataset): Dataset to evaluate the model.
            callbacks (Optional[list(Callback), Callback]): List of callback objects or callback object,
                                                            which should be executed while evaluation.
                                                            Default: ``None`` .
            dataset_sink_mode (bool): Determines whether to pass the data through dataset channel.
                Default: ``False`` .

        Returns:
            Dict, the key is the metric name defined by users and the value is the metrics value for
            the model in the test mode.

        Examples:
            >>> from mindspore import nn
            >>> from mindspore.train import Model
            >>>
            >>> # Create the dataset taking MNIST as an example. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/mnist.py
            >>> dataset = create_dataset()
            >>> # Define the network structure of LeNet5. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
            >>> net = LeNet5()
            >>> loss = nn.SoftmaxCrossEntropyWithLogits(sparse=True)
            >>> model = Model(net, loss_fn=loss, optimizer=None, metrics={'acc'})
            >>> acc = model.eval(dataset, dataset_sink_mode=False)
        """
        _init_auto_parallel_context(self._network)
        dataset_sink_mode = Validator.check_bool(dataset_sink_mode)

        _device_number_check(self._parallel_mode, self._device_number)
        if not self._metric_fns:
            raise ValueError("For Model.eval, the model argument 'metrics' can not be None or empty, "
                             "you should set the argument 'metrics' for model.")
        if isinstance(self._eval_network, nn.GraphCell) and dataset_sink_mode:
            raise ValueError("Sink mode is currently not supported when evaluating with a GraphCell.")
        if callbacks:
            self._check_methods_for_custom_callbacks(callbacks, "eval")
        cb_params = _InternalCallbackParam()
        cb_params.eval_network = self._eval_network
        cb_params.valid_dataset = valid_dataset
        cb_params.batch_num = valid_dataset.get_dataset_size()
        cb_params.mode = "eval"
        cb_params.cur_step_num = 0
        cb_params.list_callback = self._transform_callbacks(callbacks)
        cb_params.network = self._network

        self._clear_metrics()

        # Embedding cache server as a storage service, no need to execute eval.
        is_embedding_cache_server = _is_role_pserver() and _cache_enable()
        if is_embedding_cache_server:
            metrics = self._get_metrics()
            cb_params.metrics = metrics
            return metrics

        if context.get_context("device_target") == "CPU" and dataset_sink_mode:
            dataset_sink_mode = False
            logger.info("CPU cannot support dataset sink mode currently."
                        "So the evaluating process will be performed with dataset non-sink mode.")

        with _CallbackManager(callbacks) as list_callback:
            if dataset_sink_mode:
                eval_result = self._eval_dataset_sink_process(valid_dataset, list_callback, cb_params)
            else:
                eval_result = self._eval_process(valid_dataset, list_callback, cb_params)

        # When it's distributed training and using MindRT,
        # the node id should be reset to start from 0.
        # This is to avoid the timeout when finding the actor route tables in 'train' and 'eval' case(or 'fit').
        if _enable_distributed_mindrt():
            _reset_op_id_with_offset()
        _clear_auto_parallel_context(self._network)

        return eval_result

    def _predict_lite(self, *predict_data, config=None):
        """
        Generate output predictions for the input samples using backend 'lite'.

        Args:
            predict_data (Union[Tensor, list[Tensor], tuple[Tensor]], optional):
                The predict data, can be a single tensor,
                a list of tensor, or a tuple of tensor.

            config (dict, optional): The config parameter is enabled when the backend is ‘lite’.

                The config includes two parts: config_path (configPath, str) and config_item (str, dict).
                When the config_item is set, its priority is higher than the config_path. Set the ranking
                table file for inference. The content of the configuration file is as follows:

                config_path defines the path of the configuration file, which is used to pass user-defined
                    options during model building. In the following scenarios, users may need to set parameters.
                    For example: "/home/user/config.ini". Default value: ``"" `` , here is the content of the
                    config.ini file:

                The config has 3 forms：
                1. configPath defines the path of the configuration file, which is used to pass user-defined
                options during model building. Default value: ``"" ``.

                .. code-block::

                    config = {"configPath" : "/home/user/config.ini"}

                Here is the content of the config.ini file:

                .. code-block::

                    [ascend_context]
                    rank_table_file = [path_a](storage initial path of the rank table file)
                    [execution_plan]
                    [op_name1] = data_type:float16 (operator named op_name1 is set to data type float16)
                    [op_name2] = data_type:float32 (operator named op_name2 is set to data type float32)

                2. Set the user-defined options in parameter dictionary, it is done as follows:

                .. code-block::

                    config = {"ascend_context" : {"rank_table_file" : "path_b"},
                              "execution_plan" : {"op_name1" : "data_type:float16", "op_name2" : "data_type:float32"}}

                3. Both the `configPath` and the `parameter dictionary` are configured, The priority of the parameter
                dictionary is higher than that of the content in the configuration file. It is done as follows:

                .. code-block::

                    config = {"configPath" : "/home/user/config.ini",
                              "ascend_context" : {"rank_table_file" : "path_b"},
                              "execution_plan" : {"op_name3" : "data_type:float16", "op_name4" : "data_type:float32"}}

                Note that in the "configPath" the parameter is set as "rank_table_file = [path_a]", but in dict is set
                as "ascend_context" : {"rank_table_file" : "path_b"}, in this case, the path_b takes precedence.

        Returns:
            Tensor, array(s) of predictions.
        """

        def _get_lite_context(lite_context_input):
            # use default lite context parameters for now
            device_target = context.get_context("device_target").lower()
            lite_context_input.target = [device_target]
            if device_target == 'cpu':
                inter_op_parallel_num = context.get_context('inter_op_parallel_num')
                if inter_op_parallel_num and isinstance(inter_op_parallel_num, int):
                    lite_context_input.cpu.inter_op_parallel_num = inter_op_parallel_num
            elif device_target == 'gpu':
                device_id = context.get_context('device_id')
                if device_id and isinstance(device_id, int):
                    lite_context_input.gpu.device_id = device_id
                if context.get_auto_parallel_context("parallel_mode") == context.ParallelMode.SEMI_AUTO_PARALLEL:
                    from mindspore.communication import init, get_rank
                    init()
                    lite_context_input.gpu.rank_id = get_rank()
            elif device_target == 'ascend':
                device_id = context.get_context('device_id')
                if device_id and isinstance(device_id, int):
                    lite_context_input.ascend.device_id = device_id
                if context.get_auto_parallel_context("parallel_mode") == context.ParallelMode.SEMI_AUTO_PARALLEL:
                    from mindspore.communication import init, get_rank
                    init()
                    lite_context_input.ascend.rank_id = get_rank()
                    lite_context_input.ascend.provider = "ge"
            else:
                raise RuntimeError(f"For predict lite, device target should be in ['gpu', 'cpu', 'ascend']"
                                   f" but got {device_target}")
            return lite_context_input

        if not self._mindspore_lite:
            self._mindspore_lite = importlib.import_module('mindspore_lite')

        use_past = False  # default execute full model inference
        model_group_id = None
        if self._predict_network.get_flags().__contains__("is_first_iteration"):
            is_first_iteration = self._predict_network.get_flags()['is_first_iteration']
            if isinstance(is_first_iteration, bool):
                use_past = not is_first_iteration
                model_group_id = self._mindspore_lite_model_group_id

        check_input_data(*predict_data, data_class=(int, float, str, None, Tensor))
        if use_past:
            # Execute incremental model inference
            if not self._lite_incremental_predictor:
                lite_context = _get_lite_context(self._mindspore_lite.Context())
                self._lite_incremental_predictor = \
                    self._mindspore_lite.lite_infer.LiteInfer(self, *predict_data, context=lite_context,
                                                              model_group_id=model_group_id, config=config)

            inputs = self._lite_incremental_predictor.get_inputs()
            if len(predict_data) != len(inputs):
                raise RuntimeError(f"For 'Model.predict', numbers of predict_data {len(predict_data)} "
                                   f"is not equal to numbers of net input {len(inputs)}")
            for i, single_data in enumerate(predict_data):
                inputs[i].set_data_from_numpy(single_data.asnumpy())
            outputs: list = self._lite_incremental_predictor.predict(inputs)
        else:
            # Execute full model inference
            if not self._lite_full_predictor:
                lite_context = _get_lite_context(self._mindspore_lite.Context())
                self._lite_full_predictor = \
                    self._mindspore_lite.lite_infer.LiteInfer(self, *predict_data, context=lite_context,
                                                              model_group_id=model_group_id, config=config)

            inputs = self._lite_full_predictor.get_inputs()
            if len(predict_data) != len(inputs):
                raise RuntimeError(f"For 'Model.predict', numbers of predict_data {len(predict_data)} "
                                   f"is not equal to numbers of net input {len(inputs)}")
            for i, single_data in enumerate(predict_data):
                inputs[i].set_data_from_numpy(single_data.asnumpy())
            outputs: list = self._lite_full_predictor.predict(inputs)
        if not outputs:
            return Tensor(outputs)
        if len(outputs) == 1:
            return Tensor(outputs[0].get_data_to_numpy())
        outputs = [Tensor(single_output.get_data_to_numpy()) for single_output in outputs]
        return tuple(outputs)

    def predict(self, *predict_data, backend=None, config=None):
        """
        Generate output predictions for the input samples.

        Args:
            predict_data (Union[Tensor, list[Tensor], tuple[Tensor]], optional):
                The predict data, can be a single tensor,
                a list of tensor, or a tuple of tensor.
            backend (str): Select predict backend, this parameter is an experimental feature
                and is mainly used for MindSpore Lite cloud-side inference. Default: ``None`` .
            config (dict, optional) - The config parameter is enabled when the backend is ‘lite’.
                The config includes two parts: config_path (configPath, str) and config_item (str, dict).
                When the config_item is set, its priority is higher than the config_path. Set the ranking
                table file for inference. The content of the configuration file is as follows:

                config_path defines the path of the configuration file, which is used to pass user-defined
                options during model building. In the following scenarios, users may need to set parameters.
                For example: "/home/user/config.ini". Default value: ``""`` , here is the content of the
                config.ini file:

                .. code-block::

                    [ascend_context]
                    rank_table_file = [path_a](storage initial path of the rank table file)
                    [execution_plan]
                    [op_name1] = data_type:float16 (operator named op_name1 is set to data type float16)
                    [op_name2] = data_type:float32 (operator named op_name2 is set to data type float32)

                When only the config_path is configured, it is done as follows:

                .. code-block::

                    config = {"configPath" : "/home/user/config.ini"}

                When only the config_dict is configured, it is done as follows:

                .. code-block::

                    config = {"ascend_context" : {"rank_table_file" : "path_b"},
                              "execution_plan" : {"op_name1" : "data_type:float16", "op_name2" : "data_type:float32"}}

                When both the `config_path` and the `config_dict` are configured, it is done as follows:

                .. code-block::

                    config = {"configPath" : "/home/user/config.ini",
                              "ascend_context" : {"rank_table_file" : "path_b"},
                              "execution_plan" : {"op_name3" : "data_type:float16", "op_name4" : "data_type:float32"}}

                Note that both the "configPath" is configured in the config_dict and the config_item,
                in this case, the path_b in the config_dict takes precedence.

        Returns:
            Tensor, array(s) of predictions.

        Examples:
            >>> import numpy as np
            >>> import mindspore
            >>> from mindspore import Tensor
            >>> from mindspore.train import Model
            >>>
            >>> input_data = Tensor(np.random.randint(0, 255, [1, 1, 32, 32]), mindspore.float32)
            >>> # Define the network structure of LeNet5. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
            >>> model = Model(LeNet5())
            >>> result = model.predict(input_data)
        """
        _init_auto_parallel_context(self._network)
        if backend not in ['lite', None]:
            raise ValueError(f"For Model.predict, `backend` should be 'lite' or None, but got {backend}")
        if backend == "lite" and self._lite_infer:
            # pylint: disable=broad-except
            try:
                return self._predict_lite(*predict_data, config=config)
            except RuntimeError:
                self._lite_infer = False
                logger.warning("Lite inference failed, fallback to original inference!")
            except ImportError:
                self._lite_infer = False
                logger.warning("Import mindspore_lite failed, fallback to original inference!")
            except BaseException as e:
                self._lite_infer = False
                logger.warning(f"Lite inference failed, {e.__str__()}, fallback to original inference!")
        _clear_auto_parallel_context(self._network)

        def _check_input_data():
            """Input data check."""
            for item in predict_data:
                if item is None:
                    continue
                if isinstance(item, Tensor):
                    if item.size == 0:
                        msg = "The input data can not be empty."
                        logger.critical(msg)
                        raise ValueError(msg)
                    continue
                if not isinstance(item, (int, float, str)):
                    data_class_str = "Tensor, None, int, float, str"
                    raise TypeError(f'The types of input data must be in the Union({data_class_str}, ' \
                                    f'tuple[{data_class_str}], list[{data_class_str}], dict[{data_class_str}]), ' \
                                    f'but got type {item if item is None else type(item).__name__}.')

        self._check_network_mode(self._predict_network, False)
        _check_input_data()
        _parallel_predict_check()
        result = self._predict_network(*predict_data)

        check_output_data(result)

        # When it's distributed training and using MindRT,
        # the node id should be reset to start from 0.
        # This is to avoid the timeout when finding the actor route tables in 'train' and 'eval' case(or 'fit').
        if _enable_distributed_mindrt():
            _reset_op_id_with_offset()

        return result

    def _infer_train_check(self, train_dataset, dataset_sink_mode, sink_size):
        """
        Check arguments of training.

        Args:
            train_dataset (Dataset): A training dataset iterator.
            dataset_sink_mode (bool): Determines whether to pass the data through dataset channel.
            sink_size (int): Control the amount of data in each sink.
        """
        if _get_parallel_mode() not in (ParallelMode.SEMI_AUTO_PARALLEL, ParallelMode.AUTO_PARALLEL):
            raise RuntimeError("'infer_train_layout' only supports 'semi_auto_parallel' and 'auto_parallel' "
                               "mode, but got {}.".format(_get_parallel_mode()))
        dataset_sink_mode = Validator.check_bool(dataset_sink_mode)
        if not dataset_sink_mode:
            raise ValueError("Only dataset sink mode is supported for now.")
        if isinstance(self._train_network, nn.GraphCell) and dataset_sink_mode:
            raise ValueError("Dataset sink mode is currently not supported when training with a GraphCell.")
        Validator.check_is_int(sink_size)
        dataset_size = train_dataset.get_dataset_size()
        if dataset_size == 0:
            raise ValueError("There is no valid data in dataset, please check dataset file firstly.")
        if sink_size == -1:
            sink_size = dataset_size
        if sink_size < -1 or sink_size == 0:
            raise ValueError("For 'infer_train_layout', the argument 'sink_size' must be -1 or positive, "
                             "but got sink_size {}.".format(sink_size))

    def infer_train_layout(self, train_dataset, dataset_sink_mode=True, sink_size=-1):
        """
        Generate parameter layout for the train network when using `AutoParallel(cell)`
        to enable parallel mode.

        Only dataset sink mode is supported for now.

        .. warning::
            This is an experimental API that is subject to change or deletion.

        Note:
            This is a pre-compile function. The arguments should be the same as model.train() function.

        Args:
            train_dataset (Dataset): A training dataset iterator. If there is no
                         loss_fn, a tuple with multiple data (data1, data2, data3, ...) should be
                         returned and passed to the network. Otherwise, a tuple (data, label) should
                         be returned. The data and label would be passed to the network and loss
                         function respectively.
            dataset_sink_mode (bool): Determines whether to pass the data through dataset channel.
                                      Configure pynative mode or CPU, the training process will be performed with
                                      dataset not sink. Default: ``True`` .
            sink_size (int): Control the number of steps for each sinking.
                             If dataset_sink_mode is False, set sink_size as invalid.
                             If sink_size = -1, sink the complete dataset for each epoch.
                             If sink_size > 0, sink sink_size data for each epoch.
                             Default: ``-1`` .

        Returns:
            Dict, Parameter layout dictionary used for load distributed checkpoint

        Examples:
            >>> # This example should be run with multiple devices. Refer to the tutorial > Distributed Training on
            >>> # mindspore.cn.
            >>> import numpy as np
            >>> import mindspore as ms
            >>> from mindspore import Tensor, nn
            >>> from mindspore.train import Model
            >>> from mindspore.communication import init
            >>> from mindspore.parallel.auto_parallel import AutoParallel
            >>>
            >>> ms.set_context(mode=ms.GRAPH_MODE)
            >>> init()
            >>>
            >>> # Create the dataset taking MNIST as an example. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/mnist.py
            >>> dataset = create_dataset()
            >>> # Define the network structure of LeNet5. Refer to
            >>> # https://gitee.com/mindspore/docs/blob/master/docs/mindspore/code/lenet.py
            >>> net = LeNet5()
            >>> parallel_net = AutoParallel(net)
            >>> loss = nn.SoftmaxCrossEntropyWithLogits()
            >>> loss_scale_manager = ms.FixedLossScaleManager()
            >>> optim = nn.Momentum(params=net.trainable_params(), learning_rate=0.1, momentum=0.9)
            >>> model = Model(parallel_net, loss_fn=loss, optimizer=optim, metrics=None,
            ...                  loss_scale_manager=loss_scale_manager)
            >>> layout_dict = model.infer_train_layout(dataset)
        """
        _init_auto_parallel_context(self._network)
        self._infer_train_check(train_dataset, dataset_sink_mode, sink_size)

        train_dataset.__no_send__ = True
        train_dataset_helper, train_network = self._exec_preprocess(is_train=True,
                                                                    dataset=train_dataset,
                                                                    dataset_sink_mode=dataset_sink_mode,
                                                                    sink_size=sink_size)
        for inputs in train_dataset_helper:
            train_network.compile(*inputs)
            break
        train_dataset.__model_hash__ = hash(self)
        _clear_auto_parallel_context(self._network)
        return train_network.parameter_layout_dict

    def infer_predict_layout(self, *predict_data, skip_backend_compile=False):
        """
        Generate parameter layout for the predict network when using `AutoParallel(cell)`
        to enable parallel mode.

        Data could be a single tensor or multiple tensors.

        Note:
            Batch data should be put together in one tensor.

        Args:
            predict_data (Union[Tensor, list[Tensor], tuple[Tensor]], optional):
                The predict data, can be a single tensor,
                a list of tensor, or a tuple of tensor.
            skip_backend_compile (bool): Only run the frontend compile process,
                skip the compile process on the device side. Set this flag to True may
                lead to recompiling process can not hit cache.

        Returns:
            Dict, Parameter layout dictionary used for load distributed checkpoint.
            Using as one of input parameters of load_distributed_checkpoint, always.

        Raises:
            RuntimeError: If not in GRAPH_MODE.

        Examples:
            >>> import numpy as np
            >>> import mindspore as ms
            >>> import mindspore.nn as nn
            >>> from mindspore import Tensor
            >>> from mindspore.train import Model
            >>> from mindspore.ops import operations as P
            >>> from mindspore import context
            >>> from mindspore.communication import init
            >>> from mindspore.parallel.auto_parallel import AutoParallel
            >>>
            >>> class Net(nn.Cell):
            ...     def __init__(self):
            ...         super(Net, self).__init__()
            ...         self.fc1 = nn.Dense(128, 768, activation='relu')
            ...         self.fc2 = nn.Dense(128, 768, activation='relu')
            ...         self.fc3 = nn.Dense(128, 768, activation='relu')
            ...         self.fc4 = nn.Dense(768, 768, activation='relu')
            ...         self.relu4 = nn.ReLU()
            ...         self.relu5 = nn.ReLU()
            ...         self.transpose = P.Transpose()
            ...         self.matmul1 = P.MatMul()
            ...         self.matmul2 = P.MatMul()
            ...
            ...     def construct(self, x):
            ...         q = self.fc1(x)
            ...         k = self.fc2(x)
            ...         v = self.fc3(x)
            ...         k = self.transpose(k, (1, 0))
            ...         c = self.relu4(self.matmul1(q, k))
            ...         s = self.relu5(self.matmul2(c, v))
            ...         s = self.fc4(s)
            ...         return s
            ...
            >>> ms.set_context(mode=ms.GRAPH_MODE)
            >>> init()
            >>> inputs = Tensor(np.ones([32, 128]).astype(np.float32))
            >>> net = Net()
            >>> parallel_net = AutoParallel(net, parallel_mode='semi_auto')
            >>> model = Model(parallel_net)
            >>> predict_map = model.infer_predict_layout(inputs)
        """
        _init_auto_parallel_context(self._network)
        if _get_parallel_mode() not in (ParallelMode.SEMI_AUTO_PARALLEL, ParallelMode.AUTO_PARALLEL):
            raise RuntimeError('Infer predict layout only supports semi auto parallel and auto parallel mode.')
        _parallel_predict_check()
        check_input_data(*predict_data, data_class=(int, float, str, None, Tensor))

        predict_net = self._predict_network
        # Unlike the cases in build_train_network() and build_eval_network(), 'multi_subgraphs' is not set
        predict_net = self._check_network_mode(predict_net, False)
        if skip_backend_compile:
            origin_phase = predict_net.phase
            predict_net.phase = "export." + predict_net.phase
            predict_net.compile(*predict_data)
            # set phase back to prevent from hitting incomplete compile cache
            predict_net.phase = origin_phase
        else:
            predict_net.compile(*predict_data)
        _clear_auto_parallel_context(self._network)
        return predict_net.parameter_layout_dict

    def _flush_from_cache(self, cb_params):
        """Flush cache data to host if tensor is cache enable."""
        params = cb_params.train_network.get_parameters()
        for param in params:
            if param.cache_enable:
                Tensor(param).flush_from_cache()

    @property
    def train_network(self):
        """
        Get the model's train network.

        Returns:
            Object, the instance of train network.
        """
        return self._train_network

    @property
    def predict_network(self):
        """
        Get the model's predict network.

        Returns:
            Object, the instance of predict network.
        """
        return self._predict_network

    @property
    def eval_network(self):
        """
        Get the model's eval network.

        Returns:
            Object, the instance of evaluate network.
        """
        return self._eval_network


__all__ = ["Model"]
