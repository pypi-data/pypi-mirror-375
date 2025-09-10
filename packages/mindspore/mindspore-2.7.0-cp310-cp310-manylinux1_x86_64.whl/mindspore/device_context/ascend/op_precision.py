# Copyright 2024 Huawei Technologies Co., Ltd
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

"""Op precision interfaces."""
import os
from mindspore._checkparam import args_type_check
from .device import _is_supported

try:
    from mindspore._c_expression import AscendOpPrecisionConf
except ImportError:
    pass

function_status = {'precision_mode': False, 'op_precision_mode': False,
                   'matmul_allow_hf32': False, 'conv_allow_hf32': False}


def precision_mode(mode):
    """
    Configure mixed precision mode setting. The framework set the configuration of Atlas training series
    products to "force_fp16" by default, and set the configuration for other products such as the Atlas A2
    training series products to "must_keep_origin_dtype" by default.
    For detailed information, please refer to `Ascend community
    <https://www.hiascend.com/document/detail/zh/canncommercial/80RC3/apiref/appdevgapi/aclcppdevg_03_1371.html/>`_ .

    Note:
        - The default value of `precision_mode` is experimental parameter, may change in the future.

    Args:
        mode (str): The operator precision mode setting.
            The value range is as follows:

            - force_fp16: When the operator supports both float16 and float32, directly choose float16.
            - allow_fp32_to_fp16: For matrix-type operators, use float16. For vector-type operators, prioritize
              the original precision. If the operator in the network model supports float32, retain the original
              precision float32. If the operator in the network model does not support float32, directly reduce
              the precision to float16.
            - allow_mix_precision: Automatic mixed precision, for all operators in the network, according to the
              built-in optimization strategy, automatically reduce the precision of some operators to float16 or
              bfloat16.
            - must_keep_origin_dtype: Maintain the original precision.
            - force_fp32: When the input of the matrix calculation operator is float16, and the output supports both
              float16 and float32, force the output to be converted to float32.
            - allow_fp32_to_bf16: For matrix-type operators, use bfloat16. For vector-type operators, prioritize the
              original precision. If the operator in the network model supports float32, retain the original precision
              float32. If the operator in the network model does not support float32, directly reduce the precision
              to bfloat16.
            - allow_mix_precision_fp16: Automatic mixed precision, for all operators in the network, according to
              the built-in optimization strategy, automatically reduce the precision of some operators to float16.
            - allow_mix_precision_bf16: Automatic mixed precision, for all operators in the network, according to
              the built-in optimization strategy, automatically reduce the precision of some operators to bfloat16.

    Examples:
        >>> import mindspore as ms
        >>> ms.device_context.ascend.op_precision.precision_mode("force_fp16")
    """
    if not function_status['precision_mode']:
        function_status['precision_mode'] = True
        if not _is_supported():
            return
    if mode == AscendOpPrecisionConf.get_instance().precision_mode():
        return
    # Check the configuration environment whether valid
    if AscendOpPrecisionConf.get_instance().is_precision_mode_configured():
        raise RuntimeError("The 'precision_mode' can not be set repeatedly.")
    supported_modes = [
        "force_fp16",
        "allow_fp32_to_fp16",
        "allow_mix_precision",
        "must_keep_origin_dtype",
        "force_fp32",
        "allow_fp32_to_bf16",
        "allow_mix_precision_fp16",
        "allow_mix_precision_bf16",
    ]
    if mode not in supported_modes:
        raise ValueError(f"For 'precision_mode', the value of mode {mode} must be one of "
                         f"{supported_modes}, but got {mode}.")
    AscendOpPrecisionConf.get_instance().set_precision_mode(mode)


@args_type_check(path=str)
def op_precision_mode(path):
    """
    Path to config file of op precision mode.
    For detailed information, please refer to `Ascend community
    <https://www.hiascend.com/document/detail/zh/canncommercial/80RC3/apiref/appdevgapi/aclcppdevg_03_1371.html/>`_ .

    Args:
        path (str): Directory of the configuration file (.ini format) for setting the operator precision mode.
          The directory can contain letters, digits, underscores (_), hyphens (-), and periods (.).

    Examples:
        >>> import mindspore as ms
        >>> ms.device_context.ascend.op_precision.op_precision_mode("./op_precision_config_file")
    """
    if not function_status['op_precision_mode']:
        function_status['op_precision_mode'] = True
        if not _is_supported():
            return
    if path == AscendOpPrecisionConf.get_instance().op_precision_mode():
        return
    # Check the configuration environment whether valid
    if AscendOpPrecisionConf.get_instance().is_op_precision_mode_configured():
        raise RuntimeError("The 'op_precision_mode' can not be set repeatedly.")
    op_precision_path = path
    real_path = os.path.realpath(op_precision_path)
    if not os.path.exists(real_path):
        raise ValueError(
            f"For 'op_precision_mode', the 'path' is invalid, "
            f"got '{op_precision_path}'."
        )
    AscendOpPrecisionConf.get_instance().set_op_precision_mode(path)


def matmul_allow_hf32(value):
    """
    Whether to convert FP32 to HF32 for Matmul operators. CANN disables FP32 to HF32
    for Matmul operators by default.
    For detailed information, please refer to `Ascend community
    <https://www.hiascend.com/document/detail/zh/canncommercial/80RC3/apiref/appdevgapi/aclcppdevg_03_1371.html/>`_ .

    Note:
        - This is an experimental prototype that is subject to change and/or deletion.

    Args:
        value (bool): Whether to convert FP32 to HF32 for Matmul operators

    Examples:
        >>> import mindspore as ms
        >>> ms.device_context.ascend.op_precision.matmul_allow_hf32(True)
    """
    if not function_status['matmul_allow_hf32']:
        function_status['matmul_allow_hf32'] = True
        if not _is_supported():
            return
    supported_modes = [True, False]
    if value not in supported_modes:
        raise ValueError(f"For 'matmul_allow_hf32', the type of input value must be one of "
                         f"{supported_modes}, but got {value}.")
    is_enable = "1" if value else "0"
    if is_enable == AscendOpPrecisionConf.get_instance().matmul_allow_hf32():
        return
    # Check the configuration environment whether valid
    if AscendOpPrecisionConf.get_instance().is_matmul_allow_hf32_configured():
        raise RuntimeError("The 'matmul_allow_hf32' can not be set repeatedly.")
    AscendOpPrecisionConf.get_instance().set_matmul_allow_hf32(is_enable)


def conv_allow_hf32(value):
    """
    Whether to convert FP32 to HF32 for Conv operators. CANN enables FP32 to HF32
    for Conv operators by default.
    For detailed information, please refer to `Ascend community
    <https://www.hiascend.com/document/detail/zh/canncommercial/80RC3/apiref/appdevgapi/aclcppdevg_03_1371.html/>`_ .

    Note:
        - This is an experimental prototype that is subject to change and/or deletion.

    Args:
        value (bool): Whether to convert FP32 to HF32 for Conv operators.

    Examples:
        >>> import mindspore as ms
        >>> ms.device_context.ascend.op_precision.conv_allow_hf32(True)
    """
    if not function_status['conv_allow_hf32']:
        function_status['conv_allow_hf32'] = True
        if not _is_supported():
            return
    supported_modes = [True, False]
    if value not in supported_modes:
        raise ValueError(f"For 'conv_allow_hf32', the type of input value must be one of "
                         f"{supported_modes}, but got {value}.")
    is_enable = "1" if value else "0"
    if is_enable == AscendOpPrecisionConf.get_instance().conv_allow_hf32():
        return
    # Check the configuration environment whether valid
    if AscendOpPrecisionConf.get_instance().is_conv_allow_hf32_configured():
        raise RuntimeError("The 'conv_allow_hf32' can not be set repeatedly.")
    AscendOpPrecisionConf.get_instance().set_conv_allow_hf32(is_enable)
