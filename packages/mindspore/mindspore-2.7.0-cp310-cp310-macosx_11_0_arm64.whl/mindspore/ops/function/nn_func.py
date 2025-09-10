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

"""Defines nn operators with functional form."""
from __future__ import absolute_import
from math import pi, log, floor

from mindspore import context
from mindspore import log as logger
import mindspore.ops as ops
from mindspore.ops.primitive import constexpr, _primexpr
from mindspore.ops import operations as P
from mindspore.ops import functional as F
from mindspore.ops.operations import nn_ops as NN_OPS
from mindspore.ops.operations import _sequence_ops as seq
import mindspore.common.dtype as mstype
from mindspore.ops.function.math_func import logsumexp, div
from mindspore.ops.function.random_func import _get_seed, _set_prim_op_user_data
from mindspore.common.tensor import Tensor
from mindspore._c_expression import TensorPy as Tensor_
from mindspore.ops._primitive_cache import _get_cache_prim
from mindspore import _checkparam as validator
from mindspore.ops.composite.multitype_ops._constexpr_utils import raise_value_error
from mindspore.ops.operations.nn_ops import MaxUnpool2D, MaxUnpool3D
from mindspore.ops.operations.nn_ops import FractionalMaxPoolWithFixedKsize, FractionalMaxPool3DWithFixedKsize
from mindspore.ops.operations.nn_ops import PadV3
from mindspore.ops.operations.nn_ops import ChannelShuffle
from mindspore.ops.operations.nn_ops import TripletMarginLoss
from mindspore.ops.operations._sequence_ops import TupleToTensor, TensorToTuple, ListToTensor
from mindspore.common.api import _function_forbid_reuse
from mindspore.ops.auto_generate import log_softmax, dense, prelu, celu, fast_gelu, silu, elu, sigmoid, relu6, \
    softmax_impl, swiglu, logsigmoid_op, kl_div_op, divs_op, l1_loss_ext
from mindspore.ops.auto_generate import relu_op, inplace_relu_op
from mindspore.ops.auto_generate import group_norm_op, rms_norm, add_rms_norm, layer_norm_ext_op, batch_norm_ext_op,\
    mse_loss_ext
# 1
from mindspore.ops.auto_generate import (reflection_pad_1d_op, reflection_pad_2d_op, add_layernorm_v2_op,
                                         reflection_pad_3d_op,  # pylint: disable=W0611
                                         replication_pad_1d_op, replication_pad_2d_op, replication_pad_3d_op,
                                         constant_pad_nd_op, func_dropout_ext_op, reverse_v2_impl, avg_pool2d_op,
                                         upsample_nearest1d_op, upsample_nearest2d_op, upsample_nearest3d_op,
                                         upsample_linear1d_op, upsample_bilinear2d_op, upsample_bicubic2d_op,
                                         upsample_trilinear3d_impl, fill_scalar_op, floor_op, nllloss_2d_op,
                                         masked_fill_op, masked_select, ones, flatten_ext, conv_transpose2d,
                                         func_max_pool2d_op)
# 2
from mindspore.ops.auto_generate.pyboost_inner_prim import grid_sampler_2d_impl, grid_sampler_3d_impl
# 3

# 4

# 5

# 6

# 7

# 8

# 9

# 10

# 11

# 12

# 13

# 14

# 15
from mindspore.ops.auto_generate import avg_pool3d_ext_op
# 16

# 17

# 18

# 19

# 20
from mindspore.ops.functional_overload import conv3d as conv3d_op
from mindspore.ops.auto_generate.gen_ops_prim import embedding_op, MaxPoolWithIndices, \
    PromptFlashAttention, MaxPoolWithMask
from mindspore.ops.auto_generate.gen_ops_prim import conv2d_ext_op, \
    conv2d_padding_op, conv1d_ext_op, conv1d_padding_op, speed_fusion_attention_op
from mindspore.common.generator import default_generator
from mindspore.ops.auto_generate import hardshrink, hardsigmoid, hardswish
from mindspore.ops.auto_generate import softshrink
from mindspore.ops.auto_generate import soft_margin_loss
from mindspore.ops.auto_generate import moe_token_permute, moe_token_unpermute, ring_attention_update
from mindspore.ops.auto_generate import adaptive_avg_pool2d_ext_op
from mindspore.ops.auto_generate.pyboost_inner_prim import nllloss_impl
from mindspore.ops.auto_generate.pyboost_inner_prim import adaptive_max_pool2d_impl
from mindspore.ops.function.array_func import gather_ext
from mindspore.ops.operations.manually_defined import flash_attention_score, fused_infer_attention_score

abs_ = P.Abs()
add_ = P.Add()
bias_add_ = P.BiasAdd()
cast_ = P.Cast()
div_ = P.Div()
dtype_ = P.DType()
equal_ = P.Equal()
erf_ = P.Erf()
exp_ = P.Exp()
expand_dims_ = P.ExpandDims()
fillv2_ = P.FillV2()
gather_ = P.Gather()
gather_d_ = P.GatherD()
gelu_ = P.GeLU()
greater_ = P.Greater()
less_ = P.Less()
list_to_tensor_ = ListToTensor()
log_ = P.Log()
matmul_ = P.MatMul()
maximum_ = P.Maximum()
minimum_ = P.Minimum()
mish_ = NN_OPS.Mish()
mul_ = P.Mul()
neg_ = P.Neg()
ones_like_ = P.OnesLike()
reduce_mean_ = P.ReduceMean()
reduce_sum_ = P.ReduceSum()
reshape_ = P.Reshape()
scalar_to_tensor_ = P.ScalarToTensor()
select_ = P.Select()
selu_ = NN_OPS.SeLU()
shape_ = P.Shape()
sigmoid_ = P.Sigmoid()
sign_ = P.Sign()
slice_ = P.Slice()
softplus_ = P.Softplus()
softsign_ = P.Softsign()
sqrt_ = P.Sqrt()
square_ = P.Square()
sub_ = P.Sub()
tensor_shape_ = P.TensorShape()
tensor_to_tuple_ = TensorToTuple()
transpose_ = P.Transpose()
tuple_to_tensor_ = TupleToTensor()

check_positive_int_const = validator.check_positive_int
check_positive_int_sequence_const = validator.check_positive_int_sequence
check_positive_float_const = validator.check_positive_float
check_positive_float_sequence_const = validator.check_positive_float_sequence
check_bool_const = constexpr(validator.check_bool)
check_int_const = validator.check_is_int
check_non_negative_float_const = validator.check_non_negative_float
check_string_const = constexpr(validator.check_string)

generator_step_ = Tensor(12, mstype.int64)


def adaptive_avg_pool2d(input, output_size):
    r"""
    Performs 2D adaptive average pooling on a multi-plane input signal.
    That is, for any input size, the size of the specified output is H x W.
    The number of output features is equal to the number of input features.

    The input and output data format can be "NCHW" and "CHW". N is the batch size, C is the number of channels,
    H is the feature height, and W is the feature width.

    For adaptive average pooling for 2D:

    ..  math::
        \begin{align}
        h_{start} &= floor(i * H_{in} / H_{out})\\
        h_{end} &= ceil((i + 1) * H_{in} / H_{out})\\
        w_{start} &= floor(j * W_{in} / W_{out})\\
        w_{end} &= ceil((j + 1) * W_{in} / W_{out})\\
        Output(i,j) &= \frac{\sum Input[h_{start}:h_{end}, w_{start}:w_{end}]}{(h_{end}- h_{start})
        * (w_{end}- w_{start})}
        \end{align}

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input of adaptive_avg_pool2d, which is a 3D or 4D tensor,
            with float16, float32 or float64 data type.
        output_size (Union[int, tuple]): The target output size. `output_size` can be a tuple :math:`(H, W)`,
            or an int H for :math:`(H, H)`. :math:`H` and :math:`W` can be int or None.
            If it is None, it means the output size is the same as the input size.

    Returns:
        Tensor, with the same type as the `input`.

        Shape of the output is `input_shape[:len(input_shape) - len(out_shape)] + out_shape`.

    .. math::

        out\_shape = \begin{cases}
        input\_shape[-2] + output\_size[1], & \text{if } output\_size \text{ is (None, w);}\\
        output\_size[0] + input\_shape[-1], & \text{if } output\_size \text{ is (h, None);}\\
        input\_shape[-2:], & \text{if } output\_size \text{ is (None, None);}\\
        (h, h), & \text{if } output\_size \text{ is h;}\\
        (h, w), & \text{if } output\_size \text{ is (h, w)}
        \end{cases}

    Raises:
        ValueError: If `output_size` is a tuple and the length of `output_size` is not 2.
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not float16, float32 or float64.
        ValueError: If the dimension of `input` is less than or equal to the dimension of `output_size`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> # case 1: output_size=(None, 2)
        >>> input = Tensor(np.array([[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        ...                            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        ...                            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]]), mindspore.float32)
        >>> output = ops.adaptive_avg_pool2d(input, (None, 2))
        >>> print(output)
        [[[1.5 2.5]
          [4.5 5.5]
          [7.5 8.5]]
         [[1.5 2.5]
          [4.5 5.5]
          [7.5 8.5]]
         [[1.5 2.5]
          [4.5 5.5]
          [7.5 8.5]]]
        >>> # case 2: output_size=2
        >>> output = ops.adaptive_avg_pool2d(input, 2)
        >>> print(output)
        [[[3. 4.]
          [6. 7.]]
         [[3. 4.]
          [6. 7.]]
         [[3. 4.]
          [6. 7.]]]
        >>> # case 3: output_size=(1, 2)
        >>> output = ops.adaptive_avg_pool2d(input, (1, 2))
        >>> print(output)
        [[[4.5 5.5]]
         [[4.5 5.5]]
         [[4.5 5.5]]]
    """
    adaptive_avgpool2d_ = _get_cache_prim(P.AdaptiveAvgPool2D)(output_size)
    return adaptive_avgpool2d_(input)


def adaptive_avg_pool2d_ext(input, output_size):
    r"""
    Performs 2D adaptive average pooling on a multi-plane input signal.
    That is, for any input size, the size of the specified output is H x W.
    The number of output features is equal to the number of input features.

    The input and output data format can be "NCHW" and "CHW". N is the batch size, C is the number of channels,
    H is the feature height, and W is the feature width.

    For adaptive average pooling for 2D:

    ..  math::
        \begin{align}
        h_{start} &= floor(i * H_{in} / H_{out})\\
        h_{end} &= ceil((i + 1) * H_{in} / H_{out})\\
        w_{start} &= floor(j * W_{in} / W_{out})\\
        w_{end} &= ceil((j + 1) * W_{in} / W_{out})\\
        Output(i,j) &= \frac{\sum Input[h_{start}:h_{end}, w_{start}:w_{end}]}{(h_{end}- h_{start})
        * (w_{end}- w_{start})}
        \end{align}

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input of adaptive_avg_pool2d, which is a 3D or 4D tensor,
            with float16 or float32 data type.
        output_size (Union[int, tuple]): The target output size. `output_size` can be a tuple :math:`(H, W)`,
            or an int H for :math:`(H, H)`. :math:`H` and :math:`W` can be int or None.
            If it is None, it means the output size is the same as the input size.

    Returns:
        Tensor, with the same type as the `input`.

        Shape of the output is `input_shape[:len(input_shape) - len(out_shape)] + out_shape`.

    .. math::

        out\_shape = \begin{cases}
        input\_shape[-2] + output\_size[1], & \text{if } output\_size \text{ is (None, w);}\\
        output\_size[0] + input\_shape[-1], & \text{if } output\_size \text{ is (h, None);}\\
        input\_shape[-2:], & \text{if } output\_size \text{ is (None, None);}\\
        (h, h), & \text{if } output\_size \text{ is h;}\\
        (h, w), & \text{if } output\_size \text{ is (h, w)}
        \end{cases}

    Raises:
        ValueError: If `output_size` is a tuple and the length of `output_size` is not 2.
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not float16, float32 or float64.
        ValueError: If the dimension of `input` is less than or equal to the dimension of `output_size`.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> # case 1: output_size=(3, 2)
        >>> input = Tensor(np.array([[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        ...                            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        ...                            [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]]), mindspore.float32)
        >>> output = mint.nn.functional.adaptive_avg_pool2d(input, (3, 2))
        >>> print(output)
        [[[1.5 2.5]
         [4.5 5.5]
         [7.5 8.5]]
        [[1.5 2.5]
         [4.5 5.5]
         [7.5 8.5]]
        [[1.5 2.5]
         [4.5 5.5]
         [7.5 8.5]]]
    """
    output_size_ = None
    if isinstance(output_size, int):
        output_size_ = output_size
    else:
        origin_shape = shape_(input)
        w_ = origin_shape[-2] if output_size[-2] is None else output_size[-2]
        h_ = origin_shape[-1] if output_size[-1] is None else output_size[-1]
        output_size_ = (w_, h_)
    return adaptive_avg_pool2d_ext_op(input, output_size_)


def adaptive_avg_pool3d(input, output_size):
    r"""
    Performs 3D adaptive average pooling on a multi-plane input signal.
    That is, for any input size, the size of the specified output is :math:`(D, H, W)`.
    The number of output features is equal to the number of input planes.

    Suppose the last 3 dimension size of x is :math:`(inD, inH, inW)`, the last 3 dimension size of output is
    :math:`(outD, outH, outW)`.

    .. math::
        \begin{array}{ll} \\
            \forall \quad od \in [0,outD-1], oh \in [0,outH-1], ow \in [0,outW-1]\\
            output[od,oh,ow] = \\
            \qquad mean(x[istartD:iendD+1,istartH:iendH+1,istartW:iendW+1])\\
            where,\\
            \qquad istartD= \left\lceil \frac{od * inD}{outD} \right\rceil \\
            \qquad iendD=\left\lfloor \frac{(od+1)* inD}{outD} \right\rfloor \\
            \qquad istartH=\left\lceil \frac{oh * inH}{outH} \right\rceil \\
            \qquad iendH=\left\lfloor \frac{(oh+1) * inH}{outH} \right\rfloor \\
            \qquad istartW=\left\lceil \frac{ow * inW}{outW} \right\rceil \\
            \qquad iendW=\left\lfloor \frac{(ow+1) * inW}{outW} \right\rfloor
        \end{array}

    Args:
        input (Tensor): The input of adaptive_avg_pool3d, which is a 5D or 4D Tensor.
        output_size (Union[int, tuple]): The target output size. `output_size` can be a tuple :math:`(D, H, W)`,
            or an int D for :math:`(D, D, D)`. :math:`D`, :math:`H` and :math:`W` can be int or None
            which means the output size is the same as that of the input.

    Returns:
        Tensor, with the same type as the `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not float16, float32 or float64.
        ValueError: If the dimension of `input` is not 4D or 5D.
        ValueError: If `output_size` value is not positive.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> # case 1: output_size=(3, 3, 4)
        >>> output_size=(3, 3, 4)
        >>> input_val = np.random.randn(4, 3, 5, 6, 7)
        >>> input = Tensor(input_val, mindspore.float32)
        >>> output = ops.adaptive_avg_pool3d(input, output_size)
        >>> print(output.shape)
        (4, 3, 3, 3, 4)
        >>> # case 2: output_size=4
        >>> output_size=5
        >>> input_val = np.random.randn(2, 3, 8, 6, 12)
        >>> input = Tensor(input_val, mindspore.float32)
        >>> output = ops.adaptive_avg_pool3d(input, output_size)
        >>> print(output.shape)
        (2, 3, 5, 5, 5)
        >>> # case 3: output_size=(None, 4, 5)
        >>> output_size=(None, 4, 5)
        >>> input_val = np.random.randn(4, 1, 9, 10, 8)
        >>> input = Tensor(input_val, mindspore.float32)
        >>> output = ops.adaptive_avg_pool3d(input, output_size)
        >>> print(output.shape)
        (4, 1, 9, 4, 5)
    """
    adaptive_avg_pool3d_ = _get_cache_prim(NN_OPS.AdaptiveAvgPool3D)(output_size)
    return adaptive_avg_pool3d_(input)


@constexpr
def _check_avgpool_1d_type_and_int(kernel_size, stride, ceil_mode, count_include_pad):
    """Checks the type of avgpool1d input"""
    validator.check_value_type('kernel_size', kernel_size, [int], 'avg_pool1d')
    validator.check_value_type('stride', stride, (int, tuple), 'avg_pool1d')
    validator.check_value_type('ceil_mode', ceil_mode, bool, 'avg_pool1d')
    validator.check_value_type('count_include_pad', count_include_pad, bool, 'avg_pool1d')
    validator.check_int(kernel_size, 1, validator.GE, "kernel_size", 'avg_pool1d')
    validator.check_int(stride, 1, validator.GE, "stride", 'avg_pool1d')


@constexpr
def check_non_negative_int(arg_value, arg_name=None, prim_name=None):
    """Check argument is non-negative integer, which mean arg_value >= 0."""
    validator.check_non_negative_int(arg_value, arg_name, prim_name)


def avg_pool1d(input_x, kernel_size=1, stride=1, padding=0, ceil_mode=False, count_include_pad=True):
    r"""
    Applies a 1D average pooling over an input Tensor which can be regarded as a composition of 1D input planes.

    Typically the input is of shape :math:`(N_{in}, C_{in}, L_{in})`, avg_pool1d outputs regional average in the
    :math:`(L_{in})`-dimension. Given kernel size :math:`ks = l_{ker}` and `stride` :math:`s = s_0`, the
    operation is as follows.

    .. math::
        \text{output}(N_i, C_j, l) = \frac{1}{l_{ker}} \sum_{n=0}^{l_{ker}-1}
        \text{input}(N_i, C_j, s_0 \times l + n)

    .. warning::
        `kernel_size` is in the range `[1, 255]`. `stride` is in the range `[1, 63]`.

    Args:
        input_x (Tensor): Tensor of shape :math:`(N, C_{in}, L_{in})`.
        kernel_size (int, optional): The size of kernel window used to take the average value. Default: ``1`` .
        stride (Union(int, tuple[int]), optional): The distance of kernel moving. `stride` can either be an int
            number or a tuple of one int number. Default: ``1`` .
        padding (Union(int, tuple[int]), optional): The pad value to be filled. `padding` can either be an integer
            or a tuple of one integer. Default: ``0`` .
        ceil_mode (bool, optional): If True, apply ceil instead of floor to compute the output shape.
            Default: ``False``.
        count_include_pad (bool, optional): If True, include the zero-padding in the averaging calculation.
            Default: ``True`` .

    Returns:
        Tensor of shape :math:`(N, C_{out}, L_{out})`.

    Raises:
        TypeError: If `input_x` is not a Tensor.
        TypeError: If `kernel_size` or `stride` is not an int.
        TypeError: If `ceil_mode` or `count_include_pad` is not a bool.
        ValueError: If length of shape of `input_x` is not equal to `3`.
        ValueError: If `kernel_size` or `stride` is less than `1`.
        ValueError: If `padding` is not int nor a tuple whose length is equal to `2`.
        ValueError: If value(s) of `padding` is less than `0`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.random.randint(0, 10, [1, 3, 6]), mindspore.float32)
        >>> output = ops.avg_pool1d(input_x, kernel_size=6, stride=1)
        >>> print(output.shape)
        (1, 3, 1)
    """
    if not isinstance(input_x, (Tensor, Tensor_)):
        raise TypeError("For avg_pool1d, the input input_x must be tensor")

    _check_avgpool_1d_type_and_int(kernel_size, stride, ceil_mode, count_include_pad)
    if isinstance(padding, int):
        check_non_negative_int(padding, 'padding', 'avg_pool1d')
        padding = (0, 0, 0, 0, padding, padding)
    elif isinstance(padding, tuple):
        if len(padding) != 1:
            raise ValueError("For avg_pool1d, padding should be int or tuple of length 1.")
        for item in padding:
            check_non_negative_int(item, 'padding', 'avg_pool1d')
        padding = (0, 0, 0, 0, padding[0], padding[0])
    else:
        raise TypeError("For avg_pool1d, padding should be int or tuple of length 1.")

    if isinstance(stride, tuple):
        if len(stride) != 1:
            raise ValueError("For avg_pool1d, stride should be int or tuple of length 1.")
        stride = stride[0]

    squeeze_op = _get_cache_prim(P.Squeeze)((2, 3))
    avg_pool_op = _get_cache_prim(P.AvgPool3D)(kernel_size=(1, 1, kernel_size),
                                               strides=(1, 1, stride),
                                               pad_mode='pad',
                                               pad=padding,
                                               ceil_mode=ceil_mode,
                                               count_include_pad=count_include_pad)
    input_x = expand_dims_(input_x, 2)
    input_x = expand_dims_(input_x, 2)
    input_x = avg_pool_op(input_x)
    input_x = squeeze_op(input_x)
    return input_x


@_primexpr
def _check_avgpool_2d_kernel_size(kernel_size):
    """check and calculate the avgpool2d kernel_size"""
    if isinstance(kernel_size, int):
        validator.check_int(kernel_size, 1, validator.GE, "kernel_size", 'avg_pool2d')
        kernel_size = (1, kernel_size, kernel_size)
    elif isinstance(kernel_size, tuple):
        if len(kernel_size) != 2:
            raise ValueError("For avg_pool2d, kernel_size should be int or tuple of length 2.")
        for item in kernel_size:
            validator.check_int(item, 1, validator.GE, "kernel_size", 'avg_pool2d')
        kernel_size = (1, kernel_size[0], kernel_size[1])
    else:
        raise TypeError("For avg_pool2d, kernel_size should be int or tuple of length 2.")
    return kernel_size


@_primexpr
def _check_avgpool_2d_stride(stride):
    """check and calculate the avgpool2d stride"""
    if isinstance(stride, int):
        validator.check_int(stride, 1, validator.GE, "stride", 'avg_pool2d')
        stride = (1, stride, stride)
    elif isinstance(stride, tuple):
        if len(stride) != 2:
            raise ValueError("For avg_pool2d, stride should be int or tuple of length 2.")
        for item in stride:
            validator.check_int(item, 1, validator.GE, "stride", 'avg_pool2d')
        stride = (1, stride[0], stride[1])
    else:
        raise TypeError("For avg_pool2d, stride should be int or tuple of length 2.")
    return stride


@_primexpr
def _check_avgpool_2d_padding(padding):
    """check and calculate the avgpool2d padding"""
    if isinstance(padding, int):
        validator.check_non_negative_int(padding, 'padding', 'avg_pool2d')
        padding = (0, 0, padding, padding, padding, padding)
    elif isinstance(padding, tuple):
        if len(padding) != 4:
            raise ValueError("For avg_pool2d, padding should be int or tuple of length 4.")
        for item in padding:
            validator.check_non_negative_int(item, 'padding', 'avg_pool2d')
        padding = (0, 0, padding[0], padding[1], padding[2], padding[3])
    else:
        raise TypeError("For avg_pool2d, padding should be int or tuple of length 4.")
    return padding


@_primexpr
def _check_avg_pool2d_type_and_value(ceil_mode, count_include_pad, divisor_override):
    """check the type of avgpool2d input"""
    validator.check_value_type('ceil_mode', ceil_mode, bool, 'avg_pool2d')
    validator.check_value_type('count_include_pad', count_include_pad, bool, 'avg_pool2d')
    validator.check_non_negative_int(divisor_override, 'divisor_override', 'avg_pool2d')


def avg_pool2d(input_x, kernel_size=1, stride=1, padding=0, ceil_mode=False, count_include_pad=True,
               divisor_override=0):
    r"""
    Applies a 2D average pooling over an input Tensor which can be regarded as a composition of 2D input planes.
    Typically the input is of shape :math:`(N_{in}, C_{in}, H_{in}, W_{in})`, outputs regional average in the
    :math:`(H_{in}, W_{in})`-dimension. Given kernel size :math:`(k_{h}, k_{w})` and `strides` , the operation
    is as follows.

    .. math::
        \text{output}(N_i, C_j, h, w) = \frac{1}{k_{h} * k_{w}} \sum_{m=0}^{k_{h}-1} \sum_{n=0}^{k_{w}-1}
        \text{input}(N_i, C_j, stride[0] \times h + m, stride[1] \times w + n)

    .. warning::
        `kernel_size` is in the range `[1, 255]`. `stride` is in the range `[1, 63]`.

    Note:
        This interface currently does not support Atlas A2 training series products.

    Args:
        input_x (Tensor): Tensor of shape :math:`(N, C_{in}, H_{in}, W_{in})`.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the average value. It is an int number
            that represents height and width of the kernel, or a tuple of two int numbers that represent height and
            width respectively. Default: ``1`` .
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents the height and
            width of movement are both strides, or a tuple of two int numbers that represent height and width of
            movement respectively. Default: ``1`` .
        padding (Union(int, tuple[int])): The pad value to be filled. Default: 0. If `padding` is an integer, the
            paddings of top, bottom, left and right are the same, equal to pad. If `padding` is a tuple of `4` integers,
            the padding of top, bottom, left and right equal to `padding[0]`, `padding[1]`, `padding[2]` and
            `padding[3]` correspondingly. Default: ``0`` .
        ceil_mode (bool): If True, apply ceil instead of floor to compute the output shape. Default: ``False``.
        count_include_pad (bool): If True, include the zero-padding in the averaging calculation. Default: ``True`` .
        divisor_override (int): If specified, it will be used as divisor in the averaging calculation, otherwise
            `kernel_size` will be used. Default: ``0``, which means not specified.

    Returns:
        Tensor, with shape :math:`(N, C_{out}, H_{out}, W_{out})`.

    Raises:
        TypeError: If `input_x` is not a Tensor.
        TypeError: If `kernel_size` or `stride` is neither int nor tuple.
        TypeError: If `ceil_mode` or `count_include_pad` is not a bool.
        TypeError: If `divisor_override` is not an int.
        ValueError: If length of shape of `input_x` is not equal to `4`.
        ValueError: If `kernel_size` or `stride` is less than 1.
        ValueError: If `kernel_size` or `stride` is a tuple whose length is not equal to `2`.
        ValueError: If `padding` is not int nor a tuple whose length is equal to `4`.
        ValueError: If value(s) of `padding` is less than `0`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.arange(1 * 3 * 3 * 4).reshape(1, 3, 3, 4), mindspore.float32)
        >>> output = ops.avg_pool2d(x, kernel_size=2, stride=1)
        >>> print(output)
        [[[[ 2.5   3.5   4.5]
           [ 6.5   7.5   8.5]]
          [[14.5  15.5  16.5]
           [18.5  19.5  20.5]]
          [[26.5  27.5  28.5]
           [30.5  31.5  32.5]]]]
    """
    if not isinstance(input_x, (Tensor, Tensor_)):
        raise TypeError("For avg_pool2d, the input input_x must be tensor")

    kernel_size = _check_avgpool_2d_kernel_size(kernel_size)
    stride = _check_avgpool_2d_stride(stride)
    padding = _check_avgpool_2d_padding(padding)
    _check_avg_pool2d_type_and_value(ceil_mode, count_include_pad, divisor_override)
    squeeze_op = _get_cache_prim(P.Squeeze)(2)
    avg_pool_op = _get_cache_prim(P.AvgPool3D)(kernel_size=kernel_size,
                                               strides=stride,
                                               pad_mode='pad',
                                               pad=padding,
                                               ceil_mode=ceil_mode,
                                               count_include_pad=count_include_pad,
                                               divisor_override=divisor_override)
    input_x = expand_dims_(input_x, 2)
    input_x = avg_pool_op(input_x)
    input_x = squeeze_op(input_x)
    return input_x


def avg_pool2d_ext(input, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True,
                   divisor_override=None):
    r"""
        Applies a 2D average pooling over an input Tensor which can be regarded as a composition of
        2D input planes. Typically the input is of shape :math:`(N, C, H_{in}, W_{in})` ,
        outputs regional average in the :math:`(H_{in}, W_{in})` -dimension.
        Given kernel size :math:`(kH, kW)` and `stride` , the operation is as follows.

        .. math::
            \text{output}(N_i, C_j, h, w) = \frac{1}{kH * kW} \sum_{m=0}^{kH-1} \sum_{n=0}^{kW-1}
            \text{input}(N_i, C_j, stride[0] \times h + m, stride[1] \times w + n)

        .. note::
            On the Atlas platform, when calculating the input, the precision is degraded from float32 to float16.

        Args:
            input (Tensor): Tensor of shape :math:`(N, C, H_{in}, W_{in})` or :math:`(C, H_{in}, W_{in})`.
            kernel_size (Union[int, tuple[int], list[int]]): The size of kernel used to take the average value.
                Can be a single number or a tuple :math:`(kH, kW)` .
            stride (Union[int, tuple[int], list[int]], optional): The distance of kernel moving.
                Can be a single number or a tuple :math:`(sH, sW)` . Default: ``None``,
                where its value is equal to `kernel_size`.
            padding (Union[int, tuple[int], list[int]], optional): Implicit zero padding to be added on both sides.
                Can be a single number or a tuple :math:`(padH, padW)` . Default: ``0``.
            ceil_mode (bool, optional): If True, apply ceil instead of floor to compute the output shape.
                Default: ``False``.
            count_include_pad (bool, optional): If True, include the zero-padding in the averaging calculation.
                Default: ``True`` .
            divisor_override (int, optional): If specified, it will be used as divisor in the averaging calculation,
                otherwise size of pooling region will be used. Default: ``None``.

        Returns:
            Tensor, with shape :math:`(N, C, H_{out}, W_{out})` or :math:`(C, H_{out}, W_{out})`.

            .. math::
                \begin{array}{ll} \\
                    H_{out} = \frac{H_{in} + 2 \times padding[0] - kernel\_size[0]}{stride[0]} + 1 \\
                    W_{out} = \frac{W_{in} + 2 \times padding[1] - kernel\_size[1]}{stride[1]} + 1
                \end{array}

        Raises:
            TypeError: If `input` is not a Tensor.
            TypeError: If `kernel_size` or `stride` is neither int nor tuple.
            TypeError: If `ceil_mode` or `count_include_pad` is not a bool.
            TypeError: If `divisor_override` is not an int or None.
            ValueError: If the dimension of `input` is not equal to `3` or `4`.
            ValueError: If `kernel_size` or `stride` is less than 1.
            ValueError: If value of `padding` is less than `0`.
            ValueError: If `kernel_size`, `padding` or `stride` is a tuple whose length is not equal to `1` or `2`.

        Supported Platforms:
            ``Ascend``

        Examples:
            >>> import mindspore
            >>> import numpy as np
            >>> from mindspore import Tensor, ops
            >>> x = Tensor(np.arange(1 * 3 * 3 * 4).reshape(1, 3, 3, 4), mindspore.float32)
            >>> output = ops.function.nn_func.avg_pool2d_ext(x, kernel_size=2, stride=1)
            >>> print(output)
            [[[[ 2.5   3.5   4.5]
               [ 6.5   7.5   8.5]]
              [[14.5  15.5  16.5]
               [18.5  19.5  20.5]]
              [[26.5  27.5  28.5]
               [30.5  31.5  32.5]]]]
    """
    if stride is None:
        stride = kernel_size
    return avg_pool2d_op(input, kernel_size, stride, padding, ceil_mode, count_include_pad, divisor_override)


def _check_avg_pool3d_padding(padding):
    """Check the padding value in avg_pool3d op."""
    if isinstance(padding, int):
        validator.check_non_negative_int(padding, 'padding', 'avg_pool3d')
    elif isinstance(padding, tuple):
        if len(padding) != 6:
            raise ValueError("For avg_pool3d, padding should be int or tuple of length 6.")
        for item in padding:
            validator.check_non_negative_int(item, 'padding', 'avg_pool3d')
    else:
        raise TypeError("For avg_pool3d, padding should be int or tuple of length 6.")


def avg_pool3d(input_x, kernel_size=1, stride=1, padding=0, ceil_mode=False, count_include_pad=True,
               divisor_override=0):
    r"""
    Applies a 3D average pooling over an input Tensor which can be regarded as a composition of 3D input planes.
    Typically the input is of shape :math:`(N, C, D_{in}, H_{in}, W_{in})`, avg_pool3d outputs regional average in the
    :math:`(D_{in}, H_{in}, W_{in})`-dimension. Given kernel size :math:`ks = (d_{ker}, h_{ker}, w_{ker})` and stride
    :math:`s = (s_0, s_1, s_2)`, the operation is as follows.

    .. math::
        \text{output}(N_i, C_j, d, h, w) =
        \frac{1}{d_{ker} * h_{ker} * w_{ker}} \sum_{l=0}^{d_{ker}-1} \sum_{m=0}^{h_{ker}-1} \sum_{n=0}^{w_{ker}-1}

        \text{input}(N_i, C_j, s_0 \times d + l, s_1 \times h + m, s_2 \times w + n)

    .. warning::
        `kernel_size` is in the range `[1, 255]`. `stride` is in the range `[1, 63]`.

    Note:
        This interface currently does not support Atlas A2 training series products.

    Args:
        input_x (Tensor): Tensor of shape :math:`(N, C, D_{in}, H_{in}, W_{in})`. Currently support float16 and
            float32 data type.
        kernel_size (Union[int, tuple[int]], optional): The size of kernel used to take the average value, is an int
            number that represents depth, height and width are both `kernel_size`, or a tuple of three int numbers that
            represent depth, height and width respectively. Default: ``1`` .
        stride (Union[int, tuple[int]], optional): The distance of kernel moving, an int number that represents the
            depth, height and width of movement are both stride, or a tuple of three int numbers that represent depth,
            height and width of movement respectively. Default: ``1`` .
        padding (Union(int, tuple[int]), optional): The pad value to be filled. If `padding` is an integer, the addings
            of head, tail, top, bottom, left and right are the same, equal to pad. If `padding` is a tuple of six
            integers, the padding of head, tail, top, bottom, left and right equal to padding[0], padding[1],
            padding[2], padding[3], padding[4] and padding[5] correspondingly. Default: ``0`` .
        ceil_mode (bool, optional): If ``True`` , ceil instead of floor to
            compute the output shape. Default: ``False`` .
        count_include_pad (bool, optional): If ``True`` , averaging calculation
            will include the zero-padding. Default: ``True`` .
        divisor_override (int, optional): If specified, it will be used as divisor in the averaging calculation,
            otherwise `kernel_size` will be used. Default: ``0`` , which means not specified.

    Returns:
        Tensor, with shape :math:`(N, C, D_{out}, H_{out}, W_{out})`. Has the same data type with `input_x`.

    Raises:
        TypeError: If `input_x` is not a Tensor.
        TypeError: If `kernel_size`, `stride` or `padding` is neither an int not a tuple.
        TypeError: If `ceil_mode` or `count_include_pad` is not a bool.
        TypeError: If `divisor_override` is not an int.
        ValueError: If length of shape of `input_x` is not equal to `5`.
        ValueError: If numbers in `kernel_size` or `stride` are not positive.
        ValueError: If `kernel_size` or `stride` is a tuple whose length is not equal to `3`.
        ValueError: If `padding` is a tuple whose length is not equal to `6`.
        ValueError: If element of `padding` is less than `0`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.arange(1 * 2 * 2 * 2 * 3).reshape((1, 2, 2, 2, 3)), mindspore.float16)
        >>> output = ops.avg_pool3d(input_x, kernel_size=2, stride=1)
        >>> print(output)
        [[[[[ 5.  6.]]]
          [[[17. 18.]]]]]
    """
    if not isinstance(input_x, (Tensor, Tensor_)):
        raise TypeError("For avg_pool3d, the input input_x must be tensor")

    _check_avg_pool3d_padding(padding)

    avg_pool_op = _get_cache_prim(P.AvgPool3D)(kernel_size=kernel_size,
                                               strides=stride,
                                               pad_mode='pad',
                                               pad=padding,
                                               ceil_mode=ceil_mode,
                                               count_include_pad=count_include_pad,
                                               divisor_override=divisor_override)
    return avg_pool_op(input_x)


def avg_pool3d_ext(input, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True,
                   divisor_override=None):
    r"""
    Applies a 3D average pooling over an input Tensor which can be regarded as a composition of
    3D input planes. Typically the input is of shape :math:`(N, C, D_{in}, H_{in}, W_{in})` ,
    outputs regional average in the :math:`(D_{in}, H_{in}, W_{in})` -dimension.
    Given kernel size :math:`(kD, kH, kW)` and `stride` , the operation is as follows.

    .. math::
        \text{output}(N_i, C_j, d, h, w) = \frac{1}{kD * kH * kW} \sum_{l=0}^{kD-1} \sum_{m=0}^{kH-1} \sum_{n=0}^{kW-1}

        \text{input}(N_i, C_j, stride[0] \times d + l, stride[1] \times h + m, stride[2] \times w + n)

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Note:
        This interface currently does not support Atlas A2 training series products.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C, D_{in}, H_{in}, W_{in})` or :math:`(C, D_{in}, H_{in}, W_{in})`.
        kernel_size (Union[int, tuple[int], list[int]]): The size of kernel used to take the average value.
            Can be a single number or a tuple :math:`(kD, kH, kW)` .
        stride (Union[int, tuple[int], list[int]], optional): The distance of kernel moving.
            Can be a single number or a tuple :math:`(sD, sH, sW)` . Default: ``None``,
            where its value is equal to `kernel_size`.
        padding (Union[int, tuple[int], list[int]], optional): Implicit zero padding to be added on both sides.
            Can be a single number or a tuple :math:`(padD, padH, padW)` . Default: ``0``.
        ceil_mode (bool, optional): If True, apply ceil instead of floor to compute the output shape.
            Default: ``False``.
        count_include_pad (bool, optional): If True, include the zero-padding in the averaging calculation.
            Default: ``True`` .
        divisor_override (int, optional): If specified, it will be used as divisor in the averaging calculation,
            otherwise size of pooling region will be used. Default: ``None``.

    Returns:
        Tensor, with shape :math:`(N, C, D_{out}, H_{out}, W_{out})` or :math:`(C, D_{out}, H_{out}, W_{out})`.

        .. math::
            \begin{array}{ll} \\
                D_{out} = \frac{D_{in} + 2 \times padding[0] - kernel\_size[0]}{stride[0]} + 1 \\
                H_{out} = \frac{H_{in} + 2 \times padding[1] - kernel\_size[0]}{stride[1]} + 1 \\
                W_{out} = \frac{W_{in} + 2 \times padding[2] - kernel\_size[1]}{stride[2]} + 1
            \end{array}

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `kernel_size` or `stride` is neither int nor tuple.
        TypeError: If `ceil_mode` or `count_include_pad` is not a bool.
        TypeError: If `divisor_override` is not an int or None.
        ValueError: If the dimension of `input` is not equal to `4` or `5`.
        ValueError: If `kernel_size` or `stride` is less than 1.
        ValueError: If value of `padding` is less than `0`.
        ValueError: If `kernel_size`, `padding` or `stride` is a tuple whose length is not equal to `1` or `3`.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.arange(1 * 2 * 2 * 2 * 3).reshape((1, 2, 2, 2, 3)), mindspore.float16)
        >>> output = ops.avg_pool3d_ext(input_x, kernel_size=2, stride=1)
        >>> print(output)
        [[[[[ 5.  6.]]]
          [[[17. 18.]]]]]
    """
    return avg_pool3d_ext_op(input, kernel_size, stride, padding, ceil_mode, count_include_pad, divisor_override)


@constexpr
def is_ascend_backend():
    """Check if the Ascend is used"""
    return context.get_context('device_target') == 'Ascend'


@_primexpr
def _check_adaptive_max_pool1d_output_size(output_size):
    """Check the output_size value in adaptive_max_pool1d op."""
    validator.check_int(output_size, 1, validator.GE, "output_size", 'adaptive_max_pool1d')
    validator.check_value_type('output_size', output_size, [int], 'adaptive_max_pool1d')


def adaptive_max_pool1d(input, output_size):
    r"""
    Applies a 1D adaptive maximum pooling over an input Tensor which can be regarded as
    a composition of 1D input planes.

    Typically, the input is of shape :math:`(N, C, L_{in})`,
    adaptive_max_pool1d outputs regional maximum in the :math:`L_{in}`-dimension. The output is of
    shape :math:`(N, C, L_{out})`, where :math:`L_{out}` is defined by `output_size`.

    Note:
        - :math:`L_{in}` must be divisible by `output_size`.
        - Ascend platform only supports float16 type for input.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C, L_{in})`, with float16 or float32 data type.
        output_size (int): the target output size :math:`L_{out}`.

    Returns:
        Tensor of shape :math:`(N, C, L_{out})`, has the same type as `input`.

    Raises:
        TypeError: If `input` is neither float16 nor float32.
        TypeError: If `output_size` is not an int.
        ValueError: If `output_size` is less than 1.
        ValueError: If the last dimension of `input` is smaller than `output_size`.
        ValueError: If the last dimension of `input` is not divisible by `output_size`.
        ValueError: If length of shape of `input` is not equal to 3.


    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.random.randint(0, 10, [1, 3, 6]), mindspore.float32)
        >>> output = ops.adaptive_max_pool1d(input, output_size=2)
        >>> print(output.shape)
        (1, 3, 2)
    """
    if not isinstance(input, (Tensor, Tensor_)):
        raise TypeError("For adaptive_max_pool1d, the input input must be tensor")

    _check_adaptive_max_pool1d_output_size(output_size)

    x_in_shape = input.shape
    x_dtype = dtype_(input)

    if len(x_in_shape) != 3:
        raise ValueError(f"For adaptive_max_pool1d input must have 3 dim, but got {len(x_in_shape)}.")
    if x_in_shape[2] < output_size:
        raise ValueError(f"For adaptive_max_pool1d input's last dimension must be greater or equal to "
                         f"output size {output_size}, but got {x_in_shape[2]}.")
    if x_in_shape[2] % output_size != 0:
        raise ValueError(f"For adaptive_max_pool1d input's last dimension must be divisible by "
                         f"output size {output_size}, but got {x_in_shape[2]}.")
    if is_ascend_backend():
        if x_dtype not in [mstype.float16]:
            raise TypeError(f"For adaptive_max_pool1d in Ascend platform, the input dtype must be float16, "
                            f"but got {x_dtype}.")
    else:
        if x_dtype not in [mstype.float16, mstype.float32]:
            raise TypeError(f"For adaptive_max_pool1d, the input dtype must be float16 or float32, "
                            f"but got {x_dtype}.")

    squeeze_ = _get_cache_prim(P.Squeeze)(2)
    width = x_in_shape[2]
    stride = width // output_size
    kernel_size = width - (output_size - 1) * stride
    stride = (1, width // output_size)
    kernel_size = (1, kernel_size)
    max_pool_ = _get_cache_prim(NN_OPS.MaxPool)(kernel_size=kernel_size, strides=stride)
    input = expand_dims_(input, 2)
    input = max_pool_(input)
    input = squeeze_(input)

    return input


@constexpr
def _check_adaptive_max_pool2d(return_indices):
    """check the type of return_indices"""
    validator.check_value_type("return_indices", return_indices, bool, "adaptive_max_pool2d")


def adaptive_max_pool2d(input, output_size, return_indices=False):
    r"""
    This operator applies a 2D adaptive max pooling to an input signal composed of multiple input planes.
    That is, for any input size, the size of the specified output is H x W.
    The number of output features is equal to the number of input planes.

    The input and output data format can be "NCHW" and "CHW". N is the batch size, C is the number of channels,
    H is the feature height, and W is the feature width.

    .. math::

        \begin{align}
        h_{start} &= floor(i * H_{in} / H_{out})\\
        h_{end} &= ceil((i + 1) * H_{in} / H_{out})\\
        w_{start} &= floor(j * W_{in} / W_{out})\\
        w_{end} &= ceil((j + 1) * W_{in} / W_{out})\\
        Output(i,j) &= {\max Input[h_{start}:h_{end}, w_{start}:w_{end}]}
        \end{align}

    Note:
        In KBK mode, `output_size` does not support mutable.

    Args:
        input (Tensor): A 3D or 4D tensor,
            with float16, float32 or float64 data type.
        output_size (Union[int, tuple]): The target output size. `output_size` can be a tuple :math:`(H, W)`,
            or an int H for :math:`(H, H)`. :math:`H` and :math:`W` can be int or None.
            If it is None, it means the output size is the same as the input size.

        return_indices (bool, optional): If `return_indices` is ``True`` , the indices of max value would be output.
            Default: ``False`` .

    Returns:
        Tensor, with the same shape and dtype as the `input`.

    Raises:
        TypeError: If `output_size` is not int or tuple.
        TypeError: If `input` is not a tensor.
        TypeError: If `return_indices` is not a bool.
        TypeError: If dtype of `input` is not float16, float32 or float64.
        ValueError: If `output_size` is a tuple and the length of `output_size` is not 2.
        ValueError: If the data format of `input` is not "NCHW" or "CHW".

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> # case 1: output_size=(None, 2)
        >>> input = Tensor(np.array([[[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        ...                             [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]],
        ...                             [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]]]), mindspore.float32)
        >>> output = ops.adaptive_max_pool2d(input, (None, 2))
        >>> print(output)
        [[[[2. 3.]
           [5. 6.]
           [8. 9.]]
          [[2. 3.]
           [5. 6.]
           [8. 9.]]
          [[2. 3.]
           [5. 6.]
           [8. 9.]]]]
        >>> # case 2: output_size=2
        >>> output = ops.adaptive_max_pool2d(input, 2)
        >>> print(output)
        [[[[5. 6.]
           [8. 9.]]
          [[5. 6.]
           [8. 9.]]
          [[5. 6.]
           [8. 9.]]]]
        >>> # case 3: output_size=(1, 2)
        >>> output = ops.adaptive_max_pool2d(input, (1, 2))
        >>> print(output)
        [[[[8. 9.]]
          [[8. 9.]]
          [[8. 9.]]]]
    """
    output_size_ = None
    _check_adaptive_max_pool2d(return_indices)

    if isinstance(output_size, int):
        output_size_ = (output_size, output_size)
    else:
        output_size_ = tuple(-1 if val is None else val for val in output_size)

    if return_indices:
        return adaptive_max_pool2d_impl(input, output_size_)
    return adaptive_max_pool2d_impl(input, output_size_)[0]


def adaptive_max_pool3d(input, output_size, return_indices=False):
    r"""
    Calculates the 3D adaptive max pooling for an input Tensor.

    Args:
        input (Tensor): Tensor, with shape :math:`(C, D, H, W)` or :math:`(N, C, D, H, W)`.
        output_size (Union[int, tuple]): The specified output size, which is an int or Tuple(int) that
            represents depth, height and width, or a tuple of three int numbers that represent depth, height and
            width respectively. The value must be a positive integer. If it is None, the output size and
            input size of the corresponding dimension are the same.
        return_indices (bool, optional): If `return_indices` is `True`, the indices of max value would be output,
            Otherwise, it will not be output. Default: ``False``.

    Returns:
        - **y** (Tensor) - Tensor, with the same number of dims and data type as the `input`.
        - **argmax** (Tensor) - Tensor, the indices of max value, which has the same shape as the
          `y` and it's data type is int32. It will output only when `return_indices` is True.

    Raises:
        TypeError: If `input` is not a Tensor.
        ValueError: If the dimensions number of `input` is not 4 or 5.
        TypeError: If dtype of `input` is not int or float.
        ValueError: If `output_size` is neither an int nor a tuple with shape (3,).

    Supported Platforms:
        ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.arange(0,36).reshape((1, 3, 3, 4)).astype(np.float32))
        >>> output_size = (1, 1, 2)
        >>> output = ops.adaptive_max_pool3d(input, output_size, True)
        >>> print(output[0].asnumpy())
        [[[[33. 35.]]]]
        >>> print(output[1].asnumpy())
        [[[[33 35]]]]
    """
    if isinstance(output_size, int):
        output_size = (output_size, output_size, output_size)
    adaptive_max_pool3d_ = _get_cache_prim(NN_OPS.AdaptiveMaxPool3D)()
    output_size_ = Tensor(output_size, dtype=mstype.int32)
    out = adaptive_max_pool3d_(input, output_size_)
    output = out if return_indices else out[0]
    return output


def max_unpool1d(x, indices, kernel_size, stride=None, padding=0, output_size=None):
    r"""
    Computes the inverse of `max_pool1d`.

    `max_unpool1d` keeps the maximal value and set all position of non-maximal values to zero.
    Typically the input is of shape :math:`(N, C, H_{in})` or :math:`(C, H_{in})`, and the output is of shape
    :math:`(N, C, H_{out})` or :math:`(C, H_{out})`. The operation is as follows.

    .. math::
        \begin{array}{ll} \\
        H_{out} = (H_{in} - 1) \times stride[0] - 2 \times padding[0] + kernel\_size[0] \\
        \end{array}

    Args:
        x (Tensor): The input Tensor to invert. Tensor of shape :math:`(N, C, H_{in})` or :math:`(C, H_{in})`.
        indices (Tensor): Index of maximum value.
          Tensor of shape must be same with input 'x'.
          Values of indices must belong to :math:`[0, H_{in} - 1]`.
          Data type must be in int32 or int64.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value.
        stride (Union[int, tuple[int]]): The distance of kernel moving,
            If stride is 0, (0) or ``None`` , then stride equal to kernel_size.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]]): The pad value to be filled. Default: ``0`` .
        output_size (tuple[int], optional): The output shape. Default: ``None`` .
            If output_size == (), then the shape of output computed by `kernel_size`, `stride` and `padding`.
            If output_size != (), then output_size must be :math:`(N, C, H)` , :math:`(C, H)` or
            :math:`(H)` and output_size must belong to
            :math:`[(N, C, H_{out} - stride[0]), (N, C, H_{out} + stride[0])]`.

    Returns:
        Tensor, with shape :math:`(N, C, H_{out})` or :math:`(C, H_{out})`,
        with the same data type with `x`.

    Raises:
        TypeError: If data type of `x` or `indices` is not supported.
        TypeError: If `kernel_size`, `stride` or `padding` is neither an int nor a tuple.
        ValueError: If numbers in `stride`, `padding` (also support 0 and (0)) or `kernel_size` is not positive.
        ValueError: If the shapes of `x` and `indices` are not equal.
        ValueError: If `x` whose length is not 2 or 3.
        ValueError: If type of `output_size` is not tuple.
        ValueError: If `output_size` whose length is not 0, 2 or 3.
        ValueError: If `output_size` is not close to output size computed by attr `kernel_size`, `stride`, `padding`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[2, 4, 6, 8]]).astype(np.float32))
        >>> indices = Tensor(np.array([[1, 3, 5, 7]]).astype(np.int64))
        >>> output = ops.max_unpool1d(x, indices, kernel_size =2, stride=2, padding=0)
        >>> print(output.asnumpy())
        [[0. 2. 0. 4. 0. 6. 0. 8.]]
    """
    if stride is None:
        stride = kernel_size

    x_shape = shape_(x)
    x_dim = len(x_shape)

    if output_size is None:
        output_size = ()
    else:
        if not isinstance(output_size, tuple):
            raise ValueError(f"For max_unpool1d, output_size must be tuple, but type {type(output_size)}.")
        if len(output_size) not in [0, 1, 2, 3]:
            raise ValueError(f"For max_unpool1d, length of output_size with tuple must be 0, 1, 2, 3, "
                             f"but got type {len(output_size)}.")
        if not output_size:
            output_size = ()
        elif x_dim == 2:
            output_size = (1,) + x_shape[:1] + output_size[-1:] + (1,)
        else:
            output_size = x_shape[:2] + output_size[-1:] + (1,)
    if isinstance(kernel_size, tuple):
        kernel_size = kernel_size + (1,)
    elif isinstance(kernel_size, int):
        kernel_size = (kernel_size, 1)

    if isinstance(stride, tuple):
        stride = stride + (1,)
    elif isinstance(stride, int):
        stride = (stride, 1)

    if isinstance(padding, tuple):
        padding = padding + (0,)
    elif isinstance(padding, int):
        padding = (padding, 0)

    max_unpool_2d = _get_cache_prim(MaxUnpool2D)(ksize=kernel_size, strides=stride,
                                                 pads=padding, output_shape=output_size, data_format="NCHW")
    if x_dim == 2:
        x = x.expand_dims(axis=0)
        indices = indices.expand_dims(axis=0)
        x = x.expand_dims(axis=3)
        indices = indices.expand_dims(axis=3)
        out = max_unpool_2d(x, indices)
        out = out.squeeze(-1)
        out = out.squeeze(0)
    else:
        x = x.expand_dims(axis=3)
        indices = indices.expand_dims(axis=3)
        out = max_unpool_2d(x, indices)
        out = out.squeeze(-1)
    return out


def max_unpool2d(x, indices, kernel_size, stride=None, padding=0, output_size=None):
    r"""
    Computes the inverse of `max_pool2d`.

    `max_unpool2d` keeps the maximal value and set all position of non-maximal values to zero. Typically the input
    is of shape :math:`(N, C, H_{in}, W_{in})` or :math:`(C, H_{in}, W_{in})`, and the output is of
    shape :math:`(N, C, H_{out}, W_{out})` or :math:`(C, H_{out}, W_{out})`. The operation is as follows.

    .. math::
        \begin{array}{ll} \\
        H_{out} = (H{in} - 1) \times stride[0] - 2 \times padding[0] + kernel\_size[0] \\
        W_{out} = (W{in} - 1) \times stride[1] - 2 \times padding[1] + kernel\_size[1] \\
        \end{array}

    Args:
        x (Tensor): The input Tensor to invert.
          Tensor of shape :math:`(N, C, H_{in}, W_{in})` or :math:`(C, H_{in}, W_{in})`.
        indices (Tensor): Max values' index represented by the indices.
          Tensor of shape must be same with input 'x'.
          Values of indices must belong to :math:`[0, H_{in} \times W_{in} - 1]`.
          Data type must be in int32 or int64.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value,
            an int number that represents height and width of the kernel, or a tuple
            of two int numbers that represent height and width respectively.
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents
            the height and width of movement are both stride, or a tuple of two int numbers that
            represent height and width of movement respectively.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]]): The pad value to be filled. Default: ``0`` . If `padding` is an integer,
            the paddings of height and width are the same, equal to padding. If `padding` is a tuple of two
            integers, the padding of height and width equal to padding[0] and padding[1] correspondingly.
        output_size (tuple[int], optional): The target output size. Default: ``None`` .
            If output_size == (), then the shape of output computed by `kernel_size`, `stride` and `padding`.
            If output_size != (), then output_size must be :math:`(N, C, H, W)` , :math:`(C, H, W)` or :math:`(H, W)`
            and output_size must belong to
            :math:`[(N, C, H_{out} - stride[0], W_{out} - stride[1]),
            (N, C, H_{out} + stride[0], W_{out} + stride[1])]`.

    Returns:
        Tensor, with shape :math:`(N, C, H_{out}, W_{out})` or :math:`(C, H_{out}, W_{out})`,
        with the same data type with `x`.

    Raises:
        TypeError: If data type of `x` or `indices` is not supported.
        TypeError: If `kernel_size`, `stride` or `padding` is neither an int nor a tuple.
        ValueError: If numbers in `stride`, `padding` (also support 0 and (0, 0)) or `kernel_size` is not positive.
        ValueError: If the shape of `x` and `indices` are not equal.
        ValueError: If `kernel_size`, `stride` or `padding` is a tuple whose length is not equal to 2.
        ValueError: If `x` whose length is not 3 or 4.
        ValueError: If `output_size` whose type is not tuple.
        ValueError: If `output_size` whose length is not 0, 3 or 4.
        ValueError: If `output_size` is not close to output size computed by attr `kernel_size`, `stride`, `padding`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[[[0, 1], [8, 9]]]]).astype(np.float32))
        >>> indices = Tensor(np.array([[[[0, 1], [2, 3]]]]).astype(np.int64))
        >>> output = ops.max_unpool2d(x, indices, kernel_size=1, stride=1, padding=0)
        >>> print(output.asnumpy())
        [[[[0. 1.]
           [8. 9.]]]]
    """
    if stride is None:
        stride = kernel_size

    x_shape = shape_(x)
    x_dim = len(x_shape)

    if output_size is None:
        output_size = ()
    else:
        if not isinstance(output_size, tuple):
            raise ValueError(f"For max_unpool2d, output_size must be tuple, but type {type(output_size)}.")
        if len(output_size) not in [0, 2, 3, 4]:
            raise ValueError(f"For max_unpool2d, length of output_size with tuple must be 0, 2, 3, 4, "
                             f"but got type {len(output_size)}.")
        if not output_size:
            output_size = ()
        elif x_dim == 3:
            output_size = (1,) + x_shape[:1] + output_size[-2:]
        else:
            output_size = x_shape[:2] + output_size[-2:]

    max_unpool_2d = MaxUnpool2D(ksize=kernel_size, strides=stride, pads=padding, output_shape=output_size,
                                data_format="NCHW")
    if x_dim == 3:
        x = x.expand_dims(axis=0)
        indices = indices.expand_dims(axis=0)
        out = max_unpool_2d(x, indices)
        out = out.squeeze(0)
    else:
        out = max_unpool_2d(x, indices)
    return out


def max_unpool3d(x, indices, kernel_size, stride=None, padding=0, output_size=None):
    r"""
    Computes the inverse of :func:`mindspore.ops.max_pool3d`.

    `max_unpool3d` keeps the maximal value and set all position of non-maximal values to zero.
    Typically the input is of shape :math:`(N, C, D_{in}, H_{in}, W_{in})` or :math:`(C, D_{in}, H_{in}, W_{in})`,
    and the output is of shape :math:`(N, C, D_{out}, H_{out}, W_{out})` or :math:`(C, D_{out}, H_{out}, W_{out})`.
    The operation is as follows.

    .. math::
        \begin{array}{ll} \\
        D_{out} = (D{in} - 1) \times stride[0] - 2 \times padding[0] + kernel\_size[0] \\
        H_{out} = (H{in} - 1) \times stride[1] - 2 \times padding[1] + kernel\_size[1] \\
        W_{out} = (W{in} - 1) \times stride[2] - 2 \times padding[2] + kernel\_size[2] \\
        \end{array}

    Args:
        x (Tensor): The input Tensor to invert.
          Tensor of shape :math:`(N, C, D_{in}, H_{in}, W_{in})` or :math:`(C, D_{in}, H_{in}, W_{in})`.
        indices (Tensor): Max values' index represented by the indices. Tensor of shape must be same with input 'x'.
          Values of indices must belong to :math:`[0, D_{in} \times H_{in} \times W_{in} - 1]`.
          Data type must be in int32 or int64.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value,
            an int number that represents depth, height and width of the kernel, or a tuple
            of three int numbers that represent depth, height and width respectively.
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents
            the depth, height and width of movement are both stride, or a tuple of three int numbers that
            represent depth, height and width of movement respectively.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]]): The pad value to be filled. Default: ``0`` . If `padding` is an integer,
            the paddings of depth, height and width are the same, equal to padding. If `padding` is a tuple of three
            integers, the padding of depth, height and width equal to padding[0], padding[1] and padding[2]
            correspondingly.
        output_size (tuple[int], optional): The output size. Default: ``None`` . If output_size == (), then the shape of
            output computed by `kernel_size`, `stride` and `padding`. If output_size != (), then output_size must be
            :math:`(N, C, D, H, W)` or :math:`(C, D, H, W)` or :math:`(D, H, W)` and output_size must belong to
            :math:`[(N, C, D_{out} - stride[0], H_{out} - stride[1], W_{out} - stride[2]),
            (N, C, D_{out} + stride[0], H_{out} + stride[1], W_{out} + stride[2])]`.

    Returns:
        Tensor, with shape :math:`(N, C, D_{out}, H_{out}, W_{out})` or :math:`(C, D_{out}, H_{out}, W_{out})`,
        with the same data type with `x`.

    Raises:
        TypeError: If data type of `x` or `indices` is not supported.
        TypeError: If `kernel_size`, `stride` or `padding` is neither an int nor a tuple.
        ValueError: If numbers in `stride` or `padding` (also support 0 and (0, 0, 0)) or `kernel_size` is not positive.
        ValueError: If the shape of `x` and `indices` are not equal.
        ValueError: If `kernel_size`, `stride` or `padding` is a tuple whose length is not equal to 3.
        ValueError: If `x` whose length is not 4 or 5.
        ValueError: If `output_size` whose length is not 0, 4 or 5.
        ValueError: If `output_size` whose type is not tuple.
        ValueError: If `output_size` is not close to output size computed by attr `kernel_size`, `stride`, `padding`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[[[[0, 1], [8, 9]]]]]).astype(np.float32))
        >>> indices= Tensor(np.array([[[[[0, 1], [2, 3]]]]]).astype(np.int64))
        >>> output = ops.max_unpool3d(x, indices, kernel_size=2, stride=1, padding=0)
        >>> print(output)
        [[[[[0. 1. 8.]
            [9. 0. 0.]
            [0. 0. 0.]]
           [[0. 0. 0.]
            [0. 0. 0.]
            [0. 0. 0.]]]]]
    """
    if stride is None:
        stride = kernel_size

    x_shape = shape_(x)
    x_dim = len(x_shape)

    if output_size is None:
        output_size = ()
    elif not isinstance(output_size, tuple):
        raise ValueError(f"For max_unpool3d, output_size must be tuple, but type {type(output_size)}.")
    elif len(output_size) not in [0, 3, 4, 5]:
        raise ValueError(f"For max_unpool3d, length of output_size with tuple must be 0, 3, 4, 5, "
                         f"but got type {len(output_size)}.")
    if not output_size:
        output_size = ()
    elif x_dim == 5:
        output_size = x_shape[:2] + output_size[-3:]
    else:
        output_size = (1,) + x_shape[:1] + output_size[-3:]
    max_unpool_3d = MaxUnpool3D(ksize=kernel_size, strides=stride, pads=padding, output_shape=output_size,
                                data_format="NCDHW")

    if x_dim == 4:
        x = x.expand_dims(axis=0)
        indices = indices.expand_dims(axis=0)
        out = max_unpool_3d(x, indices)
        out = out.squeeze(0)
    else:
        out = max_unpool_3d(x, indices)
    return out


def binary_cross_entropy_with_logits(input, target, weight=None, pos_weight=None, reduction='mean'):
    r"""
    Adds sigmoid activation function to input `input` as logits, and uses the given logits to compute binary cross
    entropy between the `input` and the `target`.

    Sets input `input` as :math:`X`, input `target` as :math:`Y`, input `weight` as :math:`W`, output as :math:`L`.
    Then,

    .. math::

        \begin{array}{ll} \\
            p_{ij} = sigmoid(X_{ij}) = \frac{1}{1 + e^{-X_{ij}}} \\
            L_{ij} = -[Y_{ij}log(p_{ij}) + (1 - Y_{ij})log(1 - p_{ij})]
        \end{array}

    :math:`i` indicates the :math:`i^{th}` sample, :math:`j` indicates the category. Then,

    .. math::
        \ell(x, y) = \begin{cases}
        L, & \text{if reduction} = \text{'none';}\\
        \operatorname{mean}(L), & \text{if reduction} = \text{'mean';}\\
        \operatorname{sum}(L),  & \text{if reduction} = \text{'sum'.}
        \end{cases}

    :math:`\ell` indicates the method of calculating the loss. There are three methods:
    the first method is to provide the loss value directly,
    the second method is to calculate the average value of all losses,
    and the third method is to calculate the sum of all losses.

    This operator will multiply the output by the corresponding weight.
    The tensor :math:`weight` assigns different weights to each piece of data in the batch,
    and the tensor :math:`pos\_weight` adds corresponding weights to the positive examples of each category.

    In addition, it can trade off recall and precision by adding weights to positive examples.
    In the case of multi-label classification the loss can be described as:

    .. math::
        \begin{array}{ll} \\
            p_{ij,c} = sigmoid(X_{ij,c}) = \frac{1}{1 + e^{-X_{ij,c}}} \\
            L_{ij,c} = -[P_{c}Y_{ij,c} * log(p_{ij,c}) + (1 - Y_{ij,c})log(1 - p_{ij,c})]
        \end{array}

    where c is the class number (c>1 for multi-label binary classification, c=1 for single-label binary classification),
    n is the number of the sample in the batch and :math:`P_c` is the weight of the positive answer for the class c.
    :math:`P_c>1` increases the recall, :math:`P_c<1` increases the precision.

    Args:
        input (Tensor): Input `input`. Data type must be float16, float32 or bfloat16(only Atlas A2 series products
          are supported).
        target (Tensor): Ground truth label, has the same shape as `input`.
          Data type must be float16, float32 or bfloat16(only Atlas A2 series products
          are supported).
        weight (Tensor, optional): A rescaling weight applied to the loss of each batch element. It can be
          broadcast to a tensor with shape of `input`. Data type must be float16, float32 or bfloat16(only Atlas A2
          series products are supported).
          Default: ``None``, it equals to `weight` is a Tensor whose value is ``1``.
        pos_weight (Tensor, optional): A weight of positive examples. Must be a vector with length equal to the
          number of classes. It can be broadcast to a tensor with shape of `input`.
          Data type must be float16, float32 or bfloat16(only Atlas A2 series products are supported).
          Default: ``None``, it equals to `pos_weight` is a Tensor whose value is ``1``.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Scalar, if `reduction` is ``'none'``, it's a tensor with the same shape and type as input `input`.
        Otherwise, the output is a scalar.

    Raises:
        TypeError: If input `input`, `target`, `weight`, `pos_weight` is not Tensor.
        TypeError: If data type of input `input`, `target`, `weight`, `pos_weight` is not float16, float32 or bfloat16.
        TypeError: If data type of input `reduction` is not string.
        ValueError: If `weight` or `pos_weight` can not be broadcast to a tensor with shape of `input`.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'`` or ``'sum'``.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[-0.8, 1.2, 0.7], [-0.1, -0.4, 0.7]]), mindspore.float32)
        >>> target = Tensor(np.array([[0.3, 0.8, 1.2], [-0.6, 0.1, 2.2]]), mindspore.float32)
        >>> weight = Tensor(np.array([1.0, 1.0, 1.0]), mindspore.float32)
        >>> pos_weight = Tensor(np.array([1.0, 1.0, 1.0]), mindspore.float32)
        >>> output = ops.binary_cross_entropy_with_logits(input, target, weight, pos_weight)
        >>> print(output)
        0.3463612
    """

    bce_with_logits_loss_op = _get_cache_prim(NN_OPS.BCEWithLogitsLoss)(reduction)
    return bce_with_logits_loss_op(input, target, weight, pos_weight)


@_function_forbid_reuse
def dropout(input, p=0.5, training=True, seed=None):
    r"""
    During training, randomly zeroes some of the elements of the input tensor
    with probability `p` from a Bernoulli distribution. It plays the role of reducing neuron correlation and
    avoid overfitting. And the return will be multiplied by :math:`\frac{1}{1-p}` during training.
    During the reasoning, this operation returns the same Tensor as the `x`.

    .. warning::
        The Ascend backend does not support the reproducibility of random numbers, so
        the `seed` parameter has no effect.

    Args:
        input (Tensor): The input Tensor of shape :math:`(*, N)`, with data type of float16, float32 or float64.
        p (float, optional): The dropping rate, between 0 and 1, e.g. p = 0.1,
            means dropping out 10% of input units. Default: ``0.5`` .
        training (bool, optional): Apply dropout if is True. Default: ``True``.
        seed (int, optional): Seed is used as entropy source for Random number engines generating pseudo-random numbers.
            Default: ``None`` , which will be treated as ``0`` .

    Returns:
        - **output** (Tensor) - Zeroed tensor, with the same shape and data type as `input`.

    Raises:
        TypeError: If `p` is not a float.
        TypeError: If dtype of `input` is not float16, float32 or float64.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(((20, 16), (50, 50)), mindspore.float32)
        >>> output = ops.dropout(input, p=0.5)
        >>> print(output.shape)
        (2, 2)
    """
    check_bool_const(training, "training", "dropout")
    if training is False:
        return input
    keep_prob = 1 - p
    seed0, seed1 = _get_seed(seed, "dropout")
    dropout_op = P.Dropout(keep_prob=keep_prob, Seed0=seed0, Seed1=seed1)
    dropout_op = _set_prim_op_user_data(dropout_op, "random_cache", False)
    out, _ = dropout_op(input)
    return out


@_function_forbid_reuse
def dropout_ext(input, p=0.5, training=True, inplace=False):
    r"""
    During training, randomly zeroes some of the elements of the input tensor
    with probability `p` from a Bernoulli distribution. It plays the role of reducing neuron correlation and
    avoid overfitting. And the return will be multiplied by :math:`\frac{1}{1-p}` during training.
    During the reasoning, this operation returns the same Tensor as the `input`.

    Args:
        input (Tensor): The input Tensor of shape :math:`(*, N)`.
        p (float, optional): The dropping rate of input neurons, between 0 and 1, e.g. `p` = 0.1,
            means dropping out 10% of input neurons. Default: ``0.5`` .
        training (bool, optional): Apply dropout if it is ``True`` ,
            if it is ``False`` , the input is returned directly,
            and `p` is invalid. Default: ``True`` .
        inplace (bool, optional): If set to ``True`` , will do this operation in-place. Default: ``False`` .

    Returns:
        - **output** (Tensor) - Zeroed tensor, with the same shape and data type as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(((20, 16), (50, 50)), mindspore.float32)
        >>> output = ops.function.nn_func.dropout_ext(input, p=0.5)
        >>> print(output.shape)
        (2, 2)
    """
    seed, offset = default_generator._step(generator_step_)  # pylint: disable=protected-access
    return func_dropout_ext_op(input, p, training, inplace, seed, offset)


def dropout1d(input, p=0.5, training=True):
    r"""
    During training, randomly zeroes some channels of the input tensor with probability `p`
    from a Bernoulli distribution(For a 3-dimensional tensor with a shape of :math:`NCL`,
    the channel feature map refers to a 1-dimensional feature map with the shape of :math:`L`).

    For example, the :math:`j\_th` channel of the :math:`i\_th` sample in the batched input is a to-be-processed
    `1D` tensor input[i,j].
    Each channel will be zeroed out independently on every forward call which based on Bernoulli distribution
    probability `p`.

    The parper `Dropout: A Simple Way to Prevent Neural Networks from Overfitting
    <http://www.cs.toronto.edu/~rsalakhu/papers/srivastava14a.pdf>`_ mentioned this technology, And it is proved that
    it can effectively reduce over fitting and prevent neuronal coadaptation.
    For more details, refer to `Improving neural networks by preventing co-adaptation of feature detectors
    <https://arxiv.org/pdf/1207.0580.pdf>`_ .

    `dropout1d` can improve the independence between channel feature maps.

    Args:
        input (Tensor): A tensor with shape :math:`(N, C, L)` or :math:`(C, L)`, where `N` is the batch size, `C` is the
            number of channels, `L` is the feature length. The data type must be int8, int16, int32, int64, float16,
            float32 or float64.
        p (float, optional): The dropping probability of a channel, between 0 and 1, e.g. `p` = 0.8,
            which means an 80% chance of clearing. Default: ``0.5`` .
        training (bool, optional): Apply dropout if is True. Default: ``True`` .

    Returns:
        Tensor, output, with the same shape and data type as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If the data type of `p` is not float.
        ValueError: If `p` is out of the range `[0.0, 1.0]`.
        ValueError: If `input` shape is not `2D` or `3D`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.random.randn(4, 3), mindspore.float32)
        >>> output = ops.dropout1d(input_x, 0.5)
        >>> print(output.shape)
        (4, 3)
    """
    if not isinstance(p, float):
        raise TypeError(f"For dropout1d, 'p' must be float, but got type {type(p)}.")
    if p < 0 or p > 1:
        raise ValueError(f"For dropout1d, the 'p' must be a number in range [0, 1], but got {p}.")

    if not isinstance(input, Tensor):
        raise TypeError(f"For dropout1d, 'input' must be Tensor, but got type {type(input)}.")
    check_bool_const(training, "training", "dropout1d")
    if training is False:
        return input
    dropout_2d_op = NN_OPS.Dropout2D(1.0 - p)

    if len(input.shape) == 2:
        input = input.expand_dims(0)
        input = input.expand_dims(-1)
        out, _ = dropout_2d_op(input)
        out = out.squeeze(-1)
        out = out.squeeze(0)
    elif len(input.shape) == 3:
        input = input.expand_dims(-1)
        out, _ = dropout_2d_op(input)
        out = out.squeeze(-1)
    else:
        raise ValueError(f"For dropout1d, input shape should be 2D or 3D, but got {len(input.shape)}.")
    return out


def dropout2d(input, p=0.5, training=True):
    r"""
    During training, randomly zeroes some channels of the input tensor with probability `p`
    from a Bernoulli distribution(For a 4-dimensional tensor with a shape of :math:`NCHW`,
    the channel feature map refers to a 2-dimensional feature map with the shape of :math:`HW`).

    For example, the :math:`j\_th` channel of the :math:`i\_th` sample in the batched input is a to-be-processed
    `2D` tensor input[i,j].
    Each channel will be zeroed out independently on every forward call which based on Bernoulli distribution
    probability `p`.
    The parper `Dropout: A Simple Way to Prevent Neural Networks from Overfitting
    <http://www.cs.toronto.edu/~rsalakhu/papers/srivastava14a.pdf>`_ mentioned this technology, And it is proved that
    it can effectively reduce over fitting and prevent neuronal coadaptation.
    For more details, refer to `Improving neural networks by preventing co-adaptation of feature detectors
    <https://arxiv.org/pdf/1207.0580.pdf>`_ .

    `dropout2d` can improve the independence between channel feature maps.

    Args:
        input (Tensor): A `4D` tensor with shape :math:`(N, C, H, W)`, where `N` is the batch size, `C` is the number
            of channels, `H` is the feature height, and `W` is the feature width. The data type must be int8,
            int16, int32, int64, float16, float32 or float64.
        p (float): The dropping probability of a channel. The range is [0.0, 1.0], e.g. `p` = 0.8,
            which means dropping out 80% of channels. Default: ``0.5`` .
        training(bool): If `training` is True, applying dropout, otherwise, not applying. Default: ``True`` .

    Returns:
        Tensor, output, with the same shape and data type as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not int8, int16, int32, int64, float16, float32 or float64.
        TypeError: If the data type of `p` is not float.
        ValueError: If `p` is out of the range `[0.0, 1.0]`.
        ValueError: If `input` shape is not `4D`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.ones([2, 1, 2, 3]), mindspore.float32)
        >>> output = ops.dropout2d(input, 0.5)
        >>> print(output.shape)
        (2, 1, 2, 3)
    """
    check_bool_const(training, "training", "dropout2d")
    if training is False:
        return input
    dropout_2d_op = NN_OPS.Dropout2D(1.0 - p)
    out, _ = dropout_2d_op(input)
    return out


def dropout3d(input, p=0.5, training=True):
    r"""
    During training, randomly zeroes some channels of the input tensor
    with probability `p` from a Bernoulli distribution(For a 5-dimensional tensor
    with a shape of :math:`NCDHW`, the channel feature map refers to a 3-dimensional
    feature map with a shape of :math:`DHW`).

    For example, the :math:`j\_th` channel of the :math:`i\_th` sample in the batched input is a to-be-processed
    `3D` tensor input[i,j].
    Each channel will be zeroed out independently on every forward call which based on Bernoulli distribution
    probability `p`.

    `dropout3d` can improve the independence between channel feature maps.

    Args:
        input (Tensor): A `5D` tensor with shape :math:`(N, C, D, H, W)`, where `N` is the batch size, `C` is the number
            of channels, `D` is the feature depth, `H` is the feature height, and `W` is the feature width.
            The data type must be int8, int16, int32, int64, float16, float32 or float64.
        p (float): The dropping probability of a channel, between 0 and 1, e.g. `p` = 0.8,
            which means dropping out 80% of channels. Default: ``0.5`` .
        training(bool): If `training` is True, applying dropout, otherwise, not applying. Default: ``True`` .

    Returns:
        Tensor, output, with the same shape and data type as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not int8, int16, int32, int64, float16, float32 or float64.
        TypeError: If the data type of `p` is not float.
        ValueError: If `p` is out of the range `[0.0, 1.0]`.
        ValueError: If `input` shape is not 5D.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.ones([2, 1, 2, 1, 2]), mindspore.float32)
        >>> output = ops.dropout3d(input, 0.5)
        >>> print(output.shape)
        (2, 1, 2, 1, 2)
    """
    check_bool_const(training, "training", "dropout3d")
    if training is False:
        return input
    dropout_3d_op = NN_OPS.Dropout3D(1.0 - p)
    out, _ = dropout_3d_op(input)
    return out


@_primexpr
def _check_float_range_inc_neither(arg_value, lower_limit, upper_limit, arg_name=None, prim_name=None):
    """
    Method for checking whether input value is in float range inc neither.
    """
    return validator.check_float_range(arg_value, lower_limit, upper_limit, validator.INC_NEITHER, arg_name, prim_name)


def _check_fractional_output_size_ratio(output_size, output_ratio, cls_name):
    """Internal function, used to check whether fractional_max_pool can specify the output shape."""
    if output_ratio is None and output_size is None:
        raise ValueError(f"For {cls_name}, 'output_size' and 'output_ratio' can not be None"
                         f"at the same time, but got {output_ratio} and {output_size} .")


def fractional_max_pool2d(input, kernel_size, output_size=None, output_ratio=None, return_indices=False,
                          _random_samples=None):
    r"""
    Applies the 2D FractionalMaxPool operation over `input`. The output Tensor shape can be determined by either
    `output_size` or `output_ratio`, and the step size is determined by `_random_samples`. `output_size` will take
    effect when `output_size` and `output_ratio` are set at the same time.
    And `output_size` and `output_ratio` can not be ``None`` at the same time.

    Refer to the paper `Fractional MaxPooling by Ben Graham <https://arxiv.org/abs/1412.6071>`_  for more details.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C, H_{in}, W_{in})` or :math:`(C, H_{in}, W_{in})`,
            with float16, float32, float64, int32, int64 data type.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value,
            is an int number that represents height and width of the kernel, or a tuple
            of two int numbers that represent height and width respectively.
            The value must be a positive integer.
        output_size (Union[int, tuple[int]], optional): The shape of the target `output_size`,
            is an int number that represents height and width, or a tuple
            of two int numbers that represent height and width respectively.
            The value must be a positive integer.
            Default: ``None``.
        output_ratio (Union[float, tuple[float]], optional): The ratio of target output shape to input shape.
            Specifying the size of the output tensor by using a ratio of the input size.
            Data type: float16, float32, double, and value is between (0, 1).
            Default: ``None``.
        return_indices (bool, optional): Whether to return the indices of max value. Default: ``False``.
        _random_samples (Tensor, optional): The random step of fractional_max_pool2d, which is a 3D tensor.
            Tensor of data type: float16, float32, double, and value is between [0, 1).
            Supported shape :math:`(N, C, 2)` or :math:`(1, C, 2)`.
            Default: ``None``, the values of `_random_samples`
            will be randomly distributed using uniform distribution over an interval [0,1).

    Returns:
        - **y** (Tensor) - Has the same type as the `input`.
          Has the shape :math:`(N, C, H_{out}, W_{out})` or :math:`(C, H_{out}, W_{out})` ,
          where :math:`(H_{out}, W_{out})` = `output_size`
          or :math:`(H_{out}, W_{out})` = `output_ratio` * :math:`(H_{in}, W_{in})`.

        - **argmax** (Tensor) - The indices along with the outputs, which is a Tensor, with the same shape as the
          `y` and int64 data type. It will output only when `return_indices` is True.

    Raises:
        TypeError: If data type of `input` is not one of the following: float16, float32, float64, int32, int64.
        TypeError: If data type of `_random_samples` is not one of the following: float16, float32, float64.
        ValueError: If `kernel_size` is not a number and `kernel_size` is not a tuple of length 2.
        ValueError: If `output_size` is not a number and `output_size` is not a tuple of length 2.
        ValueError: If the sum of `kernel_size` , `output_size` and -1 is larger than the corresponding
                    dimension of `input`.
        ValueError: If the dimension of `_random_samples` is not 3.
        ValueError: if `output_size` and `output_ratio` are None at the same time.
        ValueError: If the first dimension size of `input` and `_random_samples` is not equal.
        ValueError: If the second dimension size of `input` and `_random_samples` is not equal.
        ValueError: If the third dimension size of `_random_samples` is not 2.

    Supported Platforms:
        ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> input = Tensor(np.array([0.3220, 0.9545, 0.7879, 0.0975, 0.3698,
        ...                            0.5135, 0.5740, 0.3435, 0.1895, 0.8764,
        ...                            0.9581, 0.4760, 0.9014, 0.8522, 0.3664,
        ...                            0.4980, 0.9673, 0.9879, 0.6988, 0.9022,
        ...                            0.9304, 0.1558, 0.0153, 0.1559, 0.9852]).reshape([1, 1, 5, 5]), mstype.float32)
        >>> _random_samples = Tensor(np.array([[[0.8, 0.8]]]), mstype.float32)
        >>> y, argmax = ops.fractional_max_pool2d(input, kernel_size=2, output_size=(2, 2),
        ...                                       _random_samples=_random_samples, return_indices=True)
        >>> print(y)
        [[[[0.9545 0.8764]
           [0.9673 0.9852]]]]
        >>> print(argmax)
        [[[[ 1  9]
           [16 24]]]]
        >>> y, argmax = ops.fractional_max_pool2d(input, kernel_size=2, output_ratio=(0.5, 0.5),
        ...                                       _random_samples=_random_samples, return_indices=True)
        >>> print(y)
        [[[[0.9545 0.8764]
           [0.9673 0.9852]]]]
        >>> print(argmax)
        [[[[ 1  9]
           [16 24]]]]
    """
    _check_fractional_output_size_ratio(output_size, output_ratio, "fractional_max_pool2d")
    _check_value_type("return_indices", return_indices, [bool], "fractional_max_pool2d")
    dim_flag = False
    if input.ndim == 3:
        input = input.expand_dims(axis=0)
        dim_flag = True
    if _random_samples is None:
        if input.dtype in mstype.float_type:
            _random_samples = ops.rand(input.shape[0], input.shape[1], 2, dtype=input.dtype)
        else:
            _random_samples = ops.rand(input.shape[0], input.shape[1], 2)
    if output_size is None:
        if isinstance(output_ratio, (float, int)):
            _check_value_type("output_ratio", output_ratio, [float], "fractional_max_pool2d")
            output_ratio = (output_ratio, output_ratio)
        _check_float_range_inc_neither(output_ratio[0], 0.0, 1.0, "output_ratio[0]", "fractional_max_pool2d")
        _check_float_range_inc_neither(output_ratio[1], 0.0, 1.0, "output_ratio[1]", "fractional_max_pool2d")
        output_size = (int(input.shape[-2] * output_ratio[0]), int(input.shape[-1] * output_ratio[1]))
    fractional_max_pool = FractionalMaxPoolWithFixedKsize(kernel_size, output_size)
    output = fractional_max_pool(input, _random_samples)
    if dim_flag:
        output = output[0].squeeze(axis=0), output[1].squeeze(axis=0)
    if return_indices:
        return output
    return output[0]


def fractional_max_pool3d(input, kernel_size, output_size=None, output_ratio=None, return_indices=False,
                          _random_samples=None):
    r"""
    Applies the 3D FractionalMaxPool operation over `input`. The output Tensor shape can be determined by either
    `output_size` or `output_ratio`, and the step size is determined by `_random_samples`. `output_size` will take
    effect when `output_size` and `output_ratio` are set at the same time.
    And `output_size` and `output_ratio` can not be ``None`` at the same time.

    Refer to the paper `Fractional MaxPooling by Ben Graham <https://arxiv.org/abs/1412.6071>`_  for more details.

    The input and output data format can be "NCDHW". N is the batch size, C is the number of channels,
    D the feature depth, H is the feature height, and W is the feature width.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input of FractionalMaxPool3d, which is a 4D or 5D tensor.
            Tensor of data type: float16, float32, double.
            Supported shape :math:`(N, C, D_{in}, H_{in}, W_{in})` or :math:`(C, D_{in}, H_{in}, W_{in})`.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value,
            is an int number that represents depth, height and width of the kernel, or a tuple
            of three int numbers that represent depth, height and width respectively.
            The value must be a positive integer.
        output_size (Union[int, tuple[int]], optional): The shape of the target `output_size`,
            is an int number that represents depth, height and width, or a tuple
            of three int numbers that represent depth, height and width respectively.
            The value must be a positive integer.
            Default: ``None`` .
        output_ratio (Union[float, tuple[float]], optional): The ratio of target output shape to input shape.
            Specifying the size of the output tensor by using a ratio of the input size.
            Data type: float16, float32, double, and value is between (0, 1).
            Default: ``None`` .
        return_indices (bool, optional): Whether to return the indices of max value. Default: ``False`` .
        _random_samples (Tensor, optional): The random step of fractional_max_pool3d, which is a 3D tensor.
            Tensor of data type: float16, float32, double, and value is between [0, 1).
            Supported shape :math:`(N, C, 3)` or :math:`(1, C, 3)` . Default: ``None``, the values of `_random_samples`
            will be randomly distributed using uniform distribution over an interval [0,1).

    Returns:
        - **y** (Tensor) - A tensor, the output of FractionalMaxPool3d.
          Has the same data type with `input`.
          Has the shape :math:`(N, C, D_{out}, H_{out}, W_{out})` or :math:`(C, D_{out}, H_{out}, W_{out})` ,
          where :math:`(D_{out}, H_{out}, W_{out})` = `output_size`
          or :math:`(D_{out}, H_{out}, W_{out})` = `output_ratio` * :math:`(D_{in}, H_{in}, W_{in})` .

        - **argmax** (Tensor) - The indices along with the outputs, which is a Tensor, with the same shape as the
          `y` and int32 data type. It will output only when `return_indices` is True.

    Raises:
        TypeError: If `input` is not a 4D or 5D tensor.
        TypeError: If `_random_samples` is not a 3D tensor.
        TypeError: If data type of `input` is not float16, float32, double, int32, int64.
        TypeError: If dtype of `_random_samples` is not float16, float32, double.
        TypeError: If dtype of `argmax` is not int32, int64.
        TypeError: if _random_samples to have the different dtypes as input.
        ValueError: If `output_size` is a tuple and if `output_size` length is not 3.
        ValueError: If `kernel_size` is a tuple and if `kernel_size` length is not 3.
        ValueError: If numbers in `output_size` or `kernel_size` is not positive.
        ValueError: if `output_size` and `output_ratio` are None at the same time.
        ValueError: If the first dimension size of `input` and `_random_samples` is not equal.
        ValueError: If the second dimension size of `input` and `_random_samples` is not equal.
        ValueError: If the third dimension size of `_random_samples` is not 3.

    Supported Platforms:
        ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> x = Tensor(np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        ...            .reshape([1, 1, 2, 2, 4]), mstype.float32)
        >>> _random_samples = Tensor(np.array([0.7, 0.7, 0.7]).reshape([1, 1, 3]), mstype.float32)
        >>> output, argmax = ops.fractional_max_pool3d(x, kernel_size=(1, 1, 1), output_size=(1, 1, 3),
        ...                                            _random_samples=_random_samples, return_indices=True)
        >>> print(output)
        [[[[[13. 14. 16.]]]]]
        >>> print(argmax)
        [[[[[12 13 15]]]]]
        >>> output, argmax = ops.fractional_max_pool3d(x, kernel_size=(1, 1, 1), output_ratio=(0.5, 0.5, 0.5),
        ...                                            _random_samples=_random_samples, return_indices=True)
        >>> print(output)
        [[[[[13. 16.]]]]]
        >>> print(argmax)
        [[[[[12 15]]]]]
    """
    _check_fractional_output_size_ratio(output_size, output_ratio, "fractional_max_pool3d")
    _check_value_type("return_indices", return_indices, [bool], "fractional_max_pool3d")
    if _random_samples is None:
        n = 1 if input.ndim == 4 else input.shape[0]
        if input.dtype in mstype.float_type:
            _random_samples = ops.rand(n, input.shape[-4], 3, dtype=input.dtype)
        else:
            _random_samples = ops.rand(n, input.shape[-4], 3)
    if input.ndim == 4:
        _random_samples = _random_samples.transpose(1, 0, 2)
    if output_size is None:
        if isinstance(output_ratio, (float, int)):
            _check_value_type("output_ratio", output_ratio, [float], "fractional_max_pool3d")
            output_ratio = (output_ratio, output_ratio, output_ratio)
        _check_float_range_inc_neither(output_ratio[0], 0.0, 1.0, "output_ratio[0]", "fractional_max_pool3d")
        _check_float_range_inc_neither(output_ratio[1], 0.0, 1.0, "output_ratio[1]", "fractional_max_pool3d")
        _check_float_range_inc_neither(output_ratio[2], 0.0, 1.0, "output_ratio[2]", "fractional_max_pool3d")
        output_size = (int(input.shape[-3] * output_ratio[0]), int(input.shape[-2] * output_ratio[1]),
                       int(input.shape[-1] * output_ratio[2]))
    if input.dtype != _random_samples.dtype:
        raise TypeError(f"For 'fractional_max_pool3d', 'input' and '_random_samples' must be same dtype, "
                        f"but got Tensor[{input.dtype}] and Tensor[{_random_samples.dtype}].")
    fractional_max_pool = FractionalMaxPool3DWithFixedKsize(kernel_size, output_size)
    output = fractional_max_pool(input, _random_samples)
    if return_indices:
        return output
    return output[0]


def kl_div(logits, labels, reduction='mean'):
    r"""
    Computes the Kullback-Leibler divergence between the logits and the labels.

    For input tensors :math:`x` and :math:`target` with the same shape, the updating formulas of KLDivLoss algorithm are
    as follows,

    .. math::
        L(x, target) = target \cdot (\log target - x)

    Then,

    .. math::
        \ell(x, target) = \begin{cases}
        L(x, target), & \text{if reduction} = \text{'none';}\\
        \operatorname{mean}(L(x, target)), & \text{if reduction} = \text{'mean';}\\
        \operatorname{sum}(L(x, target)) / x.\operatorname{shape}[0], & \text{if reduction} = \text{'batchmean';}\\
        \operatorname{sum}(L(x, target)),  & \text{if reduction} = \text{'sum'.}
        \end{cases}

    where :math:`x` represents `logits`.
    :math:`target` represents `labels`.
    :math:`\ell(x, target)` represents `output`.

    Note:
        - Currently it does not support float64 input on `Ascend`.
        - The output aligns with the mathematical definition of Kullback-Leibler divergence
          only when `reduction` is set to ``'batchmean'``.

    Args:
        logits (Tensor): The input Tensor. The data type must be float16, float32 or float64.
        labels (Tensor): The label Tensor which has the same shape and data type as `logits`.
        reduction (str): Specifies the reduction to be applied to the output.
            Its value must be one of ``'none'`` , ``'mean'`` , ``'batchmean'`` or ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.
            - ``'batchmean'``: the summed output elements divided by batch size.

    Returns:
        Tensor or Scalar, if `reduction` is ``'none'``, then output is a tensor and has the same shape as `logits`.
        Otherwise, it is a scalar.

    Raises:
        TypeError: If `reduction` is not a str.
        TypeError: If neither `logits` nor `labels` is a Tensor.
        TypeError: If dtype of `logits` or `labels` is not the supported type.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> logits = Tensor(np.array([0.2, 0.7, 0.1]), mindspore.float32)
        >>> labels = Tensor(np.array([0., 1., 0.]), mindspore.float32)
        >>> output = mindspore.ops.kl_div(logits, labels, 'mean')
        >>> print(output)
        -0.23333333
    """
    if not isinstance(reduction, str):
        raise ValueError("For 'kl_div', the 'reduction' must be str and must be in "
                         f"'['none', 'mean', 'batchmean', 'sum']', but got '{reduction}'.")

    if reduction == 'batchmean':
        kl_div_sum = _get_cache_prim(P.KLDivLoss)(reduction='sum')(logits, labels)
        shape = shape_(logits)
        batch_size = shape[0]
        return kl_div_sum / batch_size

    if reduction == 'mean':
        kl_div_sum = _get_cache_prim(P.KLDivLoss)(reduction='sum')(logits, labels)
        shape = shape_(logits)
        total_size = 1
        for dim in shape:
            total_size = total_size * dim
        return kl_div_sum / total_size

    return _get_cache_prim(P.KLDivLoss)(reduction=reduction)(logits, labels)


def kl_div_ext(input, target, reduction='mean', log_target=False):
    r"""
    Computes the Kullback-Leibler divergence between the `input` and the `target`.

    For tensors of the same shape :math:`x` and :math:`y`,
    the updating formulas of KLDivLoss algorithm are as follows,

    .. math::
        L(x, y) = y \cdot (\log y - x)

    Then,

    .. math::
        \ell(x, y) = \begin{cases}
        L(x, y), & \text{if reduction} = \text{'none';}\\
        \operatorname{mean}(L(x, y)), & \text{if reduction} = \text{'mean';}\\
        \operatorname{sum}(L(x, y)) / x.\operatorname{shape}[0], & \text{if reduction} = \text{'batchmean';}\\
        \operatorname{sum}(L(x, y)),  & \text{if reduction} = \text{'sum'.}
        \end{cases}

    where :math:`x` represents `input`, :math:`y` represents `target`, and :math:`\ell(x, y)` represents the output.

    Note:
        The output aligns with the mathematical definition of Kullback-Leibler divergence
        only when `reduction` is set to ``'batchmean'``.

    Args:
        input (Tensor): The input Tensor. The data type must be float16, float32 or bfloat16(only supported by Atlas A2
            training series products).
        target (Tensor): The target Tensor which has the same type as `input`. The shapes of `target` and `input`
            should be broadcastable.
        reduction (str, optional): Specifies the reduction to be applied to the output. Default: ``'mean'``.
        log_target (bool, optional): Specifies whether `target` is passed in the log space. Default: ``False``.

    Returns:
        Tensor, has the same dtype as `input`. If `reduction` is ``'none'``, then output has the shape as broadcast
        result of the `input` and `target`. Otherwise, it is a scalar Tensor.

    Raises:
        TypeError: If neither `input` nor `target` is a Tensor.
        TypeError: If dtype of `input` or `target` is not float16, float32 or bfloat16.
        TypeError: If dtype of `target` is not the same as `input`.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``, ``'batchmean'``.
        ValueError: If shapes of `target` and `input` can not be broadcastable.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> import numpy as np
        >>> input = ms.Tensor(np.array([[0.5, 0.5], [0.4, 0.6]]), ms.float32)
        >>> target = ms.Tensor(np.array([[0., 1.], [1., 0.]]), ms.float32)
        >>> output = ops.kl_div_ext(input, target, reduction='mean', log_target=False)
        >>> print(output)
        -0.225
    """
    if reduction == 'batchmean':
        reduced = kl_div_op(input, target, 'sum', log_target)
    else:
        reduced = kl_div_op(input, target, reduction, log_target)

    if reduction == 'batchmean' and input.ndim != 0:
        reduced = divs_op(reduced, input.shape[0])

    return reduced


@constexpr
def _check_axis_in_range(axis, ndim):
    """Checks axes are with the bounds of ndim"""
    if not isinstance(axis, int):
        raise TypeError(f'The dims must be integers, but got {type(axis)}')
    if not -ndim <= axis < ndim:
        raise ValueError(f"The 'axis' must be in the range of [-{ndim}, {ndim}), but got {axis}.")
    return axis % ndim


@constexpr
def _check_axis_valid(axes, ndim):
    """
    Checks axes are valid given ndim, and returns axes that can be passed
    to the built-in operator (non-negative, int or tuple)
    """
    if axes is None:
        raise ValueError(f"The parameter dims can not be None.")
    if isinstance(axes, (tuple, list)):
        axes = tuple(map(lambda x: _check_axis_in_range(x, ndim), axes))
        if any(axes.count(el) > 1 for el in axes):
            raise ValueError(f"The element of parameter 'dims' can not be duplicate, but got {axes}.")
        return axes
    raise ValueError(f"The parameter dims must be tuple of ints, but got {type(axes)}")


def _get_flip_start(ndim, shape, axes):
    """Calculate the start index of flip"""
    return tuple([shape[i] - 1 if i in axes else 0 for i in range(ndim)])


def _get_flip_end(ndim, shape, axes):
    """Calculate the end index of flip"""
    return tuple([-shape[i] - 1 if i in axes else shape[i] + 1 for i in range(ndim)])


@constexpr
def _get_flip_strides(ndim, axes):
    """Calculate the strides of flip"""
    return tuple([-1 if i in axes else 1 for i in range(ndim)])


def _is_shape_empty(shp):
    """Check whether shape contains zero"""
    if isinstance(shp, int):
        return shp == 0
    return ops.shape_mul(shp) == 0


def _check_input_tensor(arg_name, *tensors):
    """Check whether the input is tensor"""
    for tensor in tensors:
        if not isinstance(tensor, Tensor):
            raise TypeError(f"For '{arg_name}', the input must be Tensor, but got {ops.typeof(tensor)}")
    return True


def flip(input, dims):
    """
    Reverses elements in a tensor along the given dims.

    Args:
        input (Tensor): The input tensor.
        dims (Union[list[int], tuple[int]]): The dimension to flip.

    Returns:
        Tensor

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> input = mindspore.tensor(mindspore.ops.arange(1, 9).reshape((2, 2, 2)))
        >>> output = mindspore.ops.flip(input, (0, 2))
        >>> print(output)
        [[[6 5]
          [8 7]]
         [[2 1]
          [4 3]]]
    """
    res = reverse_v2_impl(input, dims)
    return res


def flipud(input):
    """
    Flip the input tensor in up/down direction.

    Args:
        input (Tensor): The input tensor, the dimension must be at least 2.

    Returns:
        Tensor

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> input = mindspore.tensor(mindspore.ops.arange(1, 9).reshape((2, 2, 2)))
        >>> output = mindspore.ops.flipud(input)
        >>> print(output)
        [[[5 6]
          [7 8]]
         [[1 2]
          [3 4]]]
    """
    return flip(input, (0,))


def fliplr(input):
    """
    Flip the input tensor in left/right direction.

    Args:
        input (Tensor): The input tensor, the dimension must be at least 2.

    Returns:
        Tensor

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> input = mindspore.tensor(mindspore.ops.arange(1, 9).reshape((2, 2, 2)))
        >>> output = mindspore.ops.fliplr(input)
        >>> print(output)
        [[[3 4]
          [1 2]]
         [[7 8]
          [5 6]]]
    """
    return flip(input, (1,))


def is_floating_point(input):
    """
    If the data type of the tensor is a floating point data type, return True. Otherwise return False.

    Args:
        input (Tensor): The input Tensor.

    Returns:
        Bool

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> input = mindspore.tensor([False, 0j, 1, 2.1, 1+2j], mindspore.float64)
        >>> mindspore.ops.is_floating_point(input)
        True
        >>>
        >>> input = mindspore.tensor([False, 0j, 1, 2.1, 1+2j], mindspore.float32)
        >>> mindspore.ops.is_floating_point(input)
        True
        >>>
        >>> input = mindspore.tensor([False, 0j, 1, 2.1, 1+2j], mindspore.float16)
        >>> mindspore.ops.is_floating_point(input)
        True
        >>>
        >>> input = mindspore.tensor([False, 0j, 1, 2.1, 1+2j], mindspore.int32)
        >>> mindspore.ops.is_floating_point(input)
        False
    """
    return input.dtype in mstype.float_type


def _is_dim_unknown(shape):
    return isinstance(shape, tuple) and -2 in shape


@_primexpr
def _interploate_make_tuple(rank, value):
    """
    make tuple in dynamic scenarios
    """
    s = tuple_to_tensor_((rank,), mstype.int32)
    v = None
    if isinstance(value, int):
        v = F.scalar_to_tensor(value, mstype.int64)
    else:
        v = F.scalar_to_tensor(value, mstype.float32)
    t = fillv2_(s, v)
    out = tensor_to_tuple_(t)
    return out


@_primexpr
def _interpolate_scale_factor_convert_size(shape, scale_factor):
    """
    convert scale_factor to size
    """
    x = tuple_to_tensor_(shape[2:], mstype.int64)
    y = tuple_to_tensor_(scale_factor, mstype.float32)
    t = x * y
    t = ops.TruncateDiv()(t, Tensor(1))
    t = ops.cast(t, mstype.int64)
    return tensor_to_tuple_(t)


def _interpolate_size_check_with_rank(size, input_rank):
    """
    size rank check
    """
    if len(size) != input_rank - 2:
        raise ValueError(
            f"For 'interpolate', 'input' and 'size' must have the same spatial dimensions, "
            f"but got 'input' is {input_rank - 2}D, 'size' is {len(size)}D")


def _interpolate_scale_factor_check_with_rank(scale_factor, input_rank):
    """
    scale_factor rank check
    """
    if len(scale_factor) != input_rank - 2:
        raise ValueError(
            f"For 'interpolate', 'input' and 'scale_factor' must have the same spatial dimensions, "
            f"but got 'input' is {input_rank - 2}D, 'scale_factor' is {len(scale_factor)}D"
        )


def _interpolate_mode_check(mode, supported_dict):
    """
    mode check
    """
    if isinstance(mode, list) or mode not in supported_dict:
        raise ValueError(
            f"For 'interpolate', 'mode' must be in '{list(supported_dict)}', but got {mode}"
        )


def _interpolate_rank_check(input_rank, mode, supported_dict):
    """
    rank check
    """
    if input_rank not in supported_dict.get(mode):
        raise ValueError(
            f"For 'interpolate', {mode} only support '{list(supported_dict.get(mode, {}))}'D, but got {input_rank}D"
        )


def _interpolate_scale_factor_check(scale_factor, mode, rank, supported_dict):
    """
    scale_factor check
    """
    if scale_factor is not None and "scale_factor" not in supported_dict.get(
            mode, {}).get(rank):
        raise ValueError(
            f"For 'interpolate', 'scale_factor' option cannot currently be set with the "
            f"mode = {mode} and dim = {rank}D.")


def _interpolate_align_corners_mode_check(rank, mode, supported_dict):
    """
    align_corners check
    """
    if "align_corners" not in supported_dict.get(mode, {}).get(rank):
        raise ValueError(
            f"For 'interpolate', 'align_corners' option cannot currently be set with the "
            f"mode = {mode}, and dim = {rank}D")


def interpolate(input,
                size=None,
                scale_factor=None,
                mode="nearest",
                align_corners=None,
                recompute_scale_factor=None):
    r"""
    Samples the input Tensor to the given size or scale_factor by using one of the interpolate algorithms.

    Args:
        input (Tensor): Tensor to be resized.
            Input tensor must be a 3-D, 4-D, or 5-D tensor with shape
            :math:`(N, C, [optional D], [optional H], W)` , with data type of float.
        size (Union[int, tuple[int], list[int]], optional): The target size.
            If size is a tuple or list, its length should be the same as the number of dimensions in input
            after removing the first two dimensions N, C.
            One and only one of size and scale_factor can be set to None. Default: ``None`` .
        scale_factor (Union[float, tuple[float], list[float]], optional): The scale factor of new size of the tensor.
            If scale_factor is a tuple or list, its length should be the same as the number of dimensions in input
            after removing the first two dimensions N, C.
            One and only one of size and scale_factor can be set to None. Default: ``None`` .
        mode (str, optional): The sampling algorithm. Default: ``"nearest"`` .
            One of the following sampling methods can be used:

            - 'nearest': the nearest neighbours interpolation.
            - 'linear': Linear interpolation, 3D only.
            - 'bilinear': Bilinear interpolation, 4D only.
            - 'trilinear': Trilinear interpolation, 5D only.
            - 'bicubic': Double trilinear interpolation, 4D only.
            - 'area': area interpolation.
            - 'nearest-exact': matches Scikit-Image and PIL nearest neighbours interpolation algorithms and fixes
              knows issues with `nearest`, for 3D and 4D.

        align_corners (bool, optional): Whether to use corner alignment for coordinate mapping.
            Assuming a transformation is
            applied to the input Tensor along the x-axis, the specific calculation formula is as follows:

            .. code-block::

                ori_i = new_length != 1 ? new_i * (ori_length - 1) / (new_length - 1) : 0   # 'align_corners' = True

                ori_i = new_length > 1 ? (new_i + 0.5) * ori_length / new_length - 0.5 : 0  # 'align_corners' = False

            Among them, :math:`ori\_length` and :math:`new\_length` represent the length of the Tensor before and after
            transformation along the x-axis respectively; :math:`new\_i` represents the coordinate of the i-th element
            along the x-axis after transformation; :math:`ori\_i` represents
            the corresponding coordinate of the original
            data along the x-axis.

            This is only valid for ``'linear'``, ``'bilinear'``, or ``'bicubic'`` modes. Default: ``False`` .
        recompute_scale_factor (bool, optional): Recalculate `scale_factor`.

            - If True, the parameter `size` will be calculated using the value of the `scale_factor`,
              and finally scaled using the value of `size`.
            - If False, the value of `size` or `scale_factor` will be used for direct interpolation. Default: ``None`` .

    .. note::
        The 'nearest-exact' mode is the same as the nearest-neighbor interpolation algorithm used in
        scikit-image and PIL. The 'nearest' mode produces the same results as the INTER_NEAREST interpolation
        algorithm used in OpenCV.

    Args Support List and Supported Platforms:

    +---------------+-----------+---------------+--------------+----------------+
    | mode          | input.dim | align_corners | scale_factor | device         |
    +===============+===========+===============+==============+================+
    | nearest       | 3         | \-            | ×            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 4         | \-            | ×            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 5         | \-            | √            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    | linear        | 3         | √             | ×            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    | bilinear      | 4         | √             | ×            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    | bicubic       | 4         | √             | ×            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    | area          | 3         | \-            | √            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 4         | \-            | √            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 5         | \-            | √            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+
    | nearest-exact | 3         | \-            | ×            | Ascend,CPU     |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 4         | \-            | ×            | Ascend,CPU     |
    +---------------+-----------+---------------+--------------+----------------+
    | trilinear     | 5         | √             | √            | Ascend,GPU,CPU |
    +---------------+-----------+---------------+--------------+----------------+

    - `-` indicates that there is no such parameter.
    - `×` indicates that this parameter is not currently supported.
    - `√` indicates that this parameter is supported.

    Returns:
        Tensor, resized, whose dimensions and dtype are the same as `input`.

    Raises:
        TypeError: `input` is not a Tensor.
        ValueError: Both `size` and `scale_factor` are not empty.
        ValueError: Both `size` and `scale_factor` are empty.
        ValueError: When `size` is a tuple or list, its length is not equal to `input.ndim - 2`.
        ValueError: When `scale_factor` is a tuple or list, its length is not equal to `input.ndim - 2`.
        ValueError: `mode` is not in the list of supported modes.
        ValueError: `input.ndim` is not in the list of supported dimensions for the corresponding mode.
        ValueError: `size` is not empty, `recompute_scale_factor` is not empty.
        ValueError: `scale_factor` is not in the corresponding list of supported values.
        ValueError: `align_corners` is not in the corresponding list of supported values.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([[[1, 2, 3], [4, 5, 6]]], mindspore.float32)
        >>> output = ops.interpolate(input, size=(6,), mode='nearest')
        >>> print(output)
        [[[1. 1. 2. 2. 3. 3.]
          [4. 4. 5. 5. 6. 6.]]]
    """

    def run_nearest(x, size, align_corners=None, scale_factor=None):
        # 3D 4D use ResizeNearestNeighborV2, 5D use UpsampleNearest3D
        x_rank = F.rank(x)
        if size is not None and x_rank == 3:
            t1 = seq.TupleToTensor()(size[:1], mstype.int32)
            t2 = Tensor([1], mstype.int32)
            size = F.concat([t1, t2])
            x = x.unsqueeze(-1)
            x = _get_cache_prim(P.ResizeNearestNeighborV2)()(
                x, size)
            x = _get_cache_prim(P.Squeeze)(-1)(x)
        elif size is not None and x_rank == 4:
            size = seq.TupleToTensor()(size[:2], mstype.int32)
            x = _get_cache_prim(P.ResizeNearestNeighborV2)()(
                x, size)
        else:
            x = _get_cache_prim(P.UpsampleNearest3D)()(x, size, scale_factor)
        return x

    def run_linear(x, size, align_corners=None, scale_factor=None):
        coordinate_transformation_mode = "align_corners" if align_corners else "half_pixel"
        resize = _get_cache_prim(
            P.image_ops.ResizeLinear1D)(coordinate_transformation_mode)
        return resize(x, size)

    def run_bilinear(x, size, align_corners=None, scale_factor=None):
        resize = _get_cache_prim(P.ResizeBilinearV2)(align_corners,
                                                     not align_corners)
        return resize(x, size)

    def run_trilinear(x, size, align_corners=None, scale_factor=None):
        resize = _get_cache_prim(
            P.nn_ops.UpsampleTrilinear3D)(align_corners=align_corners)
        return resize(x, size, scale_factor)

    def run_bicubic(x, size, align_corners=None, scale_factor=None):
        resize = _get_cache_prim(P.image_ops.ResizeBicubic)(
            align_corners=align_corners, half_pixel_centers=not align_corners)
        size = seq.TupleToTensor()(size, mstype.int32)
        x = resize(x, size)
        return x

    def run_area(x, size, align_corners=None, scale_factor=None):
        x_rank = F.rank(x)
        if x_rank == 3:
            x = ops.adaptive_avg_pool1d(x, size[0])
        elif x_rank == 4:
            x = ops.adaptive_avg_pool2d(x, tuple(size))
        else:
            x = ops.adaptive_avg_pool3d(x, tuple(size))
        return x

    def run_nearest_exact(x, size, align_corners=None, scale_factor=None):
        x_rank = F.rank(x)
        if x_rank == 3:
            size = seq.TupleToTensor()((size[0], 1), mstype.int32)
            # For impl of nearest 3D use 4D.
            x = x.unsqueeze(-1)
            resize = _get_cache_prim(P.ResizeNearestNeighborV2)(
                align_corners=False,
                half_pixel_centers=True)
            x = resize(x, size)
            x = _get_cache_prim(P.Squeeze)(-1)(x)
        if x_rank == 4:
            if isinstance(size, int):
                size = F.scalar_to_tensor(size, mstype.int32)
            elif isinstance(size, tuple):
                size = seq.TupleToTensor()(size, mstype.int32)
            else:
                size = seq.ListToTensor()(size, mstype.int32)
            resize = _get_cache_prim(P.ResizeNearestNeighborV2)(
                align_corners=False,
                half_pixel_centers=True)
            x = resize(x, size)
        return x

    supported_dict = {
        "nearest": {
            3: (),
            4: (),
            5: ("scale_factor",)
        },
        "linear": {
            3: ("align_corners",)
        },
        "bilinear": {
            4: ("align_corners",)
        },
        "bicubic": {
            4: ("align_corners",)
        },
        "area": {
            3: ("scale_factor",),
            4: ("scale_factor",),
            5: ("scale_factor",)
        },
        "nearest-exact": {
            3: (),
            4: ()
        },
        "trilinear": {
            5: (
                "align_corners",
                "scale_factor",
            )
        },
    }
    resize_func = {
        "nearest": run_nearest,
        "linear": run_linear,
        "bilinear": run_bilinear,
        "bicubic": run_bicubic,
        "trilinear": run_trilinear,
        "area": run_area,
        "nearest-exact": run_nearest_exact,
    }

    if not isinstance(input, Tensor):
        raise TypeError(
            f"For 'interpolate', 'input' must be a tensor, but got {type(input)}"
        )

    if isinstance(size, list):
        size = tuple(size)
    if isinstance(scale_factor, list):
        scale_factor = tuple(scale_factor)

    rank = F.rank(input)
    shape = F.shape(input)
    dim_unknown = _is_dim_unknown(shape)

    # check for size and scale_factor
    if size is not None and scale_factor is not None:
        raise ValueError(
            "For 'interpolate', 'size' and 'scale_factor' cannot be set simultaneously"
        )
    if size is not None:
        if isinstance(size, (list, tuple)):
            check_positive_int_sequence_const(size, "size", "interpolate")
            if dim_unknown is False:
                _interpolate_size_check_with_rank(size, rank)
        else:
            check_positive_int_const(size, "size", "interpolate")
            if dim_unknown is False:
                size = tuple([size for _ in range(rank - 2)])
            else:
                size = _interploate_make_tuple(rank - 2, size)
    elif scale_factor is not None:
        if isinstance(scale_factor, (list, tuple)):
            check_positive_float_sequence_const(scale_factor, "scale_factor",
                                                "interpolate")
            if dim_unknown is False:
                _interpolate_scale_factor_check_with_rank(scale_factor, rank)
        else:
            check_positive_float_const(scale_factor, "scale_factor",
                                       "interpolate")
            if dim_unknown is False:
                scale_factor = tuple([scale_factor for _ in range(rank - 2)])
            else:
                scale_factor = _interploate_make_tuple(rank - 2, scale_factor)
    else:
        raise ValueError(
            "For 'interpolate', 'size' and 'scale_factor' cannot be both empty"
        )

    # rank check
    _interpolate_mode_check(mode, supported_dict)
    if dim_unknown is False:
        _interpolate_rank_check(rank, mode, supported_dict)

    # "area" mode always requires an explicit size rather than scale factor.
    if mode == "area" and size is None:
        recompute_scale_factor = True

    # recompute_scale_factor
    if recompute_scale_factor is not None and recompute_scale_factor:
        check_bool_const(recompute_scale_factor, "recompute_scale_factor",
                         "interpolate")
        if size is not None:
            raise ValueError(
                "For 'interpolate', it is incorrect to set 'recompute_scale_factor' to True"
                " after specifying an explicit 'size'.")
        if F.isconstant(shape) and F.isconstant(scale_factor):
            tuple_len = min(len(shape) - 2, len(scale_factor))
            size = tuple([floor(shape[i + 2] * scale_factor[i])
                          for i in range(tuple_len)])
        else:
            size = _interpolate_scale_factor_convert_size(shape, scale_factor)
        scale_factor = None
    else:
        if dim_unknown is False:
            _interpolate_scale_factor_check(scale_factor, mode, rank,
                                            supported_dict)

    # align_corners
    if align_corners is not None:
        check_bool_const(align_corners, "align_corners", "interpolate")
        if dim_unknown is False:
            _interpolate_align_corners_mode_check(rank, mode, supported_dict)
    else:
        align_corners = False

    return resize_func.get(mode)(input, size, align_corners, scale_factor)


def _interploate_ext_make_tuple(input, value):
    """
    make tuple
    """
    if isinstance(value, (list, tuple)):
        return value

    rank = F.rank(input) - 2
    out = None
    if F.isconstant(value) and F.isconstant(rank):
        out = tuple([value for _ in range(rank)])
    else:
        out = tensor_to_tuple_(fill_scalar_op((rank,), value, None))
    return out


def _interpolate_ext_scale_factor_convert_size(input, scale_factor):
    """
    convert scale_factor to size
    """
    shape = F.shape(input)
    size = None
    if F.isconstant(shape) and F.isconstant(scale_factor):
        tuple_len = min(len(shape) - 2, len(scale_factor))
        size = tuple([floor(shape[i + 2] * scale_factor[i])
                      for i in range(tuple_len)])
    else:
        x = tuple_to_tensor_(shape[2:], mstype.float32)
        y = tuple_to_tensor_(tuple(scale_factor), mstype.float32)
        t = ops.cast(floor_op(x * y), mstype.int64)
        size = tensor_to_tuple_(t)
    return size


def interpolate_ext(input,
                    size=None,
                    scale_factor=None,
                    mode="nearest",
                    align_corners=None,
                    recompute_scale_factor=None):
    r"""
    Samples the input Tensor to the given size or scale_factor by using one of the interpolate algorithms.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    .. note::
        - In 'linear' mode, the scenarios, where `scale_factor` is not None and `align_corners` is False,
          is not supported.
        - In 'nearest' mode, there may exist precision problem in the scenarios, where input is 3-D/4-D Tensor
          and the image is scaled by scale_factor.
        - `mode` and `recompute_scale_factor` should be constants.

    Args:
        input (Tensor): Tensor to be resized.
            Input tensor must be a 3-D, 4-D, or 5-D tensor with shape
            :math:`(N, C, [optional D], [optional H], W)` , with data type of float.
        size (Union[int, tuple[int], list[int]], optional): The target size.
            If size is a tuple or list, its length should be the same as the number of dimensions in input
            after removing the first two dimensions N, C.
            One and only one of size and scale_factor can be set to None. Default: ``None`` .
        scale_factor (Union[float, tuple[float], list[float]], optional): The scale factor of new size of the tensor.
            If scale_factor is a tuple or list, its length should be the same as the number of dimensions in input
            after removing the first two dimensions N, C.
            One and only one of size and scale_factor can be set to None. Default: ``None`` .
        mode (str): The sampling algorithm.
            One of 'nearest', 'linear' (3D only),
            'bilinear' (4D only), 'trilinear' (5D only), and 'bicubic' (4D only).
            Default: ``"nearest"`` .
        align_corners (bool, optional): Whether to use corner alignment for coordinate mapping.
            Assuming a transformation is
            applied to the input Tensor along the x-axis, the specific calculation formula is as follows:

            .. code-block::

                ori_i = new_length != 1 ? new_i * (ori_length - 1) / (new_length - 1) : 0   # 'align_corners' = True

                ori_i = new_length > 1 ? (new_i + 0.5) * ori_length / new_length - 0.5 : 0  # 'align_corners' = False

            Among them, :math:`ori\_length` and :math:`new\_length` represent the length of the Tensor before and after
            transformation along the x-axis respectively; :math:`new\_i` represents the coordinate of the i-th element
            along the x-axis after transformation; :math:`ori\_i` represents
            the corresponding coordinate of the original
            data along the x-axis.

            This is only valid for ``'linear'``, ``'bilinear'``, or ``'bicubic'`` modes. Default: ``None`` .
        recompute_scale_factor (bool, optional): Recalculate `scale_factor`.
            If True, the parameter `size` will be calculated using the value of the `scale_factor`,
            and finally scaled using the value of `size`.
            If False, the value of `size` or `scale_factor` will be used for direct interpolation. Default: ``None`` .

    Args Support List and Supported Platforms:

    +---------------+-----------+---------------+--------------+----------------+
    | mode          | input.dim | align_corners | scale_factor | device         |
    +===============+===========+===============+==============+================+
    | nearest       | 3         | \-            | √            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 4         | \-            | √            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+
    |               | 5         | \-            | √            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+
    | linear        | 3         | √             | √            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+
    | bilinear      | 4         | √             | ×            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+
    | bicubic       | 4         | √             | ×            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+
    | trilinear     | 5         | √             | √            | Ascend         |
    +---------------+-----------+---------------+--------------+----------------+

    - `-` indicates that there is no such parameter.
    - `×` indicates that this parameter is not currently supported.
    - `√` indicates that this parameter is supported.

    Returns:
        Tensor, sampled, whose dimensions and dtype are the same as `input`.

    Raises:
        TypeError: `input` is not a Tensor.
        ValueError: Both `size` and `scale_factor` are not empty.
        ValueError: Both `size` and `scale_factor` are empty.
        ValueError: When `size` is a tuple or list, its length is not equal to `input.ndim - 2`.
        ValueError: When `scale_factor` is a tuple or list, its length is not equal to `input.ndim - 2`.
        ValueError: `mode` is not in the list of supported modes.
        ValueError: `input.ndim` is not in the list of supported dimensions for the corresponding mode.
        ValueError: `size` is not empty, `recompute_scale_factor` is not empty.
        ValueError: `scale_factor` is not in the corresponding list of supported values.
        ValueError: `align_corners` is not in the corresponding list of supported values.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([[[1, 2, 3], [4, 5, 6]]], mindspore.float32)
        >>> output = ops.interpolate_ext(input, size=(6,), mode='nearest')
        >>> print(output)
        [[[1. 1. 2. 2. 3. 3.]
          [4. 4. 5. 5. 6. 6.]]]
    """

    def run_nearest(x, size, align_corners=None, scale_factor=None):
        x_rank = F.rank(x)
        if x_rank == 3:
            out = upsample_nearest1d_op(x, size, scale_factor)
        elif x_rank == 4:
            out = upsample_nearest2d_op(x, size, scale_factor)
        else:
            out = upsample_nearest3d_op(x, size, scale_factor)
        return out

    def run_linear(x, size, align_corners=None, scale_factor=None):
        out = upsample_linear1d_op(x, size, scale_factor, align_corners)
        return out

    def run_bilinear(x, size, align_corners=None, scale_factor=None):
        out = upsample_bilinear2d_op(x, size, scale_factor, align_corners)
        return out

    def run_trilinear(x, size, align_corners=None, scale_factor=None):
        out = upsample_trilinear3d_impl(x, size, scale_factor, align_corners)
        return out

    def run_bicubic(x, size, align_corners=None, scale_factor=None):
        out = upsample_bicubic2d_op(x, size, scale_factor, align_corners)
        return out

    resize_funcs = {
        "nearest": run_nearest,
        "linear": run_linear,
        "bilinear": run_bilinear,
        "bicubic": run_bicubic,
        "trilinear": run_trilinear,
    }

    # mode check
    if mode not in resize_funcs:
        raise ValueError(
            f"For 'interpolate', 'mode' must be in '{list(resize_funcs)}', but got {mode}"
        )
    if mode in ("nearest", "area", "nearest-exact"):
        if align_corners is not None:
            raise ValueError("align_corners option can only be set with the "
                             "interpolating modes: linear | bilinear | bicubic | trilinear"
                             )
    else:
        if align_corners is None:
            align_corners = False

    # check for size and scale_factor
    if size is not None and scale_factor is not None:
        raise ValueError(
            "For 'interpolate', 'size' and 'scale_factor' cannot be set simultaneously"
        )
    if size is not None:
        size = _interploate_ext_make_tuple(input, size)
    elif scale_factor is not None:
        scale_factor = _interploate_ext_make_tuple(input, scale_factor)
    else:
        raise ValueError(
            "For 'interpolate', 'size' and 'scale_factor' cannot be both empty"
        )

    # "area" mode always requires an explicit size rather than scale factor.
    if mode == "area" and size is None:
        recompute_scale_factor = True

    # recompute_scale_factor
    if recompute_scale_factor is not None and recompute_scale_factor:
        if size is not None:
            raise ValueError(
                "For 'interpolate', it is incorrect to set 'recompute_scale_factor' to True"
                " after specifying an explicit 'size'.")
        size = _interpolate_ext_scale_factor_convert_size(input, scale_factor)
        scale_factor = None

    # scale_factor
    if mode in ("bilinear", "bicubic", "nearest-exact"):
        if scale_factor is not None:
            raise ValueError("scale_factor option can only be set with the "
                             "interpolating modes: nearest | linear | area | trilinear"
                             )

    return resize_funcs.get(mode)(input, size, align_corners, scale_factor)


def upsample(input, size=None, scale_factor=None, mode="nearest", align_corners=None, recompute_scale_factor=None):
    r"""
    Alias for :func:`mindspore.ops.interpolate` .

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    """
    return interpolate(input, size, scale_factor, mode, align_corners, recompute_scale_factor)


def softsign(x):
    r"""
    SoftSign activation function.

    The function is shown as follows:

    .. math::
        \text{SoftSign}(x) = \frac{x}{1 + |x|}

    Softsign Activation Function Graph:

    .. image:: ../images/Softsign.png
        :align: center

    Args:
        x (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of
            additional dimensions, with float16 or float32 data type.

    Returns:
        Tensor, with the same type and shape as the `x`.

    Raises:
        TypeError: If `x` is not a Tensor.
        TypeError: If dtype of `x` is neither float16 nor float32.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([0, -1, 2, 30, -30]), mindspore.float32)
        >>> output = ops.softsign(x)
        >>> print(output)
        [ 0.        -0.5         0.6666667  0.9677419 -0.9677419]
    """
    return softsign_(x)




def softmax(input, axis=-1, *, dtype=None):
    r"""
    Applies the Softmax operation to the input tensor on the specified axis.
    Suppose a slice in the given axis :math:`axis`, then for each element :math:`input_i`,
    the Softmax function is shown as follows:

    .. math::
        \text{output}(input_i) = \frac{\exp(input_i)}{\sum_{j = 0}^{N-1}\exp(input_j)},

    where :math:`N` is the length of the tensor.

    Args:
        input (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of
          additional dimensions, with float16 or float32 data type.
        axis (int, optional): The axis to perform the Softmax operation. Default: ``-1`` .

    Keyword Args:
        dtype (:class:`mindspore.dtype`, optional): When set, `input` will be converted to the specified type,
            `dtype`, before execution, and dtype of returned Tensor will also be `dtype`. Default: ``None`` .

    Returns:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If `axis` is not an int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([1, 2, 3, 4, 5]), mindspore.float32)
        >>> output = ops.softmax(input)
        >>> print(output)
        [0.01165623 0.03168492 0.08612854 0.23412167 0.6364086 ]
    """

    if not isinstance(axis, int):
        type_axis = type(axis).__name__
        raise TypeError(f" the type of 'axis' must be 'int', but got '{axis}' with type '{type_axis}'.")
    if dtype is not None:
        input = ops.cast(input, dtype)
    return softmax_impl(input, axis)


def softmax_ext(input, dim=None, dtype=None):
    r"""
    Applies the Softmax operation to the input tensor on the specified axis.
    Suppose a slice in the given axis :math:`dim`, then for each element :math:`input_i`,
    the Softmax function is shown as follows:

    .. math::
        \text{output}(input_i) = \frac{\exp(input_i)}{\sum_{j = 0}^{N-1}\exp(input_j)},

    where :math:`N` is the length of the tensor.

    Args:
        input (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of
            additional dimensions.
        dim (int, optional): The dim to perform the Softmax operation. Default: ``None`` .
        dtype (:class:`mindspore.dtype`, optional): When set, `input` will be converted to the specified type,
            `dtype`, before execution, and dtype of returned Tensor will also be `dtype`. Default: ``None`` .

    Returns:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If `dim` is not an int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([1, 2, 3, 4, 5]), mindspore.float32)
        >>> output = ops.function.nn_func.softmax_ext(input)
        >>> print(output)
        [0.01165623 0.03168492 0.08612854 0.23412167 0.6364086 ]
    """
    dim = -1 if dim is None else dim
    if not isinstance(dim, int):
        type_dim = type(dim).__name__
        raise TypeError(f" the type of 'dim' must be 'int', but got '{dim}' with type '{type_dim}'.")
    if dtype is not None:
        input = ops.cast(input, dtype)
    return softmax_impl(input, dim)


def log_softmax_ext(input, dim=None, *, dtype=None):
    r"""
    Applies the Log Softmax function to the input tensor on the specified axis.
    Supposes a slice in the given axis, :math:`x` for each element :math:`x_i`,
    the Log Softmax function is shown as follows:

    .. math::
        \text{output}(x_i) = \log \left(\frac{\exp(x_i)} {\sum_{j = 0}^{N-1}\exp(x_j)}\right),

    where :math:`N` is the length of the Tensor.

    Args:
        input (Tensor): The input Tensor.
        dim (int, optional): The axis to perform the Log softmax operation. Default: ``None`` .

    Keyword Args:
        dtype (:class:`mindspore.dtype`, optional): The desired dtype of returned Tensor. If not set to None, the input
            Tensor will be cast to `dtype` before the operation is performed. This is useful for preventing overflows.
            If set to None, stay the same as original Tensor. Default: ``None`` .

    Returns:
        Tensor, with the same shape as the input.

    Raises:
        TypeError: If `dim` is not an int.
        ValueError: If `dim` is not in range [-len(input.shape), len(input.shape)).

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> logits = Tensor(np.array([1, 2, 3, 4, 5]), mindspore.float32)
        >>> output = ops.function.nn_func.log_softmax_ext(logits, dim=-1)
        >>> print(output)
        [-4.4519143 -3.4519143 -2.4519143 -1.4519144 -0.4519144]
    """
    log_softmax_op = _get_cache_prim(P.LogSoftmaxExt)()
    return log_softmax_op(input, dim, dtype)


def softmin(x, axis=-1, *, dtype=None):
    r"""
    Applies the Softmin operation to the input tensor on the specified axis.
    Suppose a slice in the given axis :math:`x`, then for each element :math:`x_i`,
    the Softmin function is shown as follows:

    .. math::
        \text{output}(x_i) = \frac{\exp(-x_i)}{\sum_{j = 0}^{N-1}\exp(-x_j)},

    where :math:`N` is the length of the tensor.

    Args:
        axis (Union[int, tuple[int]], optional): The axis to perform the Softmin operation. Default: ``-1`` .
        x (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of
          additional dimensions, with float16 or float32 data type.

    Keyword Args:
        dtype (:class:`mindspore.dtype`, optional): When set, `x` will be converted to the specified type,
            `dtype`, before execution, and dtype of returned Tensor will also be `dtype`. Default: ``None`` .

    Returns:
        Tensor, with the same type and shape as `x`.

    Raises:
        TypeError: If `axis` is not an int or a tuple.
        TypeError: If dtype of `x` is neither float16 nor float32.
        ValueError: If `axis` is a tuple whose length is less than 1.
        ValueError: If `axis` is a tuple whose elements are not all in range [-len(logits.shape), len(logits.shape)).

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([-1, -2, 0, 2, 1]), mindspore.float16)
        >>> output = ops.softmin(x)
        >>> print(output)
        [0.2341  0.636  0.0862  0.01165  0.03168 ]
    """

    if dtype is not None:
        x = ops.cast(x, dtype)
    softmax_ = _get_cache_prim(P.Softmax)(axis)
    return softmax_(-1 * x)


def soft_shrink(input, lambd=0.5):
    r"""
    `soft_shrink` is deprecated, please use `softshrink` instead.
    """
    logger.warning("`soft_shrink` is deprecated, please use `softshrink` instead.")
    soft_shrink_op = _get_cache_prim(P.SoftShrink)(lambd)
    return soft_shrink_op(input)


def softplus(input, beta=1, threshold=20):  # pylint:disable=redefined-outer-name
    r"""
    Applies softplus function to `input` element-wise.

    The softplus function is shown as follows, x is the element of `input` :

    .. math::

        \text{output} = \frac{1}{beta}\log(1 + \exp(\text{beta * x}))

    When :math:`input * beta > threshold`, the implementation converts to the linear function
    to ensure numerical stability.

    Args:
        input (Tensor) - Tensor of any dimension.
            Supported dtypes:

            - GPU/CPU: float16, float32, float64.
            - Ascend: float16, float32.

        beta (int, optional) - The :math:`\beta` value in softplus function. Default: ``1`` .
        threshold (int, optional) - When :math:`input * beta > threshold`, converting softplus to a linear function.
            Default: ``20`` .

    Returns:
        Tensor, with the same type and shape as the `input` .

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If the dtype of `input` is not float16, float32 or float64.

    Supported Platforms:
        ``Ascend``  ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([0.1, 0.2, 30, 25]), mindspore.float32)
        >>> output = ops.softplus(input)
        >>> print(output)
        [0.7443967 0.79813886 30. 25.]
    """
    if beta == 0:
        raise ValueError("For 'softplus', the value of 'beta' cannot be 0.")
    scaling_input = beta * input
    op_output = (1 / beta) * softplus_(scaling_input)
    return ops.select(input * beta > threshold, input, op_output)


def selu(input_x):
    r"""
    Activation function SeLU (Scaled exponential Linear Unit).

    The activation function is defined as:

    .. math::
        E_{i} =
        scale *
        \begin{cases}
        x_{i}, &\text{if } x_{i} \geq 0; \cr
        \text{alpha} * (\exp(x_i) - 1), &\text{otherwise.}
        \end{cases}

    where :math:`alpha` and :math:`scale` are pre-defined constants(:math:`alpha=1.67326324`
    and :math:`scale=1.05070098`).

    See more details in `Self-Normalizing Neural Networks <https://arxiv.org/abs/1706.02515>`_.

    SeLU Activation Function Graph:

    .. image:: ../images/SeLU.png
        :align: center

    Args:
        input_x (Tensor): Tensor of any dimension,
            the data type is int8, int32, float16, float32, or float64 (CPU, GPU only).

    Returns:
        Tensor, with the same type and shape as the `input_x`.

    Raises:
        TypeError: If dtype of `input_x` is not int8, int32, float16, float32, or float64.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> output = ops.selu(input_x)
        >>> print(output)
        [[-1.1113307 4.202804 -1.7575096]
        [ 2.101402 -1.7462534 9.456309 ]]
    """
    return selu_(input_x)


def logsigmoid(x):
    r"""
    Applies LogSigmoid activation element-wise. The input is a Tensor with any valid shape.

    Logsigmoid is defined as:

    .. math::
        \text{logsigmoid}(x_{i}) = \log(\frac{1}{1 + \exp(-x_i)}),

    where :math:`x_{i}` is the element of the input.

    LogSigmoid Activation Function Graph:

    .. image:: ../images/LogSigmoid.png
        :align: center

    Args:
        x (Tensor): The input of LogSigmoid with data type of float16 or float32.
          The shape is :math:`(N,*)` where :math:`*` means, any number of additional dimensions.

    Returns:
        Tensor, with the same type and shape as the `x`.

    Raises:
        TypeError: If dtype of `x` is neither float16 nor float32.

    Supported Platforms:
        ``Ascend`` ``GPU``  ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([1.0, 2.0, 3.0]), mindspore.float32)
        >>> output = ops.logsigmoid(x)
        >>> print(output)
        [-0.31326166 -0.12692806 -0.04858734]
    """
    output = sigmoid_(x)
    ret = log_(output)
    return ret


def logsigmoid_ext(input):
    r"""
    Applies logsigmoid activation element-wise. The input is a Tensor with any valid shape.

    Logsigmoid is defined as:

    .. math::
        \text{logsigmoid}(x_{i}) = \log(\frac{1}{1 + \exp(-x_i)}),

    where :math:`x_{i}` is the element of the input.

    LogSigmoid Activation Function Graph:

    .. image:: ../images/LogSigmoid.png
        :align: center

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input of LogSigmoid with data type of bfloat16, float16 or float32.
            The shape is :math:`(*)` where :math:`*` means, any number of additional dimensions.

    Returns:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is not bfloat16, float16 and float32.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([1.0, 2.0, 3.0], mindspore.float32)
        >>> output = ops.function.nn_func.logsigmoid_ext(input)
        >>> print(output)
        [-0.31326166 -0.12692806 -0.04858734]
    """
    return logsigmoid_op(input)[0]


def _check_dense_add_bias_shape(input_shape, output_shape, bias_shape):
    """Check that the output has the correct shape after adding bias."""
    if input_shape != output_shape:
        raise ValueError(f"For dense, the bias shape {bias_shape} does not match the input shape {input_shape}.")


@_primexpr
def check_dense_inputs_same_shape(input1_shape, input2_shape, prim_name=None):
    """check bidense input Tensors' shape"""
    msg_prefix = f"For '{prim_name}', the" if prim_name else "The"
    if input1_shape[:-1] != input2_shape[:-1]:
        raise ValueError(f"{msg_prefix} dimensions except the last of 'input1' must be same as 'input2', but got "
                         f"{input1_shape} of 'input1' and {input2_shape} of 'input2'")


def bidense(input1, input2, weight, bias=None):
    r"""
    Applies bilinear dense connected layer for `input1` and `input2`. The bilinear dense function is defined as:

    .. math::
        output = x_{1}^{T}Ax_{2} + b

    :math:`x_{1}` represents `input1` , :math:`x_{2}` represents `input2` , :math:`A` represents `weight` ,
    :math:`b` represents `bias` .

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input1 (Tensor): Input Tensor of shape :math:`(*, in1\_channels)`,
            where :math:`*` means any number of additional dimensions. All but the last dimension
            should be the same with `input2`.
        input2 (Tensor): Input Tensor of shape :math:`(*, in2\_channels)`,
            where :math:`*` means any number of additional dimensions. All but the last dimension
            should be the same with `input1`.
        weight (Tensor): The weight applied to the input1 and input2.
            The shape is :math:`(out\_channels, in1\_channels, in2\_channels)`.
        bias (Tensor, optional): Additive biases to the output.
            The shape is :math:`(out\_channels)` or :math:`()`. Defaults: ``None`` , the `bias` is 0.

    Returns:
        Tensor, shape :math:`(*, out\_channels)`, where :math:`*` means any number of additional dimensions.
        All but the last dimension should be the same with the input Tensors.

    Raises:
        TypeError: If `input1` is not Tensor.
        TypeError: If `input2` is not Tensor.
        TypeError: If `weight` is not Tensor.
        TypeError: If `bias` is not Tensor.
        ValueError: If dimensions except the last of 'input1' are different from 'input2' .


    Supported Platforms:
        ``Ascend`` ``GPU``  ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input1 = mindspore.Tensor([[-1.1283, 1.2603],
        ...                            [0.0214, 0.7801],
        ...                            [-1.2086, 1.2849]], mindspore.float32)
        >>> input2 = mindspore.Tensor([[-0.4631, 0.3238, 0.4201],
        ...                            [0.6215, -1.0910, -0.5757],
        ...                            [-0.7788, -0.0706, -0.7942]], mindspore.float32)
        >>> weight = mindspore.Tensor([[[-0.3132, 0.9271, 1.1010],
        ...                             [0.6555, -1.2162, -0.2987]],
        ...                            [[1.0458, 0.5886, 0.2523],
        ...                             [-1.3486, -0.8103, -0.2080]],
        ...                            [[1.1685, 0.5569, -0.3987],
        ...                             [-0.4265, -2.6295, 0.8535]],
        ...                            [[0.6948, -1.1288, -0.6978],
        ...                             [0.3511, 0.0609, -0.1122]]], mindspore.float32)
        >>> output = ops.bidense(input1, input2, weight)
        >>> print(output)
        [[-2.0612743 0.5581219 0.22383511 0.8667302]
         [1.4476739 0.12626505 1.6552988 0.21297503]
         [0.6003161 2.912046 0.5590313 -0.35449564]]
    """
    _check_is_tensor("input1", input1, "bidense")
    _check_is_tensor("input2", input2, "bidense")
    _check_is_tensor("weight", weight, "bidense")
    _check_is_tensor("bias", bias, "bidense")
    input1_shape = input1.shape
    input2_shape = input2.shape
    check_dense_inputs_same_shape(input1_shape, input2_shape, "bidense")

    if len(input1_shape) != 2:
        input1 = input1.reshape((-1, input1_shape[-1]))
        input2 = input2.reshape((-1, input2_shape[-1]))
    batch_size = input1.shape[0]
    output = matmul_(input1, weight.transpose(1, 2, 0).view(input1_shape[-1], -1))
    output = output.view(batch_size, input2_shape[-1], weight.shape[0])
    output = output.transpose(2, 0, 1) * input2
    output = output.sum(2).swapaxes(0, 1)
    if bias is not None:
        if input1.dtype != bias.dtype or input2.dtype != bias.dtype:
            raise TypeError(f"For 'bidense', the dtype of 'bias', 'input1' and 'input2' must be the same,"
                            f" but got {bias.dtype}, {input1.dtype} and {input2.dtype}.")
        output = bias_add_(output.astype(bias.dtype), bias)
    if len(input1_shape) != 2:
        output_shape = input1_shape[:-1] + (-1,)
        output = output.reshape(output_shape)
    return output


def deformable_conv2d(x, weight, offsets, kernel_size, strides, padding, bias=None, dilations=(1, 1, 1, 1), groups=1,
                      deformable_groups=1, modulated=True):
    r"""
    Given 4D tensor inputs `x`, `weight` and `offsets`, compute a 2D deformable convolution. The deformable convolution
    operation can be expressed as follow:

    Deformable Convolution v1:

    .. math::
        y(p)=\sum_{k=1}^{K}w_{k}\cdot x(p+p_{k}+\Delta{p_{k}})

    Deformable Convolution v2:

    .. math::
        y(p)=\sum_{k=1}^{K}w_{k}\cdot x(p+p_{k}+\Delta{p_{k}})\cdot \Delta{m_{k}}

    Where :math:`\Delta{p_{k}}` and :math:`\Delta{m_{k}}` are the learnable offset and modulation scalar for the k-th
    location. For details, please refer to `Deformable ConvNets v2: More Deformable, Better Results
    <https://arxiv.org/abs/1811.11168>`_ and `Deformable Convolutional Networks <https://arxiv.org/abs/1703.06211>`_.

    Args:
        x (Tensor): A 4D tensor of input image. With the format "NCHW",
            the shape is :math:`(N, C_{in}, H_{in}, W_{in})`. Dtype: float16 or float32.
        weight (Tensor): A 4D tensor of learnable filters. Must have the same type as `x`.
            The shape is :math:`(C_{out}, C_{in} / groups, H_{f}, W_{f})`.
        offsets (Tensor): A 4D tensor of x-y coordinates offset and mask. With the format "NCHW",
            the shape is :math:`(batch, 3 * deformable\_groups * H_{f} * W_{f}, H_{out}, W_{out})`. Note the C dimension
            is stored in the order of (offset_x, offset_y, mask). Must have the same type as `x`.
        kernel_size (tuple[int]): A tuple of 2 integers. The size of kernel.
        strides (tuple[int]): A tuple of 4 integers. The stride of the sliding window for each dimension of
            input. The dimension order is interpreted according to the data format of `x`. The N and C dimensions must
            be set to 1.
        padding (tuple[int]): A tuple of 4 integers. The number of pixels to add to each (top, bottom, left,
            right) side of the input.
        bias (Tensor, optional): An 1D tensor of additive biases to the filter outputs.
            The shape is :math:`(C_{out})`. Default: ``None`` .
        dilations (tuple[int], optional): A tuple of 4 integers. The dilation factor for each dimension of input. The
            dimension order is interpreted according to the data format of `x`. The N and C dimensions must be set
            to 1. Default: ``(1, 1, 1, 1)`` .
        groups (int, optional): An integer of type int32. The number of blocked connections from input channels
            to output channels. In_channels and out_channels must both be divisible by `groups`. Default: ``1`` .
        deformable_groups (int, optional): An integer of type int32. The number of deformable group partitions.
            In_channels must be divisible by `deformable_groups`. Default: ``1`` .
        modulated (bool, optional): Specifies version of DeformableConv2D, True means v2, False means v1, currently
            only supports v2. Default: ``True`` .

    Returns:
        Tensor, A 4D Tensor of output feature map. With the same type as `x`. With the format "NCHW",
        the shape is :math:`(N, C_{out}, H_{out}, W_{out})`.

        .. math::
            \begin{array}{ll} \\
                H_{out} = \left \lfloor{\frac{H_{in} + padding[0] + padding[1] - (H_{f} - 1) \times
                \text{dilations[2]} - 1 }{\text{stride[0]}} + 1} \right \rfloor \\
                W_{out} = \left \lfloor{\frac{W_{in} + padding[2] + padding[3] - (W_{f} - 1) \times
                \text{dilations[3]} - 1 }{\text{stride[1]}} + 1} \right \rfloor \\
            \end{array}

    Raises:
        TypeError: If `strides`, `padding`, `kernel_size` or `dilations` is not a tuple with integer elements.
        TypeError: If `modulated` is not a bool.
        ValueError: If the tuple size of `strides`, `padding`, `kernel_size` or `dilations` is not expected.
        ValueError: The N or C dimensions of `strides` or `dilations` is not set to 1.
        ValueError: If `modulated` is not set to True.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> x = Tensor(np.ones((4, 3, 10, 10)), mstype.float32)
        >>> kh, kw = 3, 3
        >>> weight = Tensor(np.ones((5, 3, kh, kw)), mstype.float32)
        >>> offsets = Tensor(np.ones((4, 3 * kh * kw, 8, 8)), mstype.float32)
        >>> output = ops.deformable_conv2d(x, weight, offsets, (kh, kw), (1, 1, 1, 1), (0, 0, 0, 0))
        >>> print(output.shape)
        (4, 5, 8, 8)
    """
    deformable_offsets = _get_cache_prim(NN_OPS.DeformableOffsets)(strides, padding, kernel_size, dilations, "NCHW",
                                                                   deformable_groups,
                                                                   modulated)
    fm_offset = deformable_offsets(x, offsets)
    weight_shape = weight.shape
    out_channel = weight_shape[0]
    strides_conv = (kernel_size[0], kernel_size[1])
    conv = _get_cache_prim(P.Conv2D)(out_channel, kernel_size, 1, "valid", 0, strides_conv, 1, groups)
    output = conv(fm_offset, weight)
    if bias is not None:
        output = bias_add_(output, bias)
    return output


def pdist(input, p=2.0):
    r"""
    Calculates the distance between every pair of row vectors in
    the input using the p-norm. If the input `input` is a 2D Tensor with shape :math:`(N, M)`,
    the `output` must be a 1D Tensor with shape :math:`(N * (N - 1) / 2,)`.

    .. math::
        y[n] = \sqrt[p]{{\mid x_{i} - x_{j} \mid}^p}

    where :math:`x_{i}, x_{j}` are two different row vectors in the input.

    Args:
        input (Tensor): Input tensor. dtype: float16, float32 or float64.
        p (float): The order of norm distance, :math:`p∈[0, ∞)`. Default: ``2.0`` .

    Returns:
        Tensor, has the same dtype as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not float16, float32 or float64.
        TypeError: If `p` is not a float.
        ValueError: If `p` is a negative float.
        ValueError: If dimension of `input` is less than 2.

    Supported Platforms:
        ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]]).astype(np.float32))
        >>> y = ops.pdist(x, p=2.0)
        >>> print(y)
        [1.4142135 2.828427 1.4142135]
    """
    pdist_ = _get_cache_prim(NN_OPS.Pdist)(p=p)
    return pdist_(input)


def _circular_pad(input_x, padding):
    """circular pad"""
    if isinstance(padding, tuple):
        padding = tuple_to_tensor_(padding, mstype.int64)
    elif isinstance(padding, list):
        padding = list_to_tensor_(padding, mstype.int64)
    is_expand = False
    if padding.shape[0] // 2 + 1 == input_x.ndim:
        input_x = input_x.expand_dims(0)
        is_expand = True
    out = PadV3(mode="circular", paddings_contiguous=True)(input_x, padding, None)
    if is_expand:
        out = out.squeeze(0)
    return out


def _reflection_pad(input, pad):
    """reflection pad"""
    out = input
    if len(pad) == 2:
        out = reflection_pad_1d_op(input, pad)
    elif len(pad) == 4:
        out = reflection_pad_2d_op(input, pad)
    else:
        out = reflection_pad_3d_op(input, pad)
    return out


def _replication_pad(input, pad):
    """replication pad"""
    out = input
    if len(pad) == 2:
        out = replication_pad_1d_op(input, pad)
    elif len(pad) == 4:
        out = replication_pad_2d_op(input, pad)
    else:
        out = replication_pad_3d_op(input, pad)
    return out


def pad_ext(input, pad, mode='constant', value=None):
    r"""
    Pads the input tensor according to the pad.

    .. warning::
        `circular` mode has poor performance and is not recommended.

    Args:
        input (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of additional dimensions.
        pad (Union[tuple[int], list[int], Tensor]): Filling position of pad.
            :math:`\left\lfloor\frac{\text{len(pad)}}{2}\right\rfloor` dimensions
            of `input` will be padded.

            Example: to pad only the last dimension of the input tensor, then
            :attr:`pad` has the form
            :math:`(\text{padding_left}, \text{padding_right})`;

            Example: to pad the last 2 dimensions of the input tensor, then use
            :math:`(\text{padding_left}, \text{padding_right}, \text{padding_top}, \text{padding_bottom})`;

            Example: to pad the last 3 dimensions, use
            :math:`(\text{padding_left}, \text{padding_right}, \text{padding_top}, \text{padding_bottom},
            \text{padding_front}, \text{padding_back})` and so on.

        mode (str, optional): Pad filling mode, ``'constant'`` , ``'reflect'`` , ``'replicate'``  or ``'circular'`` .
            Default: ``'constant'`` .

            For ``'constant'`` mode, please refer to :class:`mindspore.nn.ConstantPad1d` as an example to understand
            this filling pattern and extend the padding pattern to n dimensions.

            For ``'reflect'`` mode, please refer to :class:`mindspore.nn.ReflectionPad1d` as an example to understand
            this filling pattern.
            The reflect mode is used to pad the last three dimensions of 4D or 5D input, the last two dimensions of 3D
            or 4D input, or the last dimension of 2D or 3D input.

            For ``'replicate'`` mode, please refer to :class:`mindspore.nn.ReplicationPad1d` as an example to understand
            this filling pattern.
            The replicate mode is used to pad the last three dimensions of 4D or 5D input, the last two dimensions of 3D
            or 4D input, or the last dimension of 2D or 3D input.

            For ``'circular'`` mode, the pixels from one edge of the image are wrapped around to the opposite edge,
            such that the pixel on the right edge of the image is replaced with the pixel on the left edge,
            and the pixel on the bottom edge is replaced with the pixel on the top edge.
            The circular mode is used to pad the last three dimensions of 4D or 5D input, the last two dimensions of 3D
            or 4D input, or the last dimension of 2D or 3D input.

        value (Union[int, float, None], optional): Valid only in ``'constant'`` mode.
            Set the padding value in ``'constant'`` mode. If the value is None, 0 is used as the default padding value.
            Default: ``None`` .

    Returns:
        Tensor, the tensor after padding.

    Raises:
        TypeError: If `pad` is not an int of tuple or int of list.
        TypeError: If `input` is not a Tensor.
        ValueError: If length of `pad` is not even.
        ValueError: If length of `pad` is greater than 6.
        ValueError: If `mode` is not ``'constant'`` and `value` is neither ``None`` nor 0.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> import numpy as np
        >>> x = ms.Tensor(np.arange(1 * 2 * 2 * 2).reshape((1, 2, 2, 2)), dtype=ms.float64)
        >>> output = ops.function.nn_func.pad_ext(x, [1, 0, 0, 1], mode='constant', value=6.0)
        >>> print(output)
        [[[[6. 0. 1.]
           [6. 2. 3.]
           [6. 6. 6.]]
          [[6. 4. 5.]
           [6. 6. 7.]
           [6. 6. 6.]]]]
    """
    if not isinstance(input, Tensor):
        raise TypeError(f"For 'pad', the type of 'input' must be Tensor, but got {type(input)}.")
    out = input
    if (isinstance(pad, tuple) and not pad):
        return out
    if mode == "constant":
        value = 0 if value is None else value
        out = constant_pad_nd_op(input, pad, value)
    else:
        if value is not None and value != 0:
            raise ValueError(f"Padding mode {mode} doesn\'t take in value argument.")
        if mode == "circular":
            out = _circular_pad(input, pad)
        elif mode == "reflect":
            out = _reflection_pad(input, pad)
        elif mode == "replicate":
            out = _replication_pad(input, pad)
        else:
            raise ValueError(f"Pad filling mode must be 'constant' 'circular' 'reflect' or 'replicate'.")
    return out


def _check_pad_inputs(padding):
    """check the input of pad"""
    if len(padding) % 2 != 0:
        raise ValueError(f"For 'pad', the size of padding must be divisible by 2, but got {len(padding)}")
    if not isinstance(padding, (tuple, list)):
        raise TypeError(f"For 'pad', the type of 'paddings' must be a tuple of int or list of int or a Tensor,"
                        f" but got {type(padding)}.")
    for pd in padding:
        if not isinstance(pd, int):
            raise TypeError(f"For 'pad', the paddings value must be tuple of int or list of int, but got {padding}")


def pad(input_x, padding, mode='constant', value=None):
    r"""
    Pads the input tensor according to the padding.

    Args:
        input_x (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of additional dimensions
            which is required to be no more than 5 in Ascend.
        padding (Union[tuple[int], list[int], Tensor]): Filling position of pad where the negative value is not
            supported while running in Ascend.
            :math:`\left\lfloor\frac{\text{len(padding)}}{2}\right\rfloor` dimensions
            of `input_x` will be padded.

            Example: to pad only the last dimension of the input tensor, then
            :attr:`padding` has the form
            :math:`(\text{padding_left}, \text{padding_right})`;

            Example: to pad the last 2 dimensions of the input tensor, then use
            :math:`(\text{padding_left}, \text{padding_right}, \text{padding_top}, \text{padding_bottom})`;

            Example: to pad the last 3 dimensions, use
            :math:`(\text{padding_left}, \text{padding_right}, \text{padding_top}, \text{padding_bottom},
            \text{padding_front}, \text{padding_back})` and so on.

        mode (str, optional): Pad filling mode, ``'constant'`` , ``'reflect'`` , ``'replicate'``  or ``'circular'`` .
            Default: ``'constant'`` .

            For ``'constant'`` mode, please refer to :class:`mindspore.nn.ConstantPad1d` as an example to understand
            this filling pattern and extend the padding pattern to n dimensions.

            For ``'reflect'`` mode, please refer to :class:`mindspore.nn.ReflectionPad1d` as an example to understand
            this filling pattern.
            The reflect mode is used to pad the last two dimensions of 3D or 4D input, or the last dimension of 2D or
            3D input.

            For ``'replicate'`` mode, please refer to :class:`mindspore.nn.ReplicationPad1d` as an example to understand
            this filling pattern.
            The replicate mode is used to pad the last three dimensions of 4D or 5D input, the last two dimensions of 3D
            or 4D input, or the last dimension of 2D or 3D input.

            For ``'circular'`` mode, the pixels from one edge of the image are wrapped around to the opposite edge,
            such that the pixel on the right edge of the image is replaced with the pixel on the left edge,
            and the pixel on the bottom edge is replaced with the pixel on the top edge.
            The circular mode is used to pad the last three dimensions of 4D or 5D input, the last two dimensions of 3D
            or 4D input, or the last dimension of 2D or 3D input.

        value (Union[int, float, None], optional): Valid only in ``'constant'`` mode.
            Set the padding value in ``'constant'`` mode. If the value is None, 0 is used as the default padding value.
            Default: ``None`` .

    Returns:
        Tensor, the tensor after padding.

    Raises:
        TypeError: If `padding` is not an int of tuple or int of list.
        TypeError: If `input_x` is not a Tensor.
        ValueError: If length of `padding` is not even.
        ValueError: If length of `padding` is greater than 6.
        ValueError: If `mode` is not ``'constant'`` and `value` not ``None``.
        ValueError: If rank of `input_x` is more than 5 while running in Ascend.
        ValueError: If `paddings` contains negative value while running in Ascend.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> import numpy as np
        >>> x = ms.Tensor(np.arange(1 * 2 * 2 * 2).reshape((1, 2, 2, 2)), dtype=ms.float64)
        >>> output = ops.pad(x, [1, 0, 0, 1], mode='constant', value=6.0)
        >>> print(output)
        [[[[6. 0. 1.]
           [6. 2. 3.]
           [6. 6. 6.]]
          [[6. 4. 5.]
           [6. 6. 7.]
           [6. 6. 6.]]]]
        >>> output1 = ops.pad(x, (1, 0, 0, 1), mode='reflect')
        >>> print(output1)
        [[[[1. 0. 1.]
           [3. 2. 3.]
           [1. 0. 1.]]
          [[5. 4. 5.]
           [7. 6. 7.]
           [5. 4. 5.]]]]
        >>> output2 = ops.pad(x, (1, 1, 2, 1), mode='replicate')
        >>> print(output2)
        [[[[0. 0. 1. 1.]
           [0. 0. 1. 1.]
           [0. 0. 1. 1.]
           [2. 2. 3. 3.]
           [2. 2. 3. 3.]]
          [[4. 4. 5. 5.]
           [4. 4. 5. 5.]
           [4. 4. 5. 5.]
           [6. 6. 7. 7.]
           [6. 6. 7. 7.]]]]
        >>> output3 = ops.pad(x, (1, 1, 2, 1), mode='circular')
        >>> print(output3)
        [[[[1. 0. 1. 0.]
           [3. 2. 3. 2.]
           [1. 0. 1. 0.]
           [3. 2. 3. 2.]
           [1. 0. 1. 0.]]
          [[5. 4. 5. 4.]
           [7. 6. 7. 6.]
           [5. 4. 5. 4.]
           [7. 6. 7. 6.]
           [5. 4. 5. 4.]]]]
    """
    if not isinstance(input_x, Tensor):
        raise TypeError(f"For 'pad', the type of 'input_x' must be Tensor, but got {type(input_x)}.")
    if (isinstance(padding, (tuple, list)) and not padding) or (isinstance(padding, Tensor) and padding.shape == (0,)):
        return input_x
    if not isinstance(padding, Tensor):
        _check_pad_inputs(padding)
        padding = tuple(padding)
    is_expand = False
    if mode == "constant":
        value = 0 if value is None else value
        if isinstance(value, (float, int)):
            value = scalar_to_tensor_(value, input_x.dtype)
    else:
        if len(padding) > 6:
            raise ValueError(f"For 'pad', the padding must be less than or equal to 6, but got {len(padding)}.")
        if value is not None:
            raise ValueError(f"For 'pad', the padding mode '{mode}' can not set value, but got value {value}.")
        if mode == "replicate":
            mode = "edge"
        if len(padding) // 2 + 1 == input_x.ndim:
            input_x = input_x.expand_dims(0)
            is_expand = True
    out = PadV3(mode=mode, paddings_contiguous=True)(input_x, padding, value)
    if is_expand:
        out = out.squeeze(0)
    return out


def rrelu(input, lower=1.0 / 8, upper=1.0 / 3):
    r"""

    Randomized Leaky ReLU activation function.

    The activation function is defined as:

    .. math::
        \text{rrelu}(input_{ji}) = \begin{cases}input_{ji}, &\text{if } input_{ji} \geq 0; \cr
        {\alpha_{ji}} * input_{ji}, &\text{otherwise.}\end{cases}

    where :math:`\alpha_{ji}` ~ :math:`U(l, u)`, :math:`l \le u`.

    Applies the rrelu function elementally, as described in the paper:
    `Empirical Evaluation of Rectified Activations in Convolution Network <https://arxiv.org/pdf/1505.00853.pdf>`_ .

    Args:
        input (Tensor): The input of rrelu is a Tensor of any dimension.
        lower (Union[int, float]): Slope of the activation function at data of `input` is less than 0.
            Default: ``1.0 / 8`` .
        upper (Union[int, float]): Slope of the activation function at data of `input` is less than 0.
            Default: ``1.0 / 3`` .

    Returns:
        Tensor, after rrelu, has the same type and shape as the `input`.

    Raises:
        TypeError: If `lower` is not a float or an int.
        TypeError: If `upper` is not a float or an int.
        TypeError: If `input` is not a Tensor.
        TypeError: If `input` is not a Tensor of mindspore.float16 or mindspore.float32.
        ValueError: If `lower` is greater than upper.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[-1.0, 4.0], [2.0, 0]]), mindspore.float32)
        >>> output = ops.rrelu(x)
        >>> print(output)
        [[-0.31465699  4.        ]
         [ 2.          0.        ]]
    """
    if not isinstance(upper, (float, int)):
        raise TypeError(f"For 'rrelu', 'upper' must be an int or a float, but got {type(upper)}")
    if not isinstance(lower, (float, int)):
        raise TypeError(f"For 'rrelu', 'lower' must be an int or a float, but got {type(lower)}")
    if lower > upper:
        raise ValueError(f"For 'rrelu', the value of 'upper' must be greater than or equal to 'lower', "
                         f"but got upper: {upper}, lower: {lower}. ")
    if not isinstance(input, Tensor):
        raise TypeError(f"For 'rrelu', the 'input' must be a Tensor but got {type(input)}.")
    _lower = Tensor(lower, mstype.float32)
    _upper = Tensor(upper, mstype.float32)
    _size = input.shape
    if ops.is_sequence_value_unknown(_size):
        _size = tensor_shape_(input)
    sign_matrix = sign_(input)
    negative_filter = sign_matrix.clip(None, 0)
    positive_filter = sign_matrix.clip(0, None)
    input_dtype = dtype_(input)
    mask = ops.uniform(_size, _lower, _upper).astype(input_dtype)
    negative_mask = negative_filter * mask * -1
    total_mask = negative_mask + positive_filter
    out = total_mask * input
    return out


def mirror_pad(input_x, paddings, mode):
    """
    Pads the input tensor according to the paddings and mode.

    Args:
        input_x (Tensor): Tensor of shape :math:`(N, *)`, where :math:`*` means, any number of
          additional dimensions.
        paddings (Tensor): Paddings requires constant tensor. The value of `paddings` is a
          matrix(list), and its shape is (N, 2). N is the rank of input data. All elements of paddings
          are int type. For the input in the `D` th dimension, paddings[D, 0] indicates how many sizes
          to be extended ahead of the input tensor in the `D` th dimension, and paddings[D, 1]
          indicates how many sizes to be extended behind the input tensor in the `D` th dimension. Both
          paddings[D, 0] and paddings[D, 1] must be no greater than input_x.dim_size(D)
          (or input_x.dim_size(D) - 1) if mode is SYMMETRIC (if REFLECT, respectively).
        mode (str): Specifies the padding mode. The optional values are "REFLECT" and "SYMMETRIC".
            Default: "REFLECT".

    Returns:
        Tensor, the tensor after padding.

        - If `mode` is "REFLECT", it uses a way of symmetrical copying through the axis of symmetry to fill in.
          If the `input_x` is [[1,2,3], [4,5,6], [7,8,9]] and `paddings` is [[1,1], [2,2]], then the
          `Outputs` is [[6,5,4,5,6,5,4], [3,2,1,2,3,2,1], [6,5,4,5,6,5,4], [9,8,7,8,9,8,7], [6,5,4,5,6,5,4]].
          For a more intuitive understanding, please see the example below.
        - If `mode` is "SYMMETRIC", the filling method is similar to the "REFLECT". It is also copied
          according to the symmetry axis, except that it includes the symmetry axis. If the `input_x`
          is [[1,2,3], [4,5,6], [7,8,9]] and `paddings` is [[1,1], [2,2]], then the `Outputs` is
          [[2,1,1,2,3,3,2], [2,1,1,2,3,3,2], [5,4,4,5,6,6,5], [8,7,7,8,9,9,8], [8,7,7,8,9,9,8]].
          For a more intuitive understanding, please see the example below.

    Raises:
        TypeError: If `input_x` or `paddings` is not a Tensor.
        TypeError: If `mode` is not a str.
        ValueError: If paddings.size is not equal to 2 * rank of input_x.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor([[1,2,3], [4,5,6], [7,8,9]])
        >>> mode = "REFLECT"
        >>> paddings = Tensor([[1, 1], [2, 2]])
        >>> output = ops.mirror_pad(input_x, paddings, mode)
        >>> print(output)
        [[6 5 4 5 6 5 4]
         [3 2 1 2 3 2 1]
         [6 5 4 5 6 5 4]
         [9 8 7 8 9 8 7]
         [6 5 4 5 6 5 4]]
    """

    _mirror_pad = _get_cache_prim(P.MirrorPad)(mode)
    return _mirror_pad(input_x, paddings)


def _innner_log_softmax(inputs, axis):
    """inner implementation of log_softmax, since the LogSoftmaxGrad op do not support inputs > 2d"""
    return inputs - logsumexp(inputs, axis, True)


def _check_cross_entropy_inputs(input, target, weight, ignore_index, reduction, label_smoothing):
    """
    Check inputs for cross_entropy().
    """
    _check_is_tensor('input', input, "cross_entropy_loss")
    _check_is_tensor('target', target, "cross_entropy_loss")
    _check_is_tensor('weight', weight, "cross_entropy_loss")
    check_int_const(ignore_index, 'ignore_index', "cross_entropy_loss")
    check_non_negative_float_const(label_smoothing, 'label_smoothing', "cross_entropy_loss")
    check_string_const(reduction, ['none', 'mean', 'sum'], 'reduction', "cross_entropy_loss")
    if input.dtype not in [mstype.float64, mstype.float32, mstype.float16]:
        raise TypeError(f'For cross_entropy, the input dtype should be mstype.float64, mstype.float32 or'
                        f'mstype.float16, but got dtype:{input.dtype}.')


def cross_entropy(input, target, weight=None, ignore_index=-100, reduction='mean', label_smoothing=0.0):
    r"""
    The cross entropy loss between input and target.

    The cross entropy support two kind of targets:

    - Class indices (int) in the range :math:`[0, C)` where :math:`C` is the number of classes,
      the loss with reduction=none can be described as:

      .. math::

          \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad
          l_n = - w_{y_n} \log \frac{\exp(x_{n,y_n})}{\sum_{c=1}^C \exp(x_{n,c})}
          \cdot \mathbb{1}\{y_n \not= \text{ignore_index}\}

      where :math:`x` is the inputs, :math:`y` is the target, :math:`w` is the weight, N is the batch size,
      :math:`c` belonging to :math:`[0, C-1]` is class index, where :math:`C` is the number of classes.

      If `reduction` is not ``None`` (default ``'mean'`` ), then

      .. math::

          \ell(x, y) = \begin{cases}
              \sum_{n=1}^N \frac{1}{\sum_{n=1}^N w_{y_n} \cdot \mathbb{1}\{y_n \not= \text{ignore_index}\}} l_n, &
              \text{if reduction} = \text{'mean',}\\
              \sum_{n=1}^N l_n,  &
              \text{if reduction} = \text{'sum'.}
              \end{cases}

    - Probabilities (float) for each class, useful when labels beyond a single class per minibatch item
      are required, the loss with reduction=none can be described as:

      .. math::

          \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad
          l_n = - \sum_{c=1}^C w_c \log \frac{\exp(x_{n,c})}{\sum_{i=1}^C \exp(x_{n,i})} y_{n,c}

      where :math:`x` is the inputs, :math:`y` is the target, :math:`w` is the weight, N is the batch size,
      :math:`c` belonging to :math:`[0, C-1]` is class index, where :math:`C` is the number of classes.

      If `reduction` is not ``None`` (default ``'mean'`` ), then

      .. math::

          \ell(x, y) = \begin{cases}
              \frac{\sum_{n=1}^N l_n}{N}, &
              \text{if reduction} = \text{'mean',}\\
              \sum_{n=1}^N l_n,  &
              \text{if reduction} = \text{'sum'.}
              \end{cases}

    Args:
        input (Tensor): :math:`(N)` or :math:`(N, C)` where `C = number of classes` or :math:`(N, C, H, W)`
            in case of 2D Loss, or :math:`(N, C, d_1, d_2, ..., d_K)`.
            `input` is expected to be log-probabilities, data type must be float16 or float32.
        target (Tensor): For class indices, tensor of shape :math:`()`, :math:`(N)` or
            :math:`(N, d_1, d_2, ..., d_K)` , data type must be int32. For probabilities, tensor of shape :math:`(C,)` ,
            :math:`(N, C)` or :math:`(N, C, d_1, d_2, ..., d_K)` , data type must be float16 or float32 or float64.
        weight (Tensor): A rescaling weight applied to the loss of each batch element.
            If not None, the shape is :math:`(C,)`, data type must be float16 or float32. Default: ``None`` .
        ignore_index (int): Specifies a target value that is ignored
            and does not contribute to the input gradient. Default: ``-100`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

        label_smoothing (float): Label smoothing values, a regularization tool used to prevent the model
            from overfitting when calculating Loss. The value range is [0.0, 1.0]. Default value: ``0.0`` .

    Returns:
        Tensor, the computed loss value.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore as ms
        >>> import numpy as np
        >>> # Case 1: Indices labels
        >>> inputs = ms.Tensor(np.random.randn(3, 5), ms.float32)
        >>> target = ms.Tensor(np.array([1, 0, 4]), ms.int32)
        >>> output = ms.ops.cross_entropy(inputs, target)
        >>> # Case 2: Probability labels
        >>> inputs = ms.Tensor(np.random.randn(3, 5), ms.float32)
        >>> target = ms.Tensor(np.random.randn(3, 5), ms.float32)
        >>> output = ms.ops.cross_entropy(inputs, target)
    """
    _check_cross_entropy_inputs(input, target, weight, ignore_index, reduction, label_smoothing)
    class_dim = 0 if input.ndim == 1 else 1
    if target.dtype in [mstype.float32, mstype.float16]:
        return _cross_entropy(input, target, class_dim, weight, reduction, label_smoothing)
    return nll_loss(_innner_log_softmax(input, class_dim), target, weight, ignore_index, reduction, label_smoothing)


def _cross_entropy(inputs, target, target_dim, weight=None, reduction='mean', label_smoothing=0.0):
    """cross entropy inner function"""
    class_dim = 0 if inputs.ndim == 1 else 1
    n_classes = inputs.shape[class_dim]
    inputs = _innner_log_softmax(inputs, class_dim)
    if label_smoothing > 0.0:
        target = target * (1 - label_smoothing) + label_smoothing / n_classes

    if weight is None:
        weight = ones_like_(inputs)
    elif inputs.ndim != 1:
        broadcast_shape = [1 for _ in range(inputs.ndim)]
        broadcast_shape[1] = weight.shape[0]
        weight = weight.reshape(broadcast_shape)

    if reduction == 'mean':
        return -(inputs * target * weight).sum() / (inputs.size / n_classes)
    if reduction == 'sum':
        return -(inputs * target * weight).sum()
    return -(inputs * target * weight).sum(class_dim)


def nll_loss(inputs, target, weight=None, ignore_index=-100, reduction='mean', label_smoothing=0.0):
    r"""
    Gets the negative log likelihood loss between inputs and target.

    The nll loss with reduction=none can be described as:

    .. math::

        \ell(x, t)=L=\left\{l_{1}, \ldots, l_{N}\right\}^{\top},
        \quad l_{n}=-w_{t_{n}} x_{n, t_{n}},
        \quad w_{c}=\text { weight }[c] \cdot \mathbb{1}
        \{c \not= \text{ignore_index}\},

    where :math:`x` is the inputs, :math:`t` is the target, :math:`w` is the weight,
    N is the batch size, :math:`c` belonging to :math:`[0, C-1]` is class index, where :math:`C` is the number of
    classes.

    If `reduction` is not ``'None'`` (default ``'mean'``), then

    .. math::

        \ell(x, t)=\left\{\begin{array}{ll}
        \sum_{n=1}^{N} \frac{1}{\sum_{n=1}^{N} w_{t n}} l_{n}, & \text { if reduction }=\text { 'mean', } \\
        \sum_{n=1}^{N} l_{n}, & \text { if reduction }=\text { 'sum' }
        \end{array}\right.

    .. warning::
        - In GE mode, the rank of `inputs` should be 1D or 2D, the rank of `target` and `weight` should be 1D,
          and the following restraints should be met:

          - when `inputs` is 1D: target_shape[0] == 1 and weight_shape[0] == inputs_shape[0].
          - when `inputs` is 2D: target_shape[0] == inputs_shape[0] and weight_shape[0] == inputs_shape[1].

        - On GPU or CPU, `inputs` should be 2D.

    Args:
        inputs (Tensor): :math:`(N, C)` where `C = number of classes` or :math:`(N, C, H, W)`
            in case of 2D Loss, or :math:`(N, C, d_1, d_2, ..., d_K)`.
            `inputs` is expected to be log-probabilities, data type must be float16 or float32.
        target (Tensor): :math:`(N)` or :math:`(N, d_1, d_2, ..., d_K)` for
            high-dimensional loss, data type must be int32.
        weight (Tensor): A rescaling weight applied to the loss of each batch element.
            If not None, the shape is :math:`(C,)`.
            The data type must be float16 or float32. Default: ``None`` .
        ignore_index (int): Specifies a target value that is ignored
            and does not contribute to the input gradient. Default: ``-100`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

        label_smoothing (float): Label smoothing values, a regularization tool used to prevent the model
            from overfitting when calculating Loss. The value range is [0.0, 1.0]. Default value: ``0.0`` .

    Returns:
        Tensor, the computed loss value.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> inputs = mindspore.Tensor(np.random.randn(3, 5), mindspore.float32)
        >>> target = mindspore.Tensor(np.array([1, 0, 4]), mindspore.int32)
        >>> output = ops.nll_loss(inputs, target)

    """
    ndim = inputs.ndim
    if ndim == 2:
        ret = _nll_loss(inputs, target, -1, weight, ignore_index, reduction, label_smoothing)
    elif ndim == 4:
        ret = _nll_loss(inputs, target, 1, weight, ignore_index, reduction, label_smoothing)
    elif ndim == 1:
        ret = _nll_loss(inputs, target, 0, weight, ignore_index, reduction, label_smoothing)
    else:
        n = inputs.shape[0]
        c = inputs.shape[1]
        out_size = (n,) + inputs.shape[2:]
        inputs = inputs.view((n, c, 1, -1))
        target = target.view((n, 1, -1))
        if reduction != 'none':
            ret = _nll_loss(inputs, target, 1, weight, ignore_index, reduction, label_smoothing)
        else:
            ret = _nll_loss(inputs, target, 1, weight, ignore_index, label_smoothing=label_smoothing)
            ret = ret.view(out_size)
    return ret


def _nll_loss(inputs, target, target_dim=-1, weight=None, ignore_index=None, reduction='none', label_smoothing=0.0):
    """nll loss inner function"""
    if target.ndim == inputs.ndim - 1:
        target = target.expand_dims(target_dim)
    if ignore_index is not None:
        non_pad_mask = equal_(target, ignore_index)
        target = target.masked_fill(non_pad_mask, ops.cast(0, target.dtype))
    else:
        non_pad_mask = target
    if weight is not None:
        loss_weights = gather_(weight, target, 0)
        orig_shape = inputs.shape
        if inputs.ndim != 2:
            inputs = inputs.view(orig_shape[:2] + (-1,))
            weight = weight.view(weight.shape + (1,))
        weighted_inputs = inputs * weight
        weighted_inputs = weighted_inputs.view(orig_shape)
        loss = neg_(gather_d_(weighted_inputs, target_dim, target))
        smooth_loss = neg_(weighted_inputs.sum(axis=target_dim, keepdims=True))
    else:
        loss = neg_(gather_d_(inputs, target_dim, target))
        smooth_loss = neg_(inputs.sum(axis=target_dim, keepdims=True))
        loss_weights = ones_like_(loss)
    if ignore_index is not None:
        loss = loss.masked_fill(non_pad_mask, ops.cast(0, loss.dtype))
        loss_weights = loss_weights.masked_fill(non_pad_mask, ops.cast(0, loss_weights.dtype))
        smooth_loss = smooth_loss.masked_fill(non_pad_mask, ops.cast(0, smooth_loss.dtype))

    loss = loss.squeeze(target_dim)
    smooth_loss = smooth_loss.squeeze(target_dim)

    if reduction == 'sum':
        loss = loss.sum()
        smooth_loss = smooth_loss.sum()
    if reduction == 'mean':
        loss = loss.sum() / loss_weights.sum()
        smooth_loss = smooth_loss.sum() / loss_weights.sum()

    eps_i = label_smoothing / inputs.shape[target_dim]
    loss = (1. - label_smoothing) * loss + eps_i * smooth_loss

    return loss


def nll_loss_ext(input, target, weight=None, ignore_index=-100, reduction='mean'):
    r"""
    Gets the negative log likelihood loss between input and target.

    The nll loss with reduction=none can be described as:

    .. math::

        \ell(x, t)=L=\left\{l_{1}, \ldots, l_{N}\right\}^{\top},
        \quad l_{n}=-w_{t_{n}} x_{n, t_{n}},
        \quad w_{c}=\text { weight }[c] \cdot \mathbb{1}
        \{c \not= \text{ignore_index}\},

    where :math:`x` is the input, :math:`t` is the target, :math:`w` is the weight,
    :math:`N` is the batch size, :math:`c` belonging to :math:`[0, C-1]` is class index,
    where :math:`C` is the number of classes.

    If `reduction` is not ``'none'`` (default ``'mean'``), then

    .. math::

        \ell(x, t)=\left\{\begin{array}{ll}
        \sum_{n=1}^{N} \frac{1}{\sum_{n=1}^{N} w_{t n}} l_{n}, & \text { if reduction }=\text { 'mean', } \\
        \sum_{n=1}^{N} l_{n}, & \text { if reduction }=\text { 'sum' }
        \end{array}\right.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): :math:`(N)` or :math:`(N, C)` where `C = number of classes` , `N = batch size` ,
            or :math:`(N, C, d_1, d_2, ..., d_K)` (for high-dimensional data).
            `input` is expected to be log-probabilities.
            Data type only supports float32 or float16 or bfloat16(only supported by
            Atlas A2 training series products).
        target (Tensor): :math:`()` or :math:`(N)` ,
          where the value range is :math:`[0, C-1]`, or :math:`(N, d_1, d_2, ..., d_K)` for
          high-dimensional loss, data type must be int32 or int64 or uint8.
        weight (Tensor, optional): A rescaling weight applied to the loss of each batch element.
            If not None, the shape is :math:`(C,)`.
            The data type must be float16 or float32 or bfloat16(only supported by Atlas A2 training series products).
            It should have the same data type as `input` . Default: ``None`` .
        ignore_index (int, optional): Specifies a target value that is ignored
            and does not contribute to the input gradient. Default: ``-100`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor. The data type is the same as that of `input`.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, mint
        >>> input = mindspore.Tensor(np.random.randn(3, 5), mindspore.float32)
        >>> target = mindspore.Tensor(np.array([1, 0, 4]), mindspore.int32)
        >>> output = mint.nn.functional.nll_loss(input, target)

    """
    return _nllloss_nd(input, target, weight, ignore_index, reduction)


def _nllloss_nd(input, target, weight=None, ignore_index=-100, reduction='mean'):
    """nllloss_nd inner function"""
    input_dim = input.ndim
    class_dim = 0 if input_dim == 1 else 1
    n_classes = input.shape[class_dim]
    if weight is None:
        weight = ones(n_classes, input.dtype)
    if input_dim < 1:
        raise ValueError(f"input dim should be less than 1, but got {input_dim}")
    if F.isconstant(input_dim) and F.isconstant(target.ndim) and input_dim != 1 and input.shape[0] != target.shape[0]:
        raise ValueError(f"input bacth_size should be equal to target batch_size, but got {input.shape[0]} and "
                         f"{target.shape[0]}")
    if input_dim in [1, 2]:
        return nllloss_impl(input, target, weight, reduction, ignore_index)[0]
    if input_dim == 4:
        return nllloss_2d_op(input, target, weight, reduction, ignore_index)[0]
    # input_dim==3 or input_dim>4
    n = input.shape[0]
    c = input.shape[1]
    out_size = (n,) + input.shape[2:]
    if input.size > 0:
        input = input.view((n, c, 1, -1))
    else:
        input = input.view((n, c, 0, 0))
    if target.size > 0:
        target = target.view((n, 1, -1))
    else:
        target = target.view((n, 0, 0))
    if reduction != 'none':
        return nllloss_2d_op(input, target, weight, reduction, ignore_index)[0]
    ret = nllloss_2d_op(input, target, weight, reduction, ignore_index)[0]
    return ret.view(out_size)


def _cross_entropy_for_probabilities(input, target, weight, reduction, label_smoothing, class_dim, n_classes):
    """cross_entropy inner function for class probabilities"""
    if input.shape != target.shape:
        raise ValueError("For cross_entropy that target is probabilities, input shape should equal to target shape.")
    if label_smoothing > 0.0:
        target = target * (1 - label_smoothing) + label_smoothing / n_classes
    loss = input * target
    if weight is not None:
        weight_ = weight
        ori_shape = loss.shape
        if input.ndim > 2:
            loss = loss.view(ori_shape[:2] + (-1,))
            weight_ = weight_.view(1, -1, 1)
        loss = loss * weight_
        loss = loss.view(ori_shape)
    if reduction == "mean":
        return -div(loss.sum(), (input.size / n_classes))
    if reduction == "sum":
        return -loss.sum()
    if reduction == "none":
        return -loss.sum(class_dim)
    raise ValueError(f"redution value {reduction} not valid.")


def _cross_entropy_for_class_indices(input, target, weight, ignore_index, reduction, label_smoothing, class_dim,
                                     n_classes):
    """cross_entropy inner function for class indices"""
    nllloss = _nllloss_nd(input, target, weight, ignore_index, reduction)
    if label_smoothing > 0.0:
        if weight is not None:
            weight_ = weight
            input_ = input
            ori_shape = input.shape
            if input.ndim > 2:
                input_ = input.view(ori_shape[:2] + (-1,))
                weight_ = weight_.view(1, -1, 1)
            loss = input_ * weight_
            loss = loss.view(ori_shape)
            smooth_loss = -loss.sum(class_dim)
        else:
            smooth_loss = -input.sum(class_dim)
        ignore_mask = ops.eq(target, ignore_index)
        smooth_loss = masked_fill_op(smooth_loss, ignore_mask, 0)
        if reduction == "mean":
            true_mask = ~ignore_mask
            if weight is not None:
                weight_sum = gather_ext(weight, 0, flatten_ext(masked_select(target, true_mask))).sum()
                if weight_sum == 0:
                    ret = smooth_loss.sum()
                else:
                    ret = smooth_loss.sum() / weight_sum
            else:
                weight_sum = true_mask.sum()
                if weight_sum == 0:
                    ret = smooth_loss.sum()
                else:
                    ret = smooth_loss.sum() / weight_sum
        elif reduction == "sum":
            ret = smooth_loss.sum()
        elif reduction == "none":
            ret = smooth_loss
        else:
            raise ValueError(f"redution value {reduction} not valid.")
        return (1 - label_smoothing) * nllloss + ret * (label_smoothing / n_classes)
    return nllloss


def cross_entropy_ext(input, target, weight=None, ignore_index=-100, reduction='mean', label_smoothing=0.0):
    r"""
    The cross entropy loss between input and target.

    The cross entropy supports two kind of targets:

    - Class indices (int) in the range :math:`[0, C)` where :math:`C` is the number of classes,
      the loss with reduction=none can be described as:

      .. math::

          \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad
          l_n = - w_{y_n} \log \frac{\exp(x_{n,y_n})}{\sum_{c=1}^C \exp(x_{n,c})}
          \cdot \mathbb{1}\{y_n \not= \text{ignore_index}\}

      where :math:`x` is the inputs, :math:`y` is the target, :math:`w` is the weight, :math:`N` is the batch size,
      :math:`c` belonging to :math:`[0, C-1]` is class index, where :math:`C` is the number of classes.

      If `reduction` is not ``None`` (default ``'mean'`` ), then

      .. math::

          \ell(x, y) = \begin{cases}
              \sum_{n=1}^N \frac{1}{\sum_{n=1}^N w_{y_n} \cdot \mathbb{1}\{y_n \not= \text{ignore_index}\}} l_n, &
              \text{if reduction} = \text{'mean',}\\
              \sum_{n=1}^N l_n,  &
              \text{if reduction} = \text{'sum'.}
              \end{cases}

    - Probabilities (float) for each class, useful when labels beyond a single class per minibatch item
      are required, the loss with reduction=none can be described as:

      .. math::

          \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad
          l_n = - \sum_{c=1}^C w_c \log \frac{\exp(x_{n,c})}{\sum_{i=1}^C \exp(x_{n,i})} y_{n,c}

      where :math:`x` is the inputs, :math:`y` is the target, :math:`w` is the weight, N is the batch size,
      :math:`c` belonging to :math:`[0, C-1]` is class index, where :math:`C` is the number of classes.

      If `reduction` is not ``None`` (default ``'mean'`` ), then

      .. math::

          \ell(x, y) = \begin{cases}
              \frac{\sum_{n=1}^N l_n}{N}, &
              \text{if reduction} = \text{'mean',}\\
              \sum_{n=1}^N l_n,  &
              \text{if reduction} = \text{'sum'.}
              \end{cases}

    .. warning::
            This is an experimental API that is subject to change or deletion.

    Note:
        Dynamic shape, dynamic rank and variable constant input are not supported in `strict graph mode
        (jit_syntax_level=mindspore.STRICT)
        <https://www.mindspore.cn/tutorials/en/master/compile/static_graph.html>`_.

    Args:
        input (Tensor): :math:`(N)` or :math:`(N, C)` where `C = number of classes` or :math:`(N, C, H, W)`
            in case of 2D Loss, or :math:`(N, C, d_1, d_2, ..., d_K)`.
            `input` is expected to be log-probabilities, data type must be float16 or float32 or bfloat16
            (only supported by Atlas A2 training series products).
        target (Tensor): For class indices, tensor of shape :math:`()`, :math:`(N)` or
            :math:`(N, d_1, d_2, ..., d_K)` , data type must be int32 or int64. For probabilities, tensor of shape
            :math:`(N,)` , :math:`(N, C)` or :math:`(N, C, d_1, d_2, ..., d_K)` , data type must be float16 or float32
            or bfloat16(only supported by Atlas A2 training series products).
        weight (Tensor, optional): A rescaling weight applied to the loss of each batch element.
            If not None, the shape is :math:`(C,)`, data type must be float16 or float32 or bfloat16(only supported by
            Atlas A2 training series products). Default: ``None`` .
        ignore_index (int, optional): Specifies a target value that is ignored and does not contribute to the input
            gradient. Only valid in class indices, please set it to a negative number in probabilities.
            Default: ``-100`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

        label_smoothing (float, optional): Label smoothing values, a regularization tool used to prevent the model
            from overfitting when calculating Loss. The value range is [0.0, 1.0]. Default: ``0.0`` .

    Returns:
        Tensor, the data type is the same as `input` .

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops, Tensor
        >>> import numpy as np
        >>> # Case 1: Indices labels
        >>> inputs = Tensor(np.random.randn(3, 5), ms.float32)
        >>> target = Tensor(np.array([1, 0, 4]), ms.int32)
        >>> output = ops.cross_entropy_ext(inputs, target)
        >>> # Case 2: Probability labels
        >>> inputs = Tensor(np.random.randn(3, 5), ms.float32)
        >>> target = Tensor(np.random.randn(3, 5), ms.float32)
        >>> output = ops.cross_entropy_ext(inputs, target)
    """
    if not isinstance(input, Tensor) or not isinstance(target, Tensor):
        raise TypeError(
            f"For cross_entropy, input and target must be Tensor, but got input:{type(input)}, target:{type(target)}.")
    if weight is not None and not isinstance(weight, Tensor):
        raise TypeError(f"For cross_entropy, weight must be Tensor or None, but got {type(weight)}.")
    if label_smoothing < 0.0 or label_smoothing > 1.0:
        raise ValueError(f"For cross_entropy, label_smoothing must in [0, 1]")
    if input.ndim == 0 or input.shape[0] == 0:
        raise ValueError(f"For cross_entropy, input don't support 0-dim and shape[0].")
    class_dim = 0 if input.ndim == 1 else 1
    n_classes = input.shape[class_dim]
    input = log_softmax_ext(input, class_dim, dtype=input.dtype)
    # for probabilities
    target_dtype = target.dtype
    if isinstance(target_dtype, type(mstype.tensor_type)):
        target_dtype = target_dtype.element_type()
    if target_dtype in mstype.float_type:
        return _cross_entropy_for_probabilities(input, target, weight, reduction, label_smoothing, class_dim,
                                                n_classes)
    # for class indices
    return _cross_entropy_for_class_indices(input, target, weight, ignore_index, reduction, label_smoothing,
                                            class_dim, n_classes)


def l1_loss(input, target, reduction='mean'):
    r"""
    Calculate the mean absolute error between the `input` value and the `target` value.

    Assuming that the :math:`x` and :math:`y` (predicted and target value) are 1-D Tensor,
    length :math:`N`, `reduction` is set to ``'none'``, then calculate the loss of
    :math:`x` and :math:`y` without dimensionality reduction.

    The formula is as follows:

    .. math::
        \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad \text{with } l_n = \left| x_n - y_n \right|,

    where :math:`N` is the batch size.

    If `reduction` is set to ``'mean'`` or ``'sum'`` , then:

    .. math::
        \ell(x, y) =
        \begin{cases}
            \operatorname{mean}(L), & \text{if reduction} = \text{'mean';}\\
            \operatorname{sum}(L),  & \text{if reduction} = \text{'sum'.}
        \end{cases}

    Args:
        input (Tensor): Predicted value, Tensor of any dimension.
        target (Tensor): Target value, usually has the same shape as the `input`.
            If `input` and `target` have different shape, make sure they can broadcast to each other.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Scalar, if `reduction` is ``'none'``, return a Tensor with same shape and dtype as `input`.
        Otherwise, a scalar value will be returned.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `target` is not a Tensor.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'`` or ``'sum'``.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> x = Tensor([[1, 2, 3], [4, 5, 6]], mstype.float32)
        >>> target = Tensor([[6, 5, 4], [3, 2, 1]], mstype.float32)
        >>> output = ops.l1_loss(x, target, reduction="mean")
        >>> print(output)
        3.0
    """
    _check_is_tensor('input', input, "l1_loss")
    _check_is_tensor('target', target, "l1_loss")
    if reduction not in ('mean', 'sum', 'none'):
        raise ValueError(f"For l1_loss, the 'reduction' must be in ['mean', 'sum', 'none'], but got {reduction}.")
    loss = abs_(input - target)
    return _get_loss(loss, reduction, "l1_loss")


def smooth_l1_loss(input, target, beta=1.0, reduction='none'):
    r"""
    Computes smooth L1 loss, a robust L1 loss.

    SmoothL1Loss is a Loss similar to MSELoss but less sensitive to outliers as described in the
    `Fast R-CNN <https://arxiv.org/abs/1504.08083>`_ by Ross Girshick.

    Given two input :math:`x,\  y` of length :math:`N`, the unreduced SmoothL1Loss can be described
    as follows:

    .. math::
        L_{i} =
        \begin{cases}
        \frac{0.5 (x_i - y_i)^{2}}{\text{beta}}, & \text{if } |x_i - y_i| < \text{beta} \\
        |x_i - y_i| - 0.5 * \text{beta}, & \text{otherwise. }
        \end{cases}

    If `reduction` is not `none`, then:

    .. math::
        L =
        \begin{cases}
            \operatorname{mean}(L_{i}), &  \text{if reduction} = \text{'mean';}\\
            \operatorname{sum}(L_{i}),  &  \text{if reduction} = \text{'sum'.}
        \end{cases}

    Here :math:`\text{beta}` controls the point where the loss function changes from quadratic to linear.
    :math:`\text{beta}>0` , its default value is ``1.0`` . :math:`N` is the batch size.

    .. warning::
        This API has poor performance on CPU and it is recommended to run it on the Ascend/GPU.

    Args:
        input (Tensor): Tensor of shape :math:`(N, *)` where :math:`*` means,
            any number of additional dimensions.Supported dtypes:

            - Ascend: float16, float32, bfloat16.
            - CPU/GPU: float16, float32, float64.
        target (Tensor): Ground truth data, tensor of shape :math:`(N, *)`.

            - CPU/Ascend: has the same shape as the `input`, `target` and `input`
              comply with the implicit type conversion rules to make the data types consistent.
            - GPU: has the same shape and dtype as the `input`.

        beta (number, optional): A parameter used to control the point where the function will change between
            L1 to L2 loss. Default: ``1.0`` .

            - Ascend: The value should be equal to or greater than zero.
            - CPU/GPU: The value should be greater than zero.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'none'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor, if `reduction` is ``'none'``, then output is a tensor with the same shape as `input`.
        Otherwise, the shape of output tensor is :math:`()`.

    Raises:
        TypeError: If input `input`, `target` is not Tensor.
        RuntimeError: If dtype of `input` or `target` is not one of float16, float32, float64, bfloat16.
        ValueError: If shape of `input` is not the same as `target`.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``.
        TypeError: If `beta` is not a float, int or bool.
        RuntimeError: If `beta` is less than or equal to 0.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> logits = Tensor(np.array([1, 2, 3]), mindspore.float32)
        >>> labels = Tensor(np.array([1, 2, 2]), mindspore.float32)
        >>> output = ops.smooth_l1_loss(logits, labels)
        >>> print(output)
        [0.  0.  0.5]
    """
    if beta == 0.0:
        return l1_loss_ext(input, target, reduction)
    return ops.auto_generate.smooth_l1_loss(input, target, beta=beta, reduction=reduction)


def threshold(input, thr, value):
    r"""
    Returns each element of `input` after thresholding by `thr` as a Tensor.

    The formula is defined as follows:

    .. math::
        y =
        \begin{cases}
        input, &\text{ if } input > \text{thr} \\
        \text{value}, &\text{ otherwise }
        \end{cases}

    Args:
        input (Tensor): The input of threshold with data type of float16 or float32.
        thr (Union[int, float]): The value of the threshold.
        value (Union[int, float]): The value to replace with when element is less than threshold.

    Returns:
        Tensor, the same shape and data type as the input.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `thr` is not a float or an int.
        TypeError: If `value` is not a float or an int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> inputs = mindspore.Tensor([0.0, 2, 3], mindspore.float32)
        >>> outputs = ops.threshold(inputs, 1, 100)
        >>> print(outputs)
        [100.   2.   3.]
    """
    _check_is_tensor('input', input, "threshold")
    _check_value_type("thr", thr, [float, int], "threshold")
    _check_value_type("value", value, [float, int], "threshold")
    cond = greater_(input, thr)
    input_type = input.dtype
    value = Tensor(value, input_type)
    input_shape = input.shape
    shape_tensor = tuple_to_tensor_(input_shape, mstype.int64)
    value = fillv2_(shape_tensor, value)
    return select_(cond, input, value)


def leaky_relu(input, alpha=0.2):
    r"""
    leaky_relu activation function. The element of `input` less than 0 times `alpha` .

    The activation function is defined as:

    .. math::
        \text{leaky_relu}(input) = \begin{cases}input, &\text{if } input \geq 0; \cr
        {\alpha} * input, &\text{otherwise.}\end{cases}

    where :math:`\alpha` represents the `alpha` parameter.

    For more details, see `Rectifier Nonlinearities Improve Neural Network Acoustic Models
    <https://ai.stanford.edu/~amaas/papers/relu_hybrid_icml2013_final.pdf>`_.

    LeakyReLU Activation Function Graph:

    .. image:: ../images/LeakyReLU.png
        :align: center

    Args:
        input (Tensor): The input of leaky_relu is a Tensor of any dimension.
        alpha (Union[int, float], optional): Slope of the activation function when
            the element of `input` is less than 0. Default: ``0.2`` .

    Returns:
        Tensor, has the same type and shape as the `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `alpha` is not a float or an int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> print(ops.leaky_relu(x, alpha=0.2))
        [[-0.2  4.  -1.6]
         [ 2.  -1.   9. ]]
    """
    _check_is_tensor('input', input, "leaky_relu")
    _check_value_type("alpha", alpha, [float, int], "leaky_relu")
    select_op = maximum_
    if alpha > 1:
        select_op = minimum_
    alpha = cast_(F.scalar_to_tensor(alpha), input.dtype)
    return select_op(alpha * input, input)


def intopk(x1, x2, k):
    r"""
    Return whether the elements in second input tensor exist among the top `k` elements of the first input tensor.

    Args:
        x1 (Tensor): The 2-D input tensor.
        x2 (Tensor): The 1-D input tensor, should satisfy :math:`x2.shape[0] = x1.shape[0]` .
        k (int): Top `k` elements.

    Returns:
        A 1-D tensor whose data type is bool, has the same shape with `x2`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> x1 = mindspore.tensor([[1, 8, 5, 2, 7], [4, 9, 1, 3, 5]], mindspore.float32)
        >>> x2 = mindspore.tensor([1, 3], mindspore.int32)
        >>> mindspore.ops.intopk(x1, x2, 3)
        Tensor(shape=[2], dtype=Bool, value= [ True, False])
    """
    _in_topk = _get_cache_prim(P.InTopK)(k)
    return _in_topk(x1, x2)


def lrn(x, depth_radius=5, bias=1.0, alpha=1.0, beta=0.5, norm_region="ACROSS_CHANNELS"):
    r"""
    Local Response Normalization.

    .. warning::
        lrn is deprecated on Ascend due to potential accuracy problem. It's recommended to use other
        normalization methods, e.g. :class:`mindspore.ops.batch_norm`.

    .. math::

        b_{c} = a_{c}\left(k + \frac{\alpha}{n}
        \sum_{c'=\max(0, c-n/2)}^{\min(N-1,c+n/2)}a_{c'}^2\right)^{-\beta}

    where the :math:`a_{c}` indicates the specific value of the pixel corresponding to :math:`c` in feature map;
    where the :math:`n/2` indicates the `depth_radius`; where the :math:`k` indicates the `bias`;
    where the :math:`\alpha` indicates the `alpha`; where the :math:`\beta` indicates the `beta`.

    Args:
        depth_radius (int): Half-width of the 1-D normalization window with the shape of 0-D. Default: ``5`` .
        bias (float): An offset (usually positive to avoid dividing by 0). Default: ``1.0`` .
        alpha (float): A scale factor, usually positive. Default: ``1.0`` .
        beta (float): An exponent. Default: ``0.5`` .
        norm_region (str): Specifies normalization region. Options: ``"ACROSS_CHANNELS"`` .
            Default: ``"ACROSS_CHANNELS"`` .
        x (Tensor): A 4-D Tensor with float16 or float32 data type.

    Returns:
        Tensor, with the same shape and data type as `x`.

    Raises:
        TypeError: If `depth_radius` is not an int.
        TypeError: If `bias`, `alpha` or `beta` is not a float.
        TypeError: If `norm_region` is not a str.
        TypeError: If `x` is not a Tensor.

    Supported Platforms:
        ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.array([[[[0.1], [0.2]],
        ...                       [[0.3], [0.4]]]]), mindspore.float32)
        >>> output = ops.lrn(input_x)
        >>> print(output)
        [[[[0.09534626]
           [0.1825742 ]]
          [[0.2860388 ]
           [0.3651484 ]]]]
    """
    lrn_op = NN_OPS.LRN(depth_radius, bias, alpha, beta, norm_region)
    return lrn_op(x)


def mish(x):
    r"""
    Computes MISH(A Self Regularized Non-Monotonic Neural Activation Function) of input tensors element-wise.

    The function is shown as follows:

    .. math::

        \text{output} = x * \tanh(\log(1 + \exp(\text{x})))

    See more details in `A Self Regularized Non-Monotonic Neural Activation Function
    <https://arxiv.org/abs/1908.08681>`_.

    Mish Activation Function Graph:

    .. image:: ../images/Mish.png
        :align: center

    Args:
        x (Tensor): The input Tensor.
            Supported dtypes:

            - GPU/CPU: float16, float32, float64.
            - Ascend: float16, float32.

    Returns:
        Tensor, with the same type and shape as the `x`.

    Raises:
        TypeError: If dtype of `x` is not float16, float32 or float64.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> output = ops.mish(input_x)
        >>> print(output)
        [[-3.0340147e-01  3.9974129e+00 -2.68311895e-03]
         [ 1.9439590e+00  -3.3576239e-02 8.99999990e+00]]
        >>> input_x = Tensor(2.1, mindspore.float32)
        >>> output = ops.mish(input_x)
        >>> print(output)
        2.050599
    """
    return mish_(x)


@_primexpr
def _check_value_type(arg_name, arg_value, valid_types, prim_name=None):
    """Checks whether a value is instance of some types."""
    return validator.check_value_type(arg_name, arg_value, valid_types, prim_name)


@constexpr(check=False)
def _check_is_tensor(param_name, input_data, cls_name):
    """Internal function, used to check whether the input data is Tensor."""
    if input_data is not None and not isinstance(ops.typeof(input_data), mstype.TensorType):
        raise TypeError(f"For '{cls_name}', the '{param_name}' must be a Tensor, "
                        f"but got '{ops.typeof(input_data)}'")


@constexpr
def _check_number_gt_value(arg_name, arg_value, value, cls_name):
    """Internal function, used to judge whether arg_value is greater than or equal to value."""
    return validator.check_number(arg_name, arg_value, value, validator.GT, cls_name)


def _get_axis(x):
    """Get a range of axis for input."""
    shape = ops.shape(x)
    length = ops.tuple_len(shape)
    perm = ops.make_range(0, length)
    return perm


def _get_loss(x, reduction, cls_name, weights=1.0):
    """Calculate the loss with reduction and weights."""
    if reduction not in ('mean', 'sum', 'none'):
        raise ValueError(f"For '{cls_name}', the 'reduction' must be in ['mean', 'sum', 'none'], "
                         f"but got {reduction}.")
    input_dtype = x.dtype
    x = cast_(x, mstype.float32)
    weights = cast_(weights, mstype.float32)
    x = mul_(weights, x)
    if reduction == 'mean':
        x = reduce_mean_(x, _get_axis(x))
    if reduction == 'sum':
        x = reduce_sum_(x, _get_axis(x))
    x = cast_(x, input_dtype)
    return x


def check_input_dtype(param_name1, input_data1, param_name2, input_data2, cls_name):
    """Check the type of input1 and input2."""
    if input_data1.dtype != input_data2.dtype:
        raise TypeError(f'For {cls_name}, the {param_name1} dtype should be equal to {param_name2} dtype, '
                        f'but got {param_name1} dtype:{input_data1.dtype}, {param_name2} dtype:{input_data2.dtype}.')


def margin_ranking_loss(input1, input2, target, margin=0.0, reduction='mean'):
    r"""
    MarginRankingLoss creates a criterion that measures the loss.

    Given two tensors :math:`input1`, :math:`input2` and a Tensor label :math:`target` with values 1 or -1,
    the operation is as follows:

    .. math::
        \text{loss}(input1, input2, target) = \max(0, -target * (input1 - input2) + \text{margin})

    Args:
        input1 (Tensor): Tensor of shape :math:`(N, *)` where :math:`*` means, any number of additional dimensions.
        input2 (Tensor): Tensor of shape :math:`(N, *)`, same shape and dtype as `input1`.
        target (Tensor): Contains value 1 or -1. Suppose the shape of `input1` is
          :math:`(x_1, x_2, x_3, ..., x_R)`, then the shape of `target` must be :math:`(x_1, x_2, x_3, ..., x_R)`.
        margin (float, optional): Specify the adjustment factor of the operation. Default: ``0.0`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Scalar. if `reduction` is ``'none'``, its shape is the same as `input1`.
        Otherwise, a scalar value will be returned.

    Raises:
        TypeError: If `margin` is not a float.
        TypeError: If `input1`, `input2` or `target` is not a Tensor.
        TypeError: If the types of `input1` and `input2` are inconsistent.
        TypeError: If the types of `input1` and `target` are inconsistent.
        ValueError: If the shape of `input1` and `input2` are inconsistent.
        ValueError: If the shape of `input1` and `target` are inconsistent.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'`` , ``'sum'``.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import Tensor, ops
        >>> import numpy as np
        >>> input1 = Tensor(np.array([0.3864, -2.4093, -1.4076]), ms.float32)
        >>> input2 = Tensor(np.array([-0.6012, -1.6681, 1.2928]), ms.float32)
        >>> target = ops.Sign()(Tensor(np.array([-2, -2, 3]), ms.float32))
        >>> output = ops.margin_ranking_loss(input1, input2, target)
        >>> print(output)
        1.2293333
    """
    margin = _check_value_type("margin", margin, [float], "margin_ranking_loss")
    _check_is_tensor('input1', input1, "margin_ranking_loss")
    _check_is_tensor('input2', input2, "margin_ranking_loss")
    _check_is_tensor('target', target, "margin_ranking_loss")
    check_input_dtype('input1', input1, 'input2', input2, 'margin_ranking_loss')
    check_input_dtype('target', target, 'input1', input1, 'margin_ranking_loss')
    x = maximum_(-target * (input1 - input2) + margin, 0)
    return _get_loss(x, reduction, "margin_ranking_loss")


@_primexpr
def _check_reduced_shape_valid(ori_shape, reduced_shape, axis, cls_name, arg_name1, arg_name2):
    """Internal function, used to check whether the reduced shape meets the requirements."""
    validator.check_reduce_shape(ori_shape, reduced_shape, axis, cls_name, arg_name1, arg_name2)


def cosine_embedding_loss(input1, input2, target, margin=0.0, reduction="mean"):
    r"""
    CosineEmbeddingLoss creates a criterion to measure the similarity between two tensors using cosine distance.

    Given two tensors :math:`input1`, :math:`input2`, and a Tensor label :math:`target` with values 1 or -1:

    .. math::
        loss(input1, input2, target) = \begin{cases}
        1-cos(input1, input2), & \text{if } target = 1\\
        max(0, cos(input1, input2)-margin), & \text{if } target = -1\\
        \end{cases}

    Args:
        input1 (Tensor): Tensor of shape :math:`(N, *)` where :math:`*` means, any number
          of additional dimensions.
        input2 (Tensor): Tensor of shape :math:`(N, *)`, same shape and dtype as `input1`.
        target (Tensor): Contains value 1 or -1. Suppose the shape of `input1` is
          :math:`(x_1, x_2, x_3, ..., x_R)`, then the shape of `target` must be :math:`(x_1, x_3, x_4, ..., x_R)`.
        margin (float, optional): Should be in [-1.0, 1.0]. Default: ``0.0``.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Scalar, if `reduction` is ``"none"``, its shape is the same as `target`.
        Otherwise, a scalar value will be returned.

    Raises:
        TypeError: If `margin` is not a float.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``.
        ValueError: If `margin` is not in range [-1.0, 1.0].

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> intput1 = Tensor(np.array([[0.3, 0.8], [0.4, 0.3]]), mindspore.float32)
        >>> intput2 = Tensor(np.array([[0.4, 1.2], [-0.4, -0.9]]), mindspore.float32)
        >>> target = Tensor(np.array([1, -1]), mindspore.int32)
        >>> output = ops.cosine_embedding_loss(intput1, intput2, target)
        >>> print(output)
        0.0003425479
    """

    _check_is_tensor('input1', input1, "ops.cosine_embedding_loss")
    _check_is_tensor('input2', input2, "ops.cosine_embedding_loss")
    _check_is_tensor('target', target, "ops.cosine_embedding_loss")
    check_input_dtype('input1', input1, 'input2', input2, 'ops.cosine_embedding_loss')
    _check_reduced_shape_valid(ops.shape(input1), ops.shape(target), (1,),
                               "ops.cosine_embedding_loss", "input1", "target")
    if input1.dtype in (mstype.int32, mstype.int64):
        input1 = input1.astype(mstype.float32)
    if input2.dtype in (mstype.int32, mstype.int64):
        input2 = input2.astype(mstype.float32)
    margin_f = float(margin) if isinstance(margin, int) else margin
    _check_value_type("margin", margin_f, [float], "ops.cosine_embedding_loss")
    if not isinstance(margin_f, float):
        raise TypeError(f"For ops.cosine_embedding_loss, 'margin' must be float, but got {type(margin_f)}")
    if margin_f > 1.0 or margin_f < -1.0:
        raise ValueError(f"For ops.cosine_embedding_loss, the value of 'margin' should be in [-1, 1],"
                         f"but got {margin_f}.")
    prod_sum = reduce_sum_(input1 * input2, (1,))
    square1 = reduce_sum_(ops.square(input1), (1,))
    square2 = reduce_sum_(ops.square(input2), (1,))
    denom = ops.sqrt(square1) * ops.sqrt(square2)
    cosine = prod_sum / denom

    pos_value = 1.0 - cosine
    neg_value = maximum_(cosine - margin_f, 0.0)
    zeros = ops.zeros_like(cosine)
    pos_part = ops.select(target == 1, pos_value, zeros)
    neg_part = ops.select(target == -1, neg_value, zeros)
    output_unreduced = pos_part + neg_part

    return _get_loss(output_unreduced, reduction, "cosine_embedding_loss")


def max_pool3d(x, kernel_size, stride=None, padding=0, dilation=1, ceil_mode=False, return_indices=False):
    r"""
    Performs a 3D max pooling on the input Tensor.

    Typically the input is a Tensor with shape :math:`(N_{in}, C_{in}, D_{in}, H_{in}, W_{in})`, outputs
    regional maximum in the :math:`(D_{in}, H_{in}, W_{in})`-dimension. Given `kernel_size`
    :math:`ks = (d_{ker}, h_{ker}, w_{ker})` and `stride` :math:`s = (s_0, s_1, s_2)`, the operation is as follows:

    .. math::
        \text{output}(N_i, C_j, d, h, w) =
        \max_{l=0, \ldots, d_{ker}-1} \max_{m=0, \ldots, h_{ker}-1} \max_{n=0, \ldots, w_{ker}-1}
        \text{input}(N_i, C_j, s_0 \times d + l, s_1 \times h + m, s_2 \times w + n)

    Args:
        x (Tensor): Tensor of shape :math:`(N_{in}, C_{in}, D_{in}, H_{in}, W_{in})` with data type of int8,
            int16, int32, int64, uint8, uint16, uint32, uint64, float16, float32 or float64.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value and arg
            value, is an int number that represents depth, height and width of the kernel, or a tuple of
            three int numbers that represent depth, height and width respectively.
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents
            the depth, height and width of movement are both stride, or a tuple of three int numbers that
            represent depth, height and width of movement respectively.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]]): An int number that represents the depth, height and width of movement are both
            strides, or a tuple of three int numbers that represent depth, height and width of movement respectively.
            Default: ``0`` .
        dilation (Union[int, tuple[int]]): Control the stride of elements in the kernel. Default: ``1`` .
        ceil_mode (bool): Whether to use ceil instead of floor to calculate output shape. Default: ``False`` .
        return_indices (bool): Whether to output the indices of max value. Default: ``False`` .

    Returns:
        If `return_indices` is False, return a Tensor `output`, else return a tuple (`output`, `argmax`).

        - **output** (Tensor) - Maxpooling result, with shape :math:`(N_{out}, C_{out}, D_{out}, H_{out}, W_{out})`.
          It has the same data type as `x`.

        .. math::
            D_{out} = \left\lfloor\frac{D_{in} + 2 \times \text{padding}[0] - \text{dilation}[0] \times
            (\text{kernel_size}[0] - 1) - 1}{\text{stride}[0]} + 1\right\rfloor

        .. math::
            H_{out} = \left\lfloor\frac{H_{in} + 2 \times \text{padding}[1] - \text{dilation}[1] \times
            (\text{kernel_size}[1] - 1) - 1}{\text{stride}[1]} + 1\right\rfloor

        .. math::
            W_{out} = \left\lfloor\frac{W_{in} + 2 \times \text{padding}[2] - \text{dilation}[2] \times
            (\text{kernel_size}[2] - 1) - 1}{\text{stride}[2]} + 1\right\rfloor

        - **argmax** (Tensor) - Index corresponding to the maximum value. Data type is int64. It will be returned
          only when `return_indices` is ``True`` .

    Raises:
        TypeError: If `x` is not a Tensor.
        ValueError: If length of shape of `x` is not equal to 5.
        TypeError: If `kernel_size` , `stride` , `padding` or `dilation` is not int or tuple.
        ValueError: If `kernel_size` or `stride` is less than 1.
        ValueError: If `padding` is less than 0.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.arange(2 * 1 * 2 * 2 * 2).reshape((2, 1, 2, 2, 2)), mindspore.float32)
        >>> output_tensor, argmax = ops.max_pool3d(x, kernel_size=2, stride=1, padding=1, return_indices=True)
        >>> print(output_tensor.shape)
        (2, 1, 3, 3, 3)
        >>> print(argmax.shape)
        (2, 1, 3, 3, 3)
    """
    strides = stride if (stride is not None) else kernel_size
    max_pool3d_with_argmax_ = _get_cache_prim(NN_OPS.MaxPool3DWithArgmax)(
        kernel_size, strides, padding, dilation, ceil_mode)
    out, indices = max_pool3d_with_argmax_(x)
    if return_indices:
        return out, indices
    return out


def grid_sample(input, grid, mode='bilinear', padding_mode='zeros', align_corners=None):
    """
    Given an `input` and a flow-field `grid`, computes the `output` using `input` values and pixel locations from
    `grid`. Only spatial (4-D) and volumetric (5-D) `input` is supported.

    In the spatial (4-D) case, for `input` with shape :math:`(N, C, H_{in}, W_{in})` and `grid` with shape
    :math:`(N, H_{out}, W_{out}, 2)`, the `output` will have shape :math:`(N, C, H_{out}, W_{out})`.

    For each output location `output[n, :, h, w]`, the size-2 vector `grid[n, h, w]` specifies `input` pixel
    locations `x` and `y`, which are used to interpolate the output value `output[n, :, h, w]`. In the case of 5D
    inputs, `grid[n, d, h, w]`, specifies the `x`, `y`, `z` pixel locations for interpolating
    `output[n, :, d, h, w]`. And `mode` argument specifies "nearest" or "bilinear" ("bicubic" is not supported yet)
    interpolation method to sample the input pixels.

    `grid` specifies the sampling pixel locations normalized by the `input` spatial dimensions. Therefore, it should
    have most values in the range of :math:`[-1, 1]`.

    If `grid` has values outside the range of :math:`[-1, 1]`, the corresponding outputs are handled as defined by
    `padding_mode`. If `padding_mode` is set to be "zeros", use :math:`0` for out-of-bound grid locations. If
    `padding_mode` is set to be "border", use border values for out-of-bound grid locations. If `padding_mode` is set
    to be "reflection", use values at locations reflected by the border for out-of-bound grid locations. For location
    far away from the border, it will keep being reflected until becoming in bound.

    Args:
        input (Tensor): input with shape of :math:`(N, C, H_{in}, W_{in})` (4-D case) or :math:`(N, C, D_{in},
            H_{in}, W_{in})` (5-D case) and dtype of float32 or float64.
        grid (Tensor): flow-field with shape of :math:`(N, H_{out}, W_{out}, 2)` (4-D case) or :math:`(N, D_{out},
            H_{out}, W_{out}, 3)` (5-D case) and same dtype as `input`.
        mode (str, optional): An optional string specifying the interpolation method. The optional values are
            ``'bilinear'``, ``'nearest'``. Default: ``'bilinear'`` . Note: `bicubic` is not supported yet. When
            `mode="bilinear"` and the input is 5-D, the interpolation mode used internally will actually
            be trilinear. However, when the input is 4-D, the interpolation mode will legistimately be bilinear.
            Default: ``'bilinear'`` .

            - ``'nearest'``: Nearest neighbor interpolation. Each output pixel is assigned the value of the
              nearest input pixel. This method is simple and fast but can result in blocky or pixelated outputs.
            - ``'bilinear'``: Bilinear interpolation. Each output pixel is a weighted average of the four nearest input
              pixels, computed using bilinear interpolation. This method produces smoother results compared
              to nearest neighbor interpolation.
            - ``'trilinear'``: Trilinear interpolation. This is an extension of bilinear interpolation to 3D data.
              It performs bilinear interpolation in the two spatial dimensions and linear interpolation along
              the third dimension. It is commonly used for volume or 3D image interpolation.

        padding_mode (str, optional): An optional string specifying the pad method.
            The optional values are "zeros", "border" or
            "reflection". Default: ``'zeros'`` .
        align_corners (bool, optional): If set to ``True``, the extrema (-1 and 1) are considered as referring to
            the center points of the input's corner pixels. If set to `False`, they are instead considered as referring
            to the corner points of the input's corner pixels, making the sampling more resolution agnostic. Default:
            ``None``, which is the same as ``False`` .

    Returns:
        Tensor, dtype is the same as `input` and whose shape is :math:`(N, C, H_{out}, W_{out})` (4-D) and
        :math:`(N, C, D_{out}, H_{out}, W_{out})` (5-D).

    Raises:
        TypeError: If `input` or `grid` is not a Tensor.
        TypeError: If the dtypes of `input` and `grid` are inconsistent.
        TypeError: If the dtype of `input` or `grid` is not a valid type.
        TypeError: If `align_corners` is not a boolean value.
        ValueError: If the rank of `input` or `grid` is not equal to 4(4-D case) or 5(5-D case).
        ValueError: If the first dimension of `input` is not equal to that of `grid`.
        ValueError: If the last dimension of `grid` is not equal to 2(4-D case) or 3(5-D case).
        ValueError: If `mode` is not "bilinear", "nearest" or a string value.
        ValueError: If `padding_mode` is not "zeros", "border", "reflection" or a string value.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.arange(16).reshape((2, 2, 2, 2)).astype(np.float32))
        >>> grid = Tensor(np.arange(0.2, 1, 0.1).reshape((2, 2, 1, 2)).astype(np.float32))
        >>> output = ops.grid_sample(input_x, grid, mode='bilinear', padding_mode='zeros',
        ...                          align_corners=True)
        >>> print(output)
        [[[[ 1.9      ]
           [ 2.1999998]]
          [[ 5.9      ]
           [ 6.2      ]]]
         [[[10.5      ]
           [10.8      ]]
          [[14.5      ]
           [14.8      ]]]]
    """
    align_corners = False if align_corners is None else align_corners
    if input.ndim == 4:
        return grid_sampler_2d_impl(input, grid, mode, padding_mode, align_corners)
    return grid_sampler_3d_impl(input, grid, mode, padding_mode, align_corners)


@constexpr
def _check_ctc_loss_inputs(blank, reduction, zero_infinity, prim_name):
    validator.check_value_type("blank", blank, [int], prim_name)
    validator.check_value_type('reduction', reduction, [str], prim_name)
    validator.check_string(reduction, ['none', 'sum', 'mean'], 'reduction', prim_name)
    validator.check_value_type("zero_infinity", zero_infinity, [bool], prim_name)


def ctc_loss(log_probs, targets, input_lengths, target_lengths, blank=0, reduction="mean", zero_infinity=False):
    """
    Calculates the CTC (Connectionist Temporal Classification) loss and the gradient.

    CTC is a loss function in sequence labeling problems, which is mainly used to deal with the alignment of input
    and output labels in sequence labeling problems.
    While traditional sequence labeling algorithms require the input and output symbols to be perfectly aligned at
    each moment, CTC expands the label collection and adds empty elements.
    After labeling the sequence using the extended label set, all the prediction sequences that can be converted
    into real sequences by the mapping function are correct prediction results, that is, the predicted sequence
    can be obtained without data alignment processing.
    Its objective function is to maximize the sum of probabilities of all correct prediction sequences.

    The CTC algorithm is proposed in `Connectionist Temporal Classification: Labeling Unsegmented Sequence Data with
    Recurrent Neural Networks <http://www.cs.toronto.edu/~graves/icml_2006.pdf>`_.

    Args:
        log_probs (Tensor): A tensor of shape :math:`(T, N, C)`, where T is input length, N is batch size and C is
            number of classes (including blank).
        targets (Tensor): Target sequences. A tensor of shape :math:`(N, S)`, where S is max target length.
        input_lengths (Union(tuple, Tensor)): Lengths of the input. A tuple or Tensor of shape :math:`(N)`.
        target_lengths (Union(tuple, Tensor)): Lengths of the target. A tuple or Tensor of shape :math:`(N)`.
        blank (int, optional): The blank label. Default: ``0`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

        zero_infinity (bool, optional): Whether to set infinite loss and correlation gradient to 0. Default: ``False`` .

    Returns:
        neg_log_likelihood (Tensor), A loss value with shape :math:`(N)` , which is differentiable with respect to
        each input node.

        log_alpha (Tensor), The probability of possible trace of input to target with shape :math:`(N, T, 2 * S + 1)` .

    Raises:
        TypeError: If `zero_infinity` is not a bool, `reduction` is not string.
        TypeError: If the dtype of `log_probs` is not float or double.
        TypeError: If the dtype of `targets`, `input_lengths` or `target_lengths` is not int32 or int64.
        ValueError: If the rank of `log_probs` is not 3.
        ValueError: If the rank of `targets` is not 2.
        ValueError: If the shape of `input_lengths` does not match N. N is batch size of `log_probs` .
        ValueError: If the shape of `target_lengths` does not match N. N is batch size of `log_probs` .
        ValueError: If the value of `blank` is not in range [0, num_labels|C). C is number of classes of `log_probs` .
        RuntimeError: If any value of `input_lengths` is larger than T. T is the length of `log_probs`.
        RuntimeError: If any target_lengths[i] is not in range [0, input_length[i]].

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> log_probs = Tensor(np.array([[[0.3, 0.6, 0.6]],
        ...                              [[0.9, 0.4, 0.2]]]).astype(np.float32))
        >>> targets = Tensor(np.array([[0, 1]]), mstype.int32)
        >>> input_lengths = Tensor(np.array([2]), mstype.int32)
        >>> target_lengths = Tensor(np.array([1]), mstype.int32)
        >>> loss, log_alpha = ops.ctc_loss(log_probs, targets, input_lengths,
        ...                                target_lengths, 0, 'mean', True)
        >>> print(loss)
        -2.2986124
        >>> print(log_alpha)
        [[[0.3       0.3            -inf      -inf      -inf]
          [1.2       1.8931472 1.2            -inf      -inf]]]
    """
    _check_ctc_loss_inputs(blank, reduction, zero_infinity, 'ctc_loss')
    ctc_loss_op = NN_OPS.CTCLossV2(blank=blank, reduction="none", zero_infinity=zero_infinity)
    loss, log_alpha = ctc_loss_op(log_probs, targets, input_lengths, target_lengths)
    if reduction == 'sum':
        loss = loss.sum()
    if reduction == 'mean':
        input_type = loss.dtype
        target_length_t = target_lengths.clip(1., None)
        loss = loss.astype("float32")
        loss = loss / target_length_t
        loss = loss.mean()
        loss = loss.astype(input_type)
    return (loss, log_alpha)


def gaussian_nll_loss(x, target, var, full=False, eps=1e-6, reduction='mean'):
    r"""
    Gaussian negative log likelihood loss.

    The target values are considered to be samples from a Gaussian distribution, where the expectation and variance are
    predicted by a neural network. For `labels` modeled on a Gaussian distribution, `logits` to record expectations,
    and the variance `var` (elements are all positive), the calculated loss is:

    .. math::
        \text{loss} = \frac{1}{2}\left(\log\left(\text{max}\left(\text{var},
        \ \text{eps}\right)\right) + \frac{\left(\text{x} - \text{target}\right)^2}
        {\text{max}\left(\text{var}, \ \text{eps}\right)}\right) + \text{const.}

    where :math:`eps` is used for stability of :math:`log`. When :math:`full=True`, a constant will be added to the
    loss. If the shape of :math:`var` and :math:`logits` are not the same (due to a homoscedastic assumption),
    their shapes must allow correct broadcasting.

    Args:
        x (Tensor): Tensor of shape :math:`(N, *)` or :math:`(*)` where :math:`*` means any number of
            additional dimensions.
        target (Tensor): Tensor of shape :math:`(N, *)` or :math:`(*)`, same shape as the x, or same shape
            as the x but with one dimension equal to 1 (to allow broadcasting).
        var (Tensor): Tensor of shape :math:`(N, *)` or :math:`(*)`, same shape as x, or same shape as the x
            but with one dimension equal to 1, or same shape as the x but with one fewer dimension
            (to allow for broadcasting).
        full (bool, optional): Include the constant term in the loss calculation. When :math:`full=True`,
            the constant term will be :math:`const = 0.5*log(2\pi)`. Default: ``False``.
        eps (float, optional): Used to improve the stability of log function must be greater than 0. Default: ``1e-6`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Tensor scalar, the computed loss depending on :math:`reduction`.

    Raises:
        TypeError: If `x`, `target` or `var` is not a Tensor.
        TypeError: If `full` is not a bool.
        TypeError: If `eps` is not a float.
        ValueError: If `eps` is not a float within (0, inf).
        ValueError: If `reduction` is not one of ``"none"`` , ``"mean"`` , ``"sum"`` .

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> import mindspore.common.dtype as mstype
        >>> arr1 = np.arange(8).reshape((4, 2))
        >>> arr2 = np.array([2, 3, 1, 4, 6, 4, 4, 9]).reshape((4, 2))
        >>> x = Tensor(arr1, mstype.float32)
        >>> var = Tensor(np.ones((4, 1)), mstype.float32)
        >>> target = Tensor(arr2, mstype.float32)
        >>> output = ops.gaussian_nll_loss(x, target, var)
        >>> print(output)
        1.4374993

    Reference:
        Nix, D. A. and Weigend, A. S., "Estimating the mean and variance of the
        target probability distribution", Proceedings of 1994 IEEE International
        Conference on Neural Networks (ICNN'94), Orlando, FL, USA, 1994, pp. 55-60
        vol.1, doi: 10.1109/ICNN.1994.374138.
    """
    if not isinstance(x, Tensor):
        raise TypeError(f"For 'gaussian_nll_loss', 'x' must be a tensor, but got {type(x)}.")
    if not isinstance(target, Tensor):
        raise TypeError(f"For 'gaussian_nll_loss', 'target' must be a tensor, but got {type(target)}.")
    if not isinstance(var, Tensor):
        raise TypeError(f"For 'gaussian_nll_loss', 'var' must be a tensor, but got {type(var)}.")
    if not isinstance(full, bool):
        raise TypeError(f"For 'gaussian_nll_loss', 'full' must be a bool, but got {type(full)}.")
    if not isinstance(eps, float) or eps <= 0:
        raise ValueError(f"For 'gaussian_nll_loss', 'eps' must be a positive float, but got {eps}.")
    if reduction not in ('none', 'mean', 'sum'):
        raise ValueError(f"For 'gaussian_nll_loss', 'reduction' must be one of 'none', 'mean', or 'sum',\
        but got {reduction}.")
    if not x.shape == var.shape:
        if x.shape[:-1] == var.shape:
            var = var.unsqueeze(dim=-1)

    maxima = maximum_(var, eps)
    logarithm = log_(maxima)
    squared_loss = square_(x - target)
    c = 0 if not full else 0.5 * log(2 * pi)
    loss = 0.5 * (logarithm + squared_loss / maxima) + c
    if reduction == 'mean':
        loss = loss.mean()
    elif reduction == 'sum':
        loss = loss.sum()
    return loss


@_primexpr
def _check_hinge_embedding_loss_type(inputs_dtype, targets_dtype, inputs, targets, margin, reduction):
    """Check hinge embedding loss type."""
    if not isinstance(margin, (float, int)):
        raise TypeError(f"For 'HingeEmbeddingLoss', 'margin' must be a float or int, but got {type(margin)}.")
    if reduction not in ['none', 'mean', 'sum']:
        raise ValueError(f"For 'HingeEmbeddingLoss', 'reduction' must be one of 'none', 'mean', 'sum',"
                         f"but got {reduction}.")
    if not isinstance(inputs, Tensor):
        raise TypeError(f"For 'HingeEmbeddingLoss', the first input must be a Tensor, but got {type(inputs)}.")
    if not isinstance(targets, Tensor):
        raise TypeError(f"For 'HingeEmbeddingLoss', the second input must be a Tensor, but got {type(targets)}.")

    if inputs_dtype not in mstype.float_type:
        raise TypeError(f"For 'HingeEmbeddingLoss', the dtype of the first input must be float, but got "
                        f"{inputs_dtype}.")
    if targets_dtype not in mstype.float_type:
        raise TypeError(f"For 'HingeEmbeddingLoss', the dtype of the second input must be float, but got "
                        f"{targets_dtype}.")


def hinge_embedding_loss(inputs, targets, margin=1.0, reduction='mean'):
    r"""
    Measures Hinge Embedding Loss given an input Tensor `intputs` and a labels Tensor `targets` (containing 1 or -1).

    The loss function for :math:`n`-th sample in the mini-batch is

    .. math::
        l_n = \begin{cases}
        x_n, & \text{if}\; y_n = 1,\\
        \max \{0, \Delta - x_n\}, & \text{if}\; y_n = -1,
        \end{cases}

    and the total loss functions is

    .. math::
        \ell(x, y) = \begin{cases}
        \operatorname{mean}(L), & \text{if reduction} = \text{'mean';}\\
        \operatorname{sum}(L),  & \text{if reduction} = \text{'sum'.}
        \end{cases}

    where :math:`L = \{l_1,\dots,l_N\}^\top`.

    Args:
        inputs (Tensor): Predicted values, represented as :math:`x` in the formula.
        targets (Tensor): Label values, represented as :math:`y` in the formula.
            Has the same shape as `inputs`, contains -1 or 1.
        margin (float, int): Threshold defined by Hinge Embedding Loss `margin`.
            Represented as :math:`\Delta` in the formula. Default: ``1.0`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Tensor scalar, the computed loss depending on `reduction`.

    Raises:
        TypeError: If `inputs` is not a Tensor.
        TypeError: If `targets` is not a Tensor.
        TypeError: If `margin` is not a float or int.
        ValueError: If `targets` does not have the same shape as `inputs` or they could not broadcast to each other.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import numpy as np
        >>> import mindspore.common.dtype as mstype
        >>> from mindspore import ops
        >>> from mindspore import Tensor
        >>> arr1 = np.array([0.9, -1.2, 2, 0.8, 3.9, 2, 1, 0, -1]).reshape((3, 3))
        >>> arr2 = np.array([1, 1, -1, 1, -1, 1, -1, 1, 1]).reshape((3, 3))
        >>> logits = Tensor(arr1, mstype.float32)
        >>> labels = Tensor(arr2, mstype.float32)
        >>> loss = ops.hinge_embedding_loss(logits, labels, margin=1.0, reduction='mean')
        >>> print(loss)
        0.16666666
    """
    inputs_dtype = inputs.dtype
    targets_dtype = targets.dtype
    _check_hinge_embedding_loss_type(inputs_dtype, targets_dtype, inputs, targets, margin, reduction)

    min_val = Tensor(0, inputs_dtype)
    pos_index = targets > 0
    neg_index = targets < 0
    pos = pos_index * inputs
    neg = neg_index * inputs
    m = ops.cast(margin, inputs_dtype)
    margin_matrix = m * neg_index
    neg = margin_matrix - neg
    neg = ops.clip_by_value(neg, min_val)
    loss = pos + neg
    if reduction == 'mean':
        loss = loss.mean()
    elif reduction == 'sum':
        loss = loss.sum()
    return loss


def ctc_greedy_decoder(inputs, sequence_length, merge_repeated=True):
    r"""
    Performs greedy decoding on the logits given in inputs.

    Note:
        On Ascend, 'merge_repeated' can not be set to false.

    Args:
        inputs (Tensor): The input Tensor must be a 3-D tensor whose shape is
            :math:`(max\_time, batch\_size, num\_classes)`. `num_classes` must be `num_labels + 1` classes,
            `num_labels` indicates the number of actual labels. Blank labels are reserved.
            Default blank label is `num_classes - 1`. Data type must be float32 or float64.
        sequence_length (Tensor): A tensor containing sequence lengths with the shape of :math:`(batch\_size, )`.
            The type must be int32. Each value in the tensor must be equal to or less than `max_time`.
        merge_repeated (bool): If ``true`` , merge repeated classes in output. Default: ``True`` .

    Returns:
        decoded_indices (Tensor), A tensor with shape of :math:`(total\_decoded\_outputs, 2)`.
        Data type is int64.

        decoded_values (Tensor), A tensor with shape of :math:`(total\_decoded\_outputs, )`,
        it stores the decoded classes. Data type is int64.

        decoded_shape (Tensor), A tensor with shape of :math:`(batch\_size, max\_decoded\_length)`.
        Data type is int64.

        log_probability (Tensor), A tensor with shape of :math:`(batch\_size, 1)`,
        containing sequence log-probability, has the same type as `inputs`.

    Raises:
        TypeError: If `merge_repeated` is not a bool.
        ValueError: If length of shape of `inputs` is not equal to 3.
        ValueError: If length of shape of `sequence_length` is not equal to 1.
        ValueError: If value in the `sequence_length` is larger than `max_time`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> inputs = Tensor(np.array([[[0.6, 0.4, 0.2], [0.8, 0.6, 0.3]],
        ...                           [[0.0, 0.6, 0.0], [0.5, 0.4, 0.5]]]), mindspore.float32)
        >>> sequence_length = Tensor(np.array([2, 2]), mindspore.int32)
        >>> decoded_indices, decoded_values, decoded_shape, log_probability = ops.ctc_greedy_decoder(inputs,
        ...                                                                                          sequence_length)
        >>> print(decoded_indices)
        [[0 0]
         [0 1]
         [1 0]]
        >>> print(decoded_values)
        [0 1 0]
        >>> print(decoded_shape)
        [2 2]
        >>> print(log_probability)
        [[-1.2]
         [-1.3]]
    """
    _ctc_greedy_decoder = _get_cache_prim(NN_OPS.CTCGreedyDecoder)(merge_repeated)
    return _ctc_greedy_decoder(inputs, sequence_length)


def conv3d_transpose(inputs, weight, pad_mode='valid', padding=0, stride=1, dilation=1, group=1,
                     output_padding=0):
    r"""
    Computes a 3D transposed convolution, which is also known as a deconvolution
    (although it is not an actual deconvolution).

    Args:
        inputs (Tensor): The gradients with respect to the output of the convolution.
           The shape conforms to the default.
           data_format :math:`(N, C_{in}, D_{out}, H_{out}, W_{out})`.
           Supported dtypes:

           - Ascend: float16.
           - GPU/CPU: float16, float32.
        weight (Tensor): Set size of kernel is :math:`(K_d, K_h, K_w)`, then the shape is
           :math:`(C_{in}, C_{out}//group, K_d, K_h, K_w)`. Where :math:`group` is the Args parameter,
           :math:`//` is the symbol for integer division.
           It has the same dtype as `dout`.
        pad_mode (str): Specifies padding mode. The optional values are
            "same", "valid", "pad". Default: "valid".

            - same: Adopts the way of completion. The depth, height and width of the output will be equal to
              the input `x` divided by stride. The padding will be evenly calculated in head and tail, top and bottom,
              left and right directions possibility.
              Otherwise, the last extra padding will be calculated from the tail, bottom and the right side.
              If this mode is set, `pad` must be 0.

            - valid: Adopts the way of discarding. The possible largest depth, height and width of output
              will be returned without padding. Extra pixels will be discarded. If this mode is set, `pad`
              and `output_padding` must be 0.

            - pad: Implicit paddings on both sides of the input in depth, height and width. The number of `pad` will
              be padded to the input Tensor borders. `pad` must be greater than or equal to 0.

        padding (Union(int, tuple[int])): The padding value to be filled. Default: 0. If `padding` is an integer, the
            paddings of head, tail, top, bottom, left and right are the same, equal to pad. If `padding` is a tuple of
            six integers, the padding of head, tail, top, bottom, left and right equal to padding[0], padding[1],
            padding[2], padding[3], padding[4] and padding[5] correspondingly.
        stride (Union(int, tuple[int])): The distance of kernel moving, an int number that represents
            the depth, height and width of movement are both strides, or a tuple of three int numbers that
            represent depth, height and width of movement respectively. Default: 1.
        dilation (Union(int, tuple[int])): Specifies the space to use between kernel elements. Default: 1.
        group (int): Splits input into groups. Default: 1. Only 1 is currently supported.
        output_padding (Union(int, tuple[int])): Add extra size to each dimension of the output. Default: 0.


    Outputs:
        Tensor, the gradients with respect to the input of convolution 3D.
        Tensor of shape :math:`(N, C_{out}//group, D_{out}, H_{out}, W_{out})`,
        where :math:`group` is the Args parameter.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Raises:
        TypeError: If `group` is not an int.
        TypeError: If `stride`, `padding` , `dilation` or `output_padding` is neither an int not a tuple.
        ValueError: If the rank of `inputs`, `weight` is not equal to 5.
        ValueError: If `stride` or `dilation` is less than 1.
        ValueError: if inputs[1], weight[1] and weight[2:5] i.e. `in_channel`, `out_channel` and `kernel_size` is less
                    than 1.
        ValueError: If `padding` is less than 0.
        ValueError: If `pad_mode` is not one of 'same', 'valid' nor 'pad'.
        ValueError: If `padding` is a tuple whose length is not equal to 6.
        ValueError: If `pad_mode` is not equal to 'padding' and `padding` is not equal to (0, 0, 0, 0, 0, 0).
        ValueError: If `data_format` is not 'NCDHW'.
        TypeError: If data type of dout and weight is not float16.

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> dout = Tensor(np.ones([32, 16, 10, 32, 32]), mindspore.float16)
        >>> weight = Tensor(np.ones([16, 3, 4, 6, 2]), mindspore.float16)
        >>> output = conv3d_transpose(dout, weight)
        >>> print(output.shape)
        (32, 3, 13, 37, 33)
    """
    if len(inputs.shape) != 5:
        raise_value_error("the rank of inputs tensor should be 5.")
    if len(weight.shape) != 5:
        raise_value_error("the rank of weight tensor should be 5.")
    in_channel = inputs.shape[1]
    out_channel = weight.shape[1]
    kernel_size = weight.shape[2:5]
    _conv_3d_transpose = _get_cache_prim(NN_OPS.Conv3DTranspose)(in_channel, out_channel, kernel_size, 1, pad_mode,
                                                                 padding, stride, dilation, group, output_padding)
    return _conv_3d_transpose(inputs, weight)


def _manipulate_padding(padding, dim):
    """convert padding to Conv2D padding"""
    ms_padding = ()
    if not isinstance(padding, (tuple, list)):
        raise TypeError(f"For 'conv{dim}d', 'padding' must be a tuple, list or int, but got {type(padding)}.")
    if len(padding) != dim:
        raise ValueError(f"For 'conv{dim}d', 'padding' must be a tuple or list of {dim} integers, but got {padding}.")
    for i in range(dim):
        ms_padding += (padding[i], padding[i])
    return ms_padding


def _dim_manipulation(x, name):
    """convert 1d dilation, stride, etc. to 2d"""
    if isinstance(x, int):
        if x <= 0:
            raise ValueError(f"For 'conv1d', {name} must be a positive int, but got {x}.")
        return 1, x
    if isinstance(x, (tuple, list)):
        if len(x) != 1:
            raise ValueError(f"For 'conv1d', {name} must be a tuple/list with 1 element or int, but got {x}.")
        if x[0] <= 0:
            raise ValueError(f"For 'conv1d', elements in {name} must be positive int, but got {x}.")
        return 1, x[0]
    raise ValueError(f"For 'conv1d', {name} must be an int or a tuple/list with 1 element, but got {x}.")


def _check_conv_iterable_lengths(iterable, dim, iter_name):
    """check iterables lengths used in conv functions"""
    if len(iterable) != dim:
        raise ValueError(f"For 'conv{dim}d', the {iter_name} must be a int or a tuple/list with length {dim}, "
                         f"but got {iterable}.")


def conv1d(input, weight, bias=None, stride=1, pad_mode="valid", padding=0, dilation=1, groups=1):
    r"""
    Applies a 1D convolution over an input tensor. The input Tensor is typically
    of shape :math:`(N, C_{in}, L_{in})`,
    where :math:`N` is batch size, :math:`C` is channel number, :math:`L` is input sequence width.

    The output is calculated based on formula:

    .. math::

        \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
        \sum_{k = 0}^{C_{in} - 1} \text{ccor}({\text{weight}(C_{\text{out}_j}, k), \text{X}(N_i, k)})

    where :math:`bias` is the output channel bias, :math:`ccor` is
    the `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`_,
    , :math:`weight` is the convolution kernel value and :math:`X` represents the input feature map.

    Here are the indices' meanings:

    - :math:`i` corresponds to the batch number, the range is :math:`[0, N-1]`,
      where :math:`N` is the batch size of the input.

    - :math:`j` corresponds to the output channel, ranging from :math:`[0, C_{out}-1]`,
      where :math:`C_{out}` is the number of
      output channels, which is also equal to the number of kernels.

    - :math:`k` corresponds to the input channel, ranging from :math:`[0, C_{in}-1]`,
      where :math:`C_{in}` is the number of
      input channels, which is also equal to the number of channels in the convolutional kernels.

    Therefore, in the above formula, :math:`{bias}(C_{\text{out}_j})` represents the bias of the :math:`j`-th
    output channel, :math:`{weight}(C_{\text{out}_j}, k)` represents the slice of the :math:`j`-th convolutional
    kernel in the :math:`k`-th channel, and :math:`{X}(N_i, k)` represents the slice of the :math:`k`-th input
    channel in the :math:`i`-th batch of the input feature map.

    The shape of the convolutional kernel is given by :math:`(\text{kernel_size})`,
    where :math:`\text{kernel_size}` is the width of the kernel.
    If we consider the input and output channels as well as the `groups` parameter, the complete kernel shape
    will be :math:`(C_{out}, C_{in} / \text{groups}, \text{kernel_size})`,
    where `groups` is the number of groups dividing `x`'s input channel when applying group convolution.

    For more details about convolution layer, please refer to `Gradient Based Learning Applied to Document Recognition
    <http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf>`_
    and `ConvNets <http://cs231n.github.io/convolutional-networks/>`_ .

    Note:
        On Ascend platform, only group convolution in depthwise convolution scenarios is supported.
        That is, when `groups>1`, condition :math:`C_{in}` = :math:`C_{out}` = `groups` must be satisfied.

    Args:
        input (Tensor): Input Tensor of shape :math:`(N, C_{in}, L_{in})`.
        weight (Tensor): The convolutional kernel value, it should has shape
            :math:`(N, C_{in} / \text{groups}, \text{kernel_size})`.
        bias (Tensor, optional): Bias Tensor with shape :math:`(C_{out})`.
            When bias is None, zeros will be used. Default: ``None`` .
        stride (Union(int, tuple[int]), optional): The distance of kernel moving, an int number or a tuple of one int
            that represents width of movement. Default: ``1``.
        pad_mode (str, optional): Specifies padding mode. The optional values are
            ``"same"`` , ``"valid"`` and ``"pad"`` . Default: ``"valid"`` .

            - ``"same"``: Adopts the way of completion. The height and width of the output will be equal to
              the input `x` divided by stride. The padding will be evenly calculated in left and right possiblily.
              Otherwise, the last extra padding will be calculated from the right side.
              If this mode is set, `padding` must be 0.

            - ``"valid"``: Adopts the way of discarding. The possible largest width of output will be returned
              without padding. Extra pixels will be discarded. If this mode is set, `padding` must be 0.

            - ``"pad"``: Implicit paddings on both sides of the input `x`.
              The number of `padding` will be padded to the input
              Tensor borders. `padding` must be greater than or equal to 0.
        padding (Union(int, tuple[int], list[int]), optional):  Specifies the amount of padding to apply on
            both side of `input` when `pad_mode` is set to ``"pad"``. The
            paddings of left and right are the same, equal to padding or padding[0] when padding is a tuple of
            1 integer. Default: ``0`` .
        dilation (Union(int, tuple[int]), optional): Specifies the dilation rate to use for dilated convolution.
            It can be a single int or a tuple of 1 integer.
            Assuming :math:`dilation=(d0,)`, the convolutional kernel samples the input with a
            spacing of :math:`d0-1` elements in the width direction.
            The value should be in the ranges [1, L].
            Default: ``1`` .
        groups (int, optional): Splits `input` into groups. Default: ``1`` .

    Returns:
        Tensor, the value that applied 1D convolution. The shape is :math:`(N, C_{out}, L_{out})`.
        To see how different pad modes affect the output shape, please refer to
        :class:`mindspore.nn.Conv1d` for more details.

    Raises:
        TypeError: If `stride`, `padding` or `dilation` is neither an int nor a tuple.
        TypeError: `groups` is not an int.
        TypeError: If `bias` is not a Tensor.
        ValueError: If the shape of `bias` is not :math:`(C_{out})` .
        ValueError: If `stride` or `dilation` is less than 1.
        ValueError: If `pad_mode` is not one of 'same', 'valid' or 'pad'.
        ValueError: If `padding` is a tuple whose length is not equal to 1.
        ValueError: If `pad_mode` is not equal to 'pad' and `padding` is greater than 0.

    Supported Platforms:
        ``Ascend`` ``GPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.arange(64).reshape((4, 4, 4)), mindspore.float32)
        >>> weight = Tensor(np.arange(8).reshape((2, 2, 2)), mindspore.float32)
        >>> bias = Tensor([-0.12345, 2.7683], mindspore.float32)
        >>> output = ops.conv1d(x, weight, pad_mode='pad', padding=(1,), bias=bias, groups=2)
        >>> print(output.shape)
        (4, 2, 5)
    """
    if input.ndim != 3:
        raise ValueError(f"For 'conv1d', the input must be a 3D Tensor, but got input of {input.ndim}D.")
    if weight.ndim != 3:
        raise ValueError(f"For 'conv1d', the weight must be a 3D Tensor, but got input of {weight.ndim}D.")
    expanded_input = expand_dims_(input, 2)
    sqz = _get_cache_prim(P.Squeeze)(2)
    weight_shape = weight.shape
    out_channel = weight_shape[0]
    kernel_size = (1, weight_shape[2])
    expanded_weight = expand_dims_(weight, 2)
    if isinstance(padding, int):
        padding = (0, 0, padding, padding)
    elif isinstance(padding, (tuple, list)):
        if len(padding) != 1:
            raise ValueError(f"For 'conv1d', padding must be a tuple or list with 1 element or int, but got {padding}.")
        padding = (0, 0, padding[0], padding[0])
    else:
        raise TypeError(f"For 'conv1d', padding must be a tuple, list or int, but got {type(padding)}.")
    input_shape = input.shape
    in_channel = input_shape[1]
    if not (in_channel % groups == 0 and out_channel % groups == 0):
        raise ValueError(f"The argument 'groups' should be divisible by 'in_channel' " \
                         f"and 'out_channel', but got group:{groups}, in_channel:{in_channel}, " \
                         f"out_channel:{out_channel}.")
    dilation = _dim_manipulation(dilation, name='dilation')
    stride = _dim_manipulation(stride, name='stride')
    conv = _get_cache_prim(P.Conv2D)(out_channel, kernel_size, 1, pad_mode, padding, stride, dilation, groups, "NCHW")
    conv_res = conv(expanded_input, expanded_weight)
    squeezed_conv_res = sqz(conv_res)
    if bias is None:
        return squeezed_conv_res
    if not isinstance(bias, Tensor):
        raise TypeError(f"For 'conv1d', the 'bias' must be a Tensor, but got {type(bias)}.")
    if bias.shape[0] != out_channel:
        raise ValueError(f"For 'conv1d', given weight of size {weight_shape}, expected bias to be 1-dimensional with " \
                         f"{out_channel} elements, but got bias of size {bias.shape[0]} instead.")
    output = bias_add(squeezed_conv_res, bias)
    return output


def conv2d(input, weight, bias=None, stride=1, pad_mode="valid", padding=0, dilation=1, groups=1):
    r"""
    Applies a 2D convolution over an input tensor. The input tensor is typically of
    shape :math:`(N, C_{in}, H_{in}, W_{in})`, where :math:`N` is batch size, :math:`C` is
    channel number, :math:`H` is feature height, :math:`W` is feature width.

    The output is calculated based on formula:

    .. math::

        \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
        \sum_{k = 0}^{C_{in} - 1} \text{ccor}({\text{weight}(C_{\text{out}_j}, k), \text{X}(N_i, k)})

    where :math:`bias` is the output channel bias, :math:`ccor` is
    the `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`_,
    , :math:`weight` is the convolution kernel value and :math:`X` represents the input feature map.

    Here are the indices' meanings:

    - :math:`i` corresponds to the batch number, the range is :math:`[0, N-1]`,
      where :math:`N` is the batch size of the input.

    - :math:`j` corresponds to the output channel, the range is :math:`[0, C_{out}-1]`,
      where :math:`C_{out}` is the number of output channels, which is also equal to the number of kernels.

    - :math:`k` corresponds to the input channel, the range is :math:`[0, C_{in}-1]`,
      where :math:`C_{in}` is the number of
      input channels, which is also equal to the number of channels in the convolutional kernels.

    Therefore, in the above formula, :math:`{bias}(C_{out_j})` represents the bias of the :math:`j`-th
    output channel, :math:`{weight}(C_{out_j}, k)` represents the slice of the :math:`j`-th convolutional
    kernel in the :math:`k`-th channel, and :math:`{X}(N_i, k)` represents the slice of the :math:`k`-th input
    channel in the :math:`i`-th batch of the input feature map.

    The shape of the convolutional kernel is given by :math:`(\text{kernel_size[0]}, \text{kernel_size[1]})`,
    where :math:`\text{kernel_size[0]}` and :math:`\text{kernel_size[1]}` are the height and width of the kernel,
    respectively.
    If we consider the input and output channels as well as the `groups` parameter, the complete kernel shape
    will be :math:`(C_{out}, C_{in} / \text{groups}, \text{kernel_size[0]}, \text{kernel_size[1]})`,
    where `groups` is the number of groups dividing `x`'s input channel when applying group convolution.

    For more details about convolution layer, please refer to `Gradient Based Learning Applied to Document Recognition
    <http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf>`_ and
    `ConvNets <http://cs231n.github.io/convolutional-networks/>`_.

    Note:
        On Ascend platform, only group convolution in depthwise convolution scenarios is supported.
        That is, when `groups>1`, condition :math:`C_{in}` = :math:`C_{out}` = `groups` must be satisfied.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C_{in}, H_{in}, W_{in})`.
        weight (Tensor): Tensor of shape
            :math:`(N, C_{in} / \text{groups}, \text{kernel_size[0]}, \text{kernel_size[1]})`, then the size of kernel
            is :math:`(\text{kernel_size[0]}, \text{kernel_size[1]})`.
        bias (Tensor, optional): Bias Tensor with shape :math:`(C_{out})`.
            When bias is ``None`` , zeros will be used. Default: ``None`` .
        stride (Union(int, tuple[int]), optional): The distance of kernel moving, an int number that represents
            the height and width of movement are both strides, or a tuple of two int numbers that
            represent height and width of movement respectively. Default: ``1`` .
        pad_mode (str, optional): Specifies padding mode. The optional values are
            ``"same"`` , ``"valid"`` and ``"pad"`` . Default: ``"valid"`` .

            - same: Adopts the way of completion. The height and width of the output will be equal to
              the input `x` divided by stride. The padding will be evenly calculated in top and bottom,
              left and right possiblily. Otherwise, the last extra padding will be calculated from the bottom
              and the right side. If this mode is set, `padding` must be 0.

            - valid: Adopts the way of discarding. The possible largest height and width of output will be returned
              without padding. Extra pixels will be discarded. If this mode is set, `padding` must be 0.

            - pad: Implicit paddings on both sides of the input `x`. The number of `padding` will be padded to the input
              Tensor borders. `padding` must be greater than or equal to 0.
        padding (Union(int, tuple[int], list[int]), optional): Implicit paddings on both sides of the input `x`.
            If `padding` is one integer, the paddings of top, bottom, left and right are the same, equal to padding.
            If `padding` is a tuple/list with 2 integers, the padding of top adn bottom is padding[0],
            and the padding of left and right is padding[1]. Default: ``0`` .
        dilation (Union(int, tuple[int]), optional): Gaps between kernel elements.The data type is int or a tuple of
            2 integers. Specifies the dilation rate to use for dilated convolution. If set to be :math:`k > 1`,
            there will be :math:`k - 1` pixels skipped for each sampling location. Its value must
            be greater than or equal to 1 and bounded by the height and width of the input `x`. Default: ``1`` .
        groups (int, optional): Splits `input` into groups. Default: ``1`` .

    Returns:
        Tensor, the value that applied 2D convolution. The shape is :math:`(N, C_{out}, H_{out}, W_{out})`.
        To see how different pad modes affect the output shape, please refer to
        :class:`mindspore.nn.Conv2d` for more details.


    Raises:
        TypeError: If `stride`, `padding` or `dilation` is neither an int nor a tuple.
        TypeError: `groups` is not an int.
        TypeError: If `bias` is not a Tensor.
        ValueError: If  the shape of `bias` is not :math:`(C_{out})` .
        ValueError: If `stride` or `dilation` is less than 1.
        ValueError: If `pad_mode` is not one of 'same', 'valid' or 'pad'.
        ValueError: If `padding` is a tuple/list whose length is not equal to 2.
        ValueError: If `pad_mode` is not equal to 'pad' and `padding` is greater than 0.

    Supported Platforms:
        ``Ascend`` ``GPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.ones([10, 32, 32, 32]), mindspore.float32)
        >>> weight = Tensor(np.ones([32, 32, 3, 3]), mindspore.float32)
        >>> output = ops.conv2d(x, weight)
        >>> print(output.shape)
        (10, 32, 30, 30)
    """
    if isinstance(stride, (tuple, list)):
        _check_conv_iterable_lengths(stride, dim=2, iter_name='stride')
    if isinstance(dilation, (tuple, list)):
        _check_conv_iterable_lengths(dilation, dim=2, iter_name='dilation')
    if isinstance(padding, (tuple, list)):
        padding = _manipulate_padding(padding, dim=2)
    weight_shape = weight.shape
    out_channel = weight_shape[0]
    kernel_size = weight_shape[2:4]
    input_shape = input.shape
    in_channel = input_shape[1]
    if not (in_channel % groups == 0 and out_channel % groups == 0):
        raise ValueError(f"The argument 'groups' should be divisible by 'in_channel' " \
                         f"and 'out_channel', but got group:{groups}, in_channel:{in_channel}, " \
                         f"out_channel:{out_channel}.")
    conv = _get_cache_prim(P.Conv2D)(out_channel, kernel_size, 1, pad_mode, padding, stride, dilation, groups, "NCHW")
    if bias is None:
        return conv(input, weight)
    if not isinstance(bias, Tensor):
        raise TypeError(f"For 'conv2d', the 'bias' must be a Tensor, but got {type(bias)}.")
    if bias.shape[0] != out_channel:
        raise ValueError(f"For 'conv2d', Given weight of size {weight_shape}, expected bias to be 1-dimensional with " \
                         f"{out_channel} elements, but got bias of size {bias.shape[0]} instead.")
    conv_result = conv(input, weight)
    output = bias_add(conv_result, bias)
    return output


def conv1d_ext(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1):
    r"""
    Applies a 1D convolution over an input tensor. The input tenor is typically
    of shape :math:`(N, C_{in}, L_{in})`,
    where :math:`N` is batch size, :math:`C` is channel number, :math:`L` is sequence length.

    The output is calculated based on formula:

    .. math::

        \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
        \sum_{k = 0}^{C_{in} - 1} \text{ccor}({\text{weight}(C_{\text{out}_j}, k), \text{X}(N_i, k)})

    where :math:`bias` is the output channel bias, :math:`ccor` is
    the `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`_,
    :math:`weight` is the convolution kernel value and :math:`X` represents the input feature map.

    - :math:`i` corresponds to the batch number, the range is :math:`[0, N-1]`,
      where :math:`N` is the batch size of the input.

    - :math:`j` corresponds to the output channel, the range is :math:`[0, C_{out}-1]`,
      where :math:`C_{out}` is the number of
      output channels, which is also equal to the number of kernels.

    - :math:`k` corresponds to the input channel, the range is :math:`[0, C_{in}-1]`,
      where :math:`C_{in}` is the number of
      input channels, which is also equal to the number of channels in the convolutional kernels.

    Therefore, in the above formula, :math:`{bias}(C_{\text{out}_j})` represents the bias of the :math:`j`-th
    output channel, :math:`{weight}(C_{\text{out}_j}, k)` represents the slice of the :math:`j`-th convolutional
    kernel in the :math:`k`-th channel, and :math:`{X}(N_i, k)` represents the slice of the :math:`k`-th input
    channel in the :math:`i`-th batch of the input feature map.

    The shape of the convolutional kernel is given by :math:`(\text{kernel_size})`,
    where :math:`\text{kernel_size}` is the length of the kernel.
    If we consider the input and output channels as well as the `groups` parameter, the complete kernel shape
    will be :math:`(C_{out}, C_{in} / \text{groups}, \text{kernel_size})`,
    where `groups` is the number of groups dividing `x`'s input channel when applying groups convolution.

    For more details about convolution layer, please refer to `Gradient Based Learning Applied to Document Recognition
    <http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf>`_.

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C_{in}, L_{in})` or :math:`(C_{in}, L_{in})`.
        weight (Tensor): Tensor of shape
            :math:`(N, C_{in} / \text{groups}, \text{kernel_size})`, then the size of kernel
            is :math:`(\text{kernel_size})`.
        bias (Tensor, optional): Bias Tensor with shape :math:`(C_{out})`.
            When bias is ``None`` , zeros will be used. Default: ``None`` .
        stride (Union[int, tuple[int], list[int]], optional): The movement stride of the 1D convolution kernel.
            The data type is an integer or a tuple of one integer. Default: ``1`` .` .
        padding (Union[int, tuple[int], list[int], str], optional): The number of padding
            on the input.
            The data type is an integer or a tuple of one integer or string {`valid`, `same`}.
            The value should be greater than or equal to 0. Default: ``0`` .

            - ``"same"``: Pad the input around its edges so that the shape of input and output
              are the same when `stride` is set to ``1``.
              The amount of padding to is calculated by the operator internally, If the amount is even, it is
              uniformly distributed around the input, if it is odd, the excess amount goes to the right side.
              If this mode is set, `stride` must be 1.

            - ``"valid"``: No padding is applied to the input, and the output returns the maximum
              possible length. Extra sequence that could not complete a full stride will
              be discarded.

        dilation (Union[int, tuple[int], list[int]], optional): Specifies the dilation rate to use for
            dilated convolution. It can be a single int or a tuple of 1 integer.
            Assuming :math:`dilation=(d)`, the convolutional kernel samples the input with a
            spacing of :math:`d-1` elements in the length direction.
            Default: ``1`` .
        groups (int, optional): Splits filter into groups, `in_channels` and `out_channels` must be
            divisible by `groups`. If the groups is equal to `in_channels` and `out_channels`,
            this 1D convolution layer also can be called 1D depthwise convolution layer. Default: ``1`` .

            - :math:`(C_{in} \text{ % } \text{groups} == 0)` , :math:`(C_{out} \text{ % } \text{groups} == 0)` ,
              :math:`(C_{out} >= \text{groups})` , :math:`(\text{weight[1]} = C_{in} / \text{groups})`。

    Returns:
        Tensor, the value that applied 1D convolution. The shape is :math:`(N, C_{out}, L_{out})`.
        To see how different pad modes affect the output shape, please refer to
        :class:`mindspore.mint.nn.Conv1d` for more details.

    Raises:
        ValueError: Args and size of the input feature map should satisfy the output formula to ensure that the size of
            the output feature map is positive; otherwise, an error will be reported.
        RuntimeError: On Ascend, due to the limitation of the L1 cache size of different NPU chip, if input size or
            kernel size is too large, it may trigger an error.
        TypeError: If `in_channels`, `out_channels` or `groups` is not an int.
        TypeError: If `kernel_size`, `stride` or `dilation` is neither an int not a tuple.
        ValueError: If `in_channels`, `out_channels`, `kernel_size`, `stride` or `dilation` is less than 1.
        ValueError: If `padding` is less than 0.
        ValueError: If `padding` is `same` , `stride` is not equal to 1.
        ValueError: The input parameters do not satisfy the convolution output formula.
        ValueError: The KernelSize cannot exceed the size of the input feature map.
        ValueError: The value of padding cannot cause the calculation area to exceed the input size.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops, mint
        >>> x = Tensor(np.ones([10, 32, 32]), mindspore.float32)
        >>> weight = Tensor(np.ones([32, 32, 3]), mindspore.float32)
        >>> output = mint.nn.functional.conv1d(x, weight)
        >>> print(output.shape)
        (10, 32, 30)
    """
    if isinstance(padding, (int, tuple, list)):
        return conv1d_ext_op(input, weight, bias, stride, padding, dilation, groups)
    if isinstance(padding, str):
        return conv1d_padding_op(input, weight, bias, stride, padding, dilation, groups)
    raise TypeError(f"For conv1d, the parameter 'padding' must be a tuple/list " \
                    f"or a string, but got {type(padding)}")


def _check_stride_when_same_mode(stride):
    """ stride must be 1 when pad mode is same """
    if isinstance(stride, int):
        if stride != 1:
            raise ValueError(f"For conv2d, 'padding=same' is not supported for stride convolution, " \
                             f"but got {stride}")
    elif isinstance(stride, tuple):
        validator.check_int(len(stride), 2, validator.EQ, "stride", 'conv2d')
        if not all(s == 1 for s in stride):
            raise ValueError(f"For conv2d, 'padding=same' is not supported for stride convolution, " \
                             f"but got {stride}")
    else:
        raise TypeError(f"For conv2d, the parameter 'stride' must be a int/tuple, but got {type(stride)}")


def _get_pad_info(dilation, weight):
    """ Get pad list by dilation and weight shape """
    need_pad_nd = False
    pad_l = ()
    pad_r = ()
    for i in range(2):
        d = dilation[i]
        weight_size = weight.shape[i + 2]
        pad_item = d * (weight_size - 1)
        pad_l += (int(pad_item / 2),)
        pad_r += (int(pad_item - pad_l[i]),)
        if pad_l[i] != pad_r[i]:
            need_pad_nd = True
    return need_pad_nd, pad_l, pad_r


def _get_pad_nd_info(pad_l, pad_r):
    """ Get pad_nd list if input need to exec pad_nd """
    pad_nd = ()
    new_pad_l = ()
    for i in range(2):
        delta_pad = pad_r[i] - pad_l[i]
        if delta_pad > 0:
            pad_nd = (0, delta_pad,) + pad_nd
            new_pad_l += (pad_l[i],)
        else:
            pad_nd = (delta_pad, 0,) + pad_nd
            new_pad_l += (pad_r[i],)
    return pad_nd, new_pad_l


def conv2d_ext(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1):
    r"""
    Applies a 2D convolution over an input tensor. The input tensor is typically of
    shape :math:`(N, C_{in}, H_{in}, W_{in})` or :math:`(C_{in}, H_{in}, W_{in})`,
    where :math:`N` is batch size, :math:`C` is channel number, :math:`H` is feature height, :math:`W` is feature width.

    The output is calculated based on formula:

    .. math::

        \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
        \sum_{k = 0}^{C_{in} - 1} \text{ccor}({\text{weight}(C_{\text{out}_j}, k), \text{X}(N_i, k)})

    where :math:`bias` is the output channel bias, :math:`ccor` is
    the `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`_,
    , :math:`weight` is the convolution kernel value and :math:`X` represents the input feature map.

    - :math:`i` corresponds to the batch number, the range is :math:`[0, N-1]`,
      where :math:`N` is the batch size of the input.

    - :math:`j` corresponds to the output channel, the range is :math:`[0, C_{out}-1]`,
      where :math:`C_{out}` is the number of output channels, which is also equal to the number of kernels.

    - :math:`k` corresponds to the input channel, the range is :math:`[0, C_{in}-1]`,
      where :math:`C_{in}` is the number of
      input channels, which is also equal to the number of channels in the convolutional kernels.

    Therefore, in the above formula, :math:`{bias}(C_{out_j})` represents the bias of the :math:`j`-th
    output channel, :math:`{weight}(C_{out_j}, k)` represents the slice of the :math:`j`-th convolutional
    kernel in the :math:`k`-th channel, and :math:`{X}(N_i, k)` represents the slice of the :math:`k`-th input
    channel in the :math:`i`-th batch of the input feature map.

    The shape of the convolutional kernel is given by :math:`(\text{kernel_size[0]}, \text{kernel_size[1]})`,
    where :math:`\text{kernel_size[0]}` and :math:`\text{kernel_size[1]}` are the height and width of the kernel,
    respectively.
    If we consider the input and output channels as well as the `group` parameter, the complete kernel shape
    will be :math:`(C_{out}, C_{in} / \text{group}, \text{kernel_size[0]}, \text{kernel_size[1]})`,
    where `group` is the number of groups dividing `x`'s input channel when applying group convolution.

    For more details about convolution layer, please refer to `Gradient Based Learning Applied to Document Recognition
    <http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf>`_ and
    `ConvNets <http://cs231n.github.io/convolutional-networks/>`_.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C_{in}, H_{in}, W_{in})` or :math:`(C_{in}, H_{in}, W_{in})`.
        weight (Tensor): Tensor of shape
            :math:`(N, C_{in} / \text{groups}, \text{kernel_size[0]}, \text{kernel_size[1]})`, then the size of kernel
            is :math:`(\text{kernel_size[0]}, \text{kernel_size[1]})`.
        bias (Tensor, optional): Bias Tensor with shape :math:`(C_{out})`.
            When bias is ``None`` , zeros will be used. Default: ``None`` .
        stride (Union(int, tuple[int], list[int]), optional): The distance of kernel moving, an int number that
            represents the height and width of movement are both strides, or a tuple of two int numbers that
            represent height and width of movement respectively. Default: ``1`` .
        padding (Union[int, tuple[int], list[int], str], optional): The number of padding
            on the height and width directions of the input.
            The data type is an integer or a tuple of two integers or string {`valid`, `same`}. If `padding` is an
            integer, then `padding_{H}` and `padding_{W}` are all equal to `padding`.
            If `padding` is a tuple of 2 integers, then `padding_{H}` and `padding_{W}`
            is equal to `padding[0]` and `padding[1]` respectively.
            The value should be greater than or equal to 0. Default: ``0`` .

            - ``"same"``: Pad the input around its edges so that the shape of input and output
              are the same when `stride` is set to ``1``.
              The amount of padding to is calculated by the operator internally, If the amount is even, it is
              uniformly distributed around the input, if it is odd, the excess amount goes to the right/bottom side.
              If this mode is set, `stride` must be 1.

            - ``"valid"``: No padding is applied to the input, and the output returns the maximum
              possible height and width. Extra pixels that could not complete a full stride will
              be discarded.

        dilation (Union(int, tuple[int], list[int]), optional): Gaps between kernel elements.The data type
            is int or a tuple of 2 integers. Specifies the dilation rate to use for dilated convolution.
            If set to be :math:`k > 1`,
            there will be :math:`k - 1` pixels skipped for each sampling location. Its value must
            be greater than or equal to 1 and bounded by the height and width of the input `x`. Default: ``1`` .
        groups (int, optional): Splits `input` into groups. Default: ``1`` .

            - :math:`(C_{in} \text{ % } \text{groups} == 0)` , :math:`(C_{out} \text{ % } \text{groups} == 0)` ,
              :math:`(C_{out} >= \text{groups})` , :math:`(\text{weight[1]} = C_{in} / \text{groups})`

    Returns:
        Tensor, the value that applied 2D convolution. The shape is :math:`(N, C_{out}, H_{out}, W_{out})`.
        To see how different pad modes affect the output shape, please refer to
        :class:`mindspore.mint.nn.Conv2d` for more details.

    Raises:
        ValueError: Args and size of the input feature map should satisfy the output formula to ensure that the size of
            the output feature map is positive; otherwise, an error will be reported. For more details on the output
            formula, please refer to :class:`mindspore.mint.nn.Conv2d`.
        RuntimeError: On Ascend, due to the limitation of the L1 cache size of different NPU chip, if input size or
            kernel size is too large, it may trigger an error.
        TypeError: If `in_channels` , `out_channels` or `groups` is not an int.
        TypeError: If `kernel_size` , `stride` or `dilation` is neither an int nor a tuple.
        TypeError: If `bias` is not a Tensor.
        ValueError: If  the shape of `bias` is not :math:`(C_{out})` .
        ValueError: If `stride` or `dilation` is less than 1.
        ValueError: If `padding` is `same` , `stride` is not equal to 1.
        ValueError: The input parameters do not satisfy the convolution output formula.
        ValueError: The KernelSize cannot exceed the size of the input feature map.
        ValueError: The value of padding cannot cause the calculation area to exceed the input size.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops, mint
        >>> x = Tensor(np.ones([10, 32, 32, 32]), mindspore.float32)
        >>> weight = Tensor(np.ones([32, 32, 3, 3]), mindspore.float32)
        >>> output = mint.nn.functional.conv2d(x, weight)
        >>> print(output.shape)
        (10, 32, 30, 30)
    """
    if isinstance(padding, (int, tuple, list)):
        return conv2d_ext_op(input, weight, bias, stride, padding, dilation, groups)
    if isinstance(padding, str):
        return conv2d_padding_op(input, weight, bias, stride, padding, dilation, groups)
    raise TypeError(f"For conv2d, the parameter 'padding' must be a tuple/list " \
                    f"or a string, but got {type(padding)}")


def hardtanh(input, min_val=-1.0, max_val=1.0):
    r"""
    Applies the hardtanh activation function element-wise. The activation function is defined as:

    .. math::
        \text{hardtanh}(input) = \begin{cases}
            max\_val, & \text{ if } input > max\_val \\
            min\_val, & \text{ if } input < min\_val \\
            input, & \text{ otherwise. }
        \end{cases}

    Linear region range :math:`[min\_val, max\_val]` can be adjusted using `min_val` and `max_val`.

    Hardtanh Activation Function Graph:

    .. image:: ../images/Hardtanh.png
        :align: center

    Args:
        input (Tensor): Input Tensor.
        min_val (Union[int, float], optional): Minimum value of the linear region range. Default: ``-1.0`` .
        max_val (Union[int, float], optional): Maximum value of the linear region range. Default: ``1.0`` .

    Returns:
        Tensor, with the same dtype and shape as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `min_val` is neither float nor int.
        TypeError: If dtype of `max_val` is neither float nor int.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> x = Tensor([-1, -2, 0, 2, 1], mindspore.float16)
        >>> output = ops.hardtanh(x, min_val=-1.0, max_val=1.0)
        >>> print(output)
        [-1. -1.  0.  1.  1.]
    """
    _check_is_tensor('input', input, "hardtanh")
    _check_value_type("min_val", min_val, [int, float], "hardtanh")
    _check_value_type("max_val", max_val, [int, float], "hardtanh")
    input_dtype = input.dtype
    input = maximum_(input, min_val)
    input = minimum_(input, max_val)
    return input.astype(input_dtype)


def huber_loss(input, target, reduction='mean', delta=1.0):
    r"""
    Calculates the error between the predicted value and the target value,
    which has the best of both the loss of :func:`mindspore.ops.l1_loss` and the loss of :func:`mindspore.ops.mse_loss`.

    Assuming that the :math:`x` and :math:`y` are 1-D Tensor, length :math:`N`, the `reduction` parameter
    is set to ``'none'`` then calculate the loss of :math:`x` and :math:`y` without dimensionality reduction.
    The formula is as follows:

    .. math::
        \ell(x, y) = L = \{l_1,\dots,l_N\}^\top

    with

    .. math::
        l_n = \begin{cases}
            0.5 * (x_n - y_n)^2, & \text{if } |x_n - y_n| < delta; \\
            delta * (|x_n - y_n| - 0.5 * delta), & \text{otherwise. }
        \end{cases}

    where :math:`N` is the batch size.

    If `reduction` is "mean" or "sum", then:

    .. math::
        \ell(x, y) =
        \begin{cases}
            \operatorname{mean}(L), & \text{if reduction} = \text{"mean";}\\
            \operatorname{sum}(L),  & \text{if reduction} = \text{"sum".}
        \end{cases}

    Args:
        input (Tensor): Predicted value, Tensor of any dimension.
        target (Tensor): Target value, has same dtype and shape as the `input` in common cases.
            However, when the shape of `target` is different from the shape of `input`,
            and they should be broadcasted to each other.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

        delta (Union[int, float]): The threshold to change between two type of loss.
            The value must be greater than zero. Default: ``1.0`` .

    Returns:
        Tensor or Scalar, if `reduction` is ``'none'``, return a Tensor with same shape and dtype as `input`.
        Otherwise, a scalar value will be returned.

    Raises:
        TypeError: If `input` or `target` is not a Tensor.
        TypeError: If dtype of `delta` is neither float nor int.
        ValueError: If `delta` is less than or equal to 0.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``.
        ValueError: If `input` and `target` have different shapes and cannot be broadcasted to each other.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> x = Tensor([1, 2, 10, 2], mindspore.float32)
        >>> target = Tensor([1, 5, 1, 20], mindspore.float32)
        >>> output = ops.huber_loss(x, target, reduction="mean", delta=2)
        >>> print(output)
        13.5
    """
    _check_is_tensor('input', input, "huber_loss")
    _check_is_tensor('target', target, "huber_loss")
    _check_value_type("delta", delta, [int, float], "huber_loss")
    _check_number_gt_value("delta", delta, 0.0, "huber_loss")
    z = sub_(input, target)
    z = abs_(z)
    cond = less_(z, delta)
    l1 = mul_(0.5, square_(z))
    l2 = mul_(delta, sub_(z, 0.5 * delta))
    loss = select_(cond, l1, l2)
    return _get_loss(loss, reduction, "huber_loss")


@_primexpr
def _check_adaptive_avg_pool1d_output_size(output_size):
    """Check the output_size value in adaptive_avg_pool1d op."""
    validator.check_int(output_size, 1, validator.GE, "output_size", 'adaptive_avg_pool1d')
    validator.check_value_type('output_size', output_size, [int], 'adaptive_avg_pool1d')


def adaptive_avg_pool1d(input, output_size):
    r"""
    Applies a 1D adaptive average pooling over an input Tensor which can be regarded as a composition of 1D input
    planes.

    Typically, the input is of shape :math:`(N, C, L_{in})`, adaptive_avg_pool1d outputs regional average
    in the :math:`L_{in}`-dimension. The output is of shape :math:`(N, C, L_{out})`, where :math:`L_{out}`
    is defined by `output_size`.

    Note:
        :math:`L_{in}` must be divisible by `output_size`.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C, L_{in})`, with float16 or float32 data type.
        output_size (int): the target output size :math:`L_{out}`.

    Returns:
        Tensor of shape :math:`(N, C, L_{out})`, has the same type as `input`.

    Raises:
        TypeError: If `output_size` is not an int.
        TypeError: If `input` is neither float16 nor float32.
        ValueError: If `output_size` is less than 1.
        ValueError: If length of shape of `input` is not equal to 3.
        ValueError: If the last dimension of `input` is smaller than `output_size`.
        ValueError: If the last dimension of `input` is not divisible by `output_size`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.random.randint(0, 10, [1, 3, 6]), mindspore.float32)
        >>> output = ops.adaptive_avg_pool1d(input, output_size=2)
        >>> print(output.shape)
        (1, 3, 2)
    """

    def _check(x, output_size):
        x_in_shape = x.shape
        x_dtype = dtype_(x)
        if not isinstance(x, (Tensor, Tensor_)):
            raise TypeError("For adaptive_avg_pool1d, the input input must be tensor")

        _check_adaptive_avg_pool1d_output_size(output_size)

        if len(x_in_shape) != 3:
            raise ValueError(f"For adaptive_avg_pool1d input must have 3 dim, but got {len(x_in_shape)}.")
        if x_in_shape[2] < output_size:
            raise ValueError(f"For adaptive_avg_pool1d input's last dimension must be greater or equal to " \
                             f"output size {output_size}, but got {x_in_shape[2]}.")
        if x_in_shape[2] % output_size != 0:
            raise ValueError(f"For adaptive_avg_pool1d input's last dimension must be divisible by "
                             f"output size {output_size}, but got {x_in_shape[2]}.")
        if x_dtype not in [mstype.float16, mstype.float32]:
            raise TypeError(f"For adaptive_avg_pool1d, the input dtype must be float16 or float32, " \
                            f"but got {x_dtype}.")

    _check(input, output_size)
    x_in_shape = input.shape
    squeeze_ = _get_cache_prim(P.Squeeze)(2)
    width = x_in_shape[2]
    stride = width // output_size
    kernel_size = width - (output_size - 1) * stride
    stride = (1, width // output_size)
    kernel_size = (1, kernel_size)
    avg_pool_ = _get_cache_prim(P.AvgPool)(kernel_size=kernel_size, strides=stride)
    input = expand_dims_(input, 2)
    input = avg_pool_(input)
    input = squeeze_(input)
    return input


def layer_norm(input, normalized_shape, weight=None, bias=None, eps=1e-5):
    r"""Applies the Layer Normalization on the mini-batch input.

    Layer normalization is widely used in recurrent neural networks. Apply normalization to the mini-batch
    input of a single training case. LayerNorm is described in the paper
    `Layer Normalization <https://arxiv.org/abs/1607.06450>`_.

    Unlike batch normalization, layer normalization performs the exact same calculations at training and
    test time. Applies to all channels and pixels, even batch_size=1. The formula is as follows:

    .. math::
        y = \frac{x - \mathrm{E}[x]}{\sqrt{\mathrm{Var}[x] + \epsilon}} * \gamma + \beta

    where :math:`\gamma` is the weight value learned through training, :math:`\beta` is the bias value
    learned through training.

    Args:
        input (Tensor): The shape of input is `(N, *)`, where `*` represents any additional dimension.
        normalized_shape (Union(int, tuple[int], list[int])): The normalized shape of `input` for LayerNorm.
          `normalized_shape` equal to `input_shape[begin_norm_axis:]`, where `begin_norm_axis` represents the axis
          where normalization begins.
        weight (Tensor, optional): Learnable parameter :math:`\gamma` . Tensor of shape `normalized_shape`.
          Default: ``None``, has the same data type with `input`. Initialized to ``1`` when `weight` is None.
        bias (Tensor, optional): Learnable parameter :math:`\beta` . Tensor of shape `normalized_shape`.
          Default: ``None``, has the same data type with `input`. Initialized to ``0`` when `bias` is None.
        eps (float, optional): A value added to the denominator for numerical stability(:math:`\epsilon`).
          Default: ``1e-5`` .

    Returns:
        Tensor. The normalized tensor, has the same type and shape as the `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `normalized_shape` is not an integer, a list or a tuple.
        TypeError: If `eps` is not a float.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.array([[1, 2, 3], [1, 2, 3]]), mindspore.float32)
        >>> normalized_shape = (3,)
        >>> gamma = Tensor(np.ones(normalized_shape), mindspore.float32)
        >>> beta = Tensor(np.zeros(normalized_shape), mindspore.float32)
        >>> eps = 1e-7
        >>> output = ops.layer_norm(input_x, normalized_shape, gamma, beta, eps)
        >>> print(output)
        [[-1.2247448 0. 1.2247448]
         [-1.2247448 0. 1.2247448]]
    """
    if weight is None:
        weight = ops.ones(normalized_shape, dtype=input.dtype)
    if bias is None:
        bias = ops.zeros(normalized_shape, dtype=input.dtype)
    return layer_norm_ext_op(input, normalized_shape, weight, bias, eps)[0]


def add_layer_norm(x1, x2, gamma, beta, epsilon=1e-5, additional_output=False):
    r"""
    Implements the add_layer_norm algorithm.

    .. math::
        \begin{aligned}
        x = x1 + x2                                                                      \\
        y = \frac{x - \mathrm{E}[x]}{\sqrt{\mathrm{Var}[x] + \epsilon}} * \gamma + \beta \\
        \end{aligned}

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        x1 (Tensor): Input of Addition Calculation in AddLayerNorm. `x1 + x2` will be calculated in the operator
            and the calculation result is normalized. Data type is float16, bfloat16 or float32 .
        x2 (Tensor): Input of Addition Calculation in AddLayerNorm. `x1 + x2` will be calculated in the operator
            and the calculation result is normalized. Has the same dtype and shape as the `x1`.
        gamma (Tensor): Learnable parameter :math:`\gamma` . Tensor of shape is 1D, keep same with last
            dimension `x1` .
        beta (Tensor): Learnable parameter :math:`\beta` . Tensor of shape is 1D, keep same with last dimension `x1` .
        epsilon (float, optional): A value added to the denominator for numerical stability(:math:`\epsilon`).
            Default: ``1e-5`` .
        additional_output (bool, optional): Indicates whether to enable the output of `x=x1+x2`.
            Default: ``False`` .

    Returns:
        tuple [Tensor], tuple of 4 Tensors. the output of normalized input and the updated parameters.

        - **y** (Tensor) - Output of normalization, has the same type as the `x1`.
        - **mean** (Tensor) - The mean of input, has the same type as the `x1`.
        - **rstd** (Tensor) - The reciprocal of the input standard deviation. Shape is the same as `mean` .
        - **x** (Tensor) - output of `x1 + x2`.

    Raises:
        TypeError: If `x1` is not a Tensor.
        TypeError: If `x2` is not a Tensor.
        TypeError: If `gamma` is not a Tensor.
        TypeError: If `beta` is not a Tensor.
        TypeError: If `epsilon` is not a float.
        TypeError: If `additional_output` is not a bool.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x1 = Tensor(np.array([[1, 2, 3], [1, 2, 3]]), mindspore.float32)
        >>> x2 = Tensor(np.array([[1, 2, 3], [1, 2, 3]]), mindspore.float32)
        >>> gamma = Tensor(np.ones([3]), mindspore.float32)
        >>> beta = Tensor(np.zeros([3]), mindspore.float32)
        >>> epsilon = 1e-7
        >>> output = ops.add_layer_norm(x1, x2, gamma, beta, epsilon)
        >>> print(output[0])
        [[-1.2247448 0 1.2247448]
         [-1.2247448 0 1.2247448]]
        >>> print(output[1])
        [[4]
         [4]]
        >>> print(output[2])
        [[0.6123724]
         [0.6123724]]
    """
    return add_layernorm_v2_op(x1, x2, gamma, beta, epsilon, additional_output)


def group_norm(input, num_groups, weight=None, bias=None, eps=1e-5):
    r"""Group Normalization over a mini-batch of inputs.

    Group Normalization is widely used in recurrent neural networks. It applies
    normalization on a mini-batch of inputs for each single training case as described
    in the paper `Group Normalization <https://arxiv.org/pdf/1803.08494.pdf>`_. Group Normalization
    divides the channels into groups and computes within each group the mean and variance for normalization,
    and it performs very stable over a wide range of batch size. :math:`\gamma` and :math:`\beta` are trainable scale
    and shift.
    It can be described using the following formula:

    .. math::
        y = \frac{x - \mathrm{E}[x]}{\sqrt{\mathrm{Var}[x] + \epsilon}} * \gamma + \beta

    where :math:`\gamma` is `weight`, :math:`\beta` is `bias`, :math:`\epsilon` is `eps`.

    Args:
        input (Tensor): The input feature with shape :math:`(N, C, *)` where :math:`*` means, any number of
            additional dimensions.
        num_groups (int): The number of groups to be divided along the channel dimension.
        weight (Tensor, optional): The shape :math:`(C,)`, Default: ``None``, has the same data type with `input`.
        bias (Tensor, optional): The shape :math:`(C,)`, Default: ``None``, has the same data type with `input`.
        eps (float, optional): A value added to the denominator for numerical stability. Default: ``1e-5`` .

    Returns:
        Tensor, the normalized and scaled offset tensor, has the same shape and data type as the `input`.

    Raises:
        TypeError: If `num_groups` is not an int.
        TypeError: If `eps` is not a float.
        ValueError: If `num_groups` is less than 1.
        ValueError: If `C` (the second parameter of dimensions of `input`) is not divided by `num_groups`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore as ms
        >>> import numpy as np
        >>> from mindspore import ops
        >>> x = ms.Tensor(np.ones([1, 2, 4, 4], np.float32))
        >>> output = ops.group_norm(x, 2)
        >>> print(output)
        [[[[0. 0. 0. 0.]
           [0. 0. 0. 0.]
           [0. 0. 0. 0.]
           [0. 0. 0. 0.]]
          [[0. 0. 0. 0.]
           [0. 0. 0. 0.]
           [0. 0. 0. 0.]
           [0. 0. 0. 0.]]]]
    """
    if weight is None:
        weight = ops.ones([input.shape[1]], dtype=input.dtype)
    if bias is None:
        bias = ops.zeros([input.shape[1]], dtype=input.dtype)
    return group_norm_op(input, num_groups, weight, bias, eps)[0]


def batch_norm_ext(input, running_mean, running_var, weight=None, bias=None, training=False, momentum=0.1, eps=1e-5):
    r"""
    Batch Normalization for input data and updated parameters.

    Batch Normalization is widely used in convolutional neural networks. This operation
    applies Batch Normalization over inputs to avoid internal covariate shift as described
    in the paper `Batch Normalization: Accelerating Deep Network Training by Reducing Internal
    Covariate Shift <https://arxiv.org/abs/1502.03167>`_. It rescales and recenters the
    features using a mini-batch of data and the learned parameters can be described
    in the following formula,

    .. math::

        y = \frac{x - mean}{\sqrt{variance + \epsilon}} * \gamma + \beta

    where :math:`\gamma` is `weight`, :math:`\beta` is `bias`, :math:`\epsilon` is `eps`, :math:`mean` is the
    mean of :math:`x`, :math:`variance` is the variance of :math:`x`.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C, *)`, with bfloat16, float16 or float32 data type.
            For Atlas training products, the shape must be 2-4 dimensions currently.
        running_mean (Tensor): The shape :math:`(C,)`, with bfloat, float16 or float32 data type.
        running_var (Tensor): The shape :math:`(C,)`, with bfloat, float16 or float32 data type.
        weight (Tensor, optional): The shape :math:`(C,)`, with bfloat, float16 or float32 data type, Default: ``None``.
            Initialized to ``1`` when `weight` is None.
        bias (Tensor, optional): The shape :math:`(C,)`, with bfloat, float16 or float32 data type. Default: ``None``.
            Initialized to ``0`` when `weight` is None.
        training (bool, optional): If `training` is `True`, `mean` and `variance` are computed during training.
            If `training` is `False`, they're loaded from checkpoint during inference. Default: ``False`` .
        momentum (float, optional): The hyper parameter to compute moving average for `running_mean` and `running_var`
            (e.g. :math:`new\_running\_mean = (1 - momentum) * running\_mean + momentum * current\_mean`).
            Default: ``0.1`` .
        eps (float, optional): A small value added for numerical stability. Default: ``1e-5``.

    Returns:
        Tensor, has the same type and shape as `input`. The shape is :math:`(N, C, *)`.

    Raises:
        TypeError: If `training` is not a bool.
        TypeError: If dtype of `eps` or `momentum` is not float.
        TypeError: If `input`, `weight`, `bias`, `running_mean` or `running_var` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor([[1.0, 2.0], [3.0, 4.0]], mindspore.float32)
        >>> running_mean = Tensor([0.5, 1.5], mindspore.float32)
        >>> running_var = Tensor([0.1, 0.2], mindspore.float32)
        >>> weight = Tensor([2.0, 2.0], mindspore.float32)
        >>> bias = Tensor([-1.0, -1.0], mindspore.float32)
        >>> output = ops.function.nn_func.batch_norm_ext(input_x, running_mean, running_var, weight, bias)
        >>> print(output)
        [[ 2.1621194  1.2360122]
         [14.810596  10.180061 ]]
    """
    output = batch_norm_ext_op(input, weight, bias, running_mean, running_var, training, momentum, eps)
    return output[0]


def batch_norm(input_x, running_mean, running_var, weight, bias, training=False, momentum=0.1, eps=1e-5):
    r"""
    Batch Normalization for input data and updated parameters.

    Batch Normalization is widely used in convolutional neural networks. This operation
    applies Batch Normalization over inputs to avoid internal covariate shift as described
    in the paper `Batch Normalization: Accelerating Deep Network Training by Reducing Internal
    Covariate Shift <https://arxiv.org/abs/1502.03167>`_. It rescales and recenters the
    features using a mini-batch of data and the learned parameters can be described
    in the following formula,

    .. math::

        y = \frac{x - mean}{\sqrt{variance + \epsilon}} * \gamma + \beta

    where :math:`\gamma` is `weight`, :math:`\beta` is `bias`, :math:`\epsilon` is `eps`, :math:`mean` is the
    mean of :math:`x`, :math:`variance` is the variance of :math:`x`.

    .. warning::
        - For Atlas 200/300/500 inference product,
          the result accuracy fails to reach 1‰ due to the square root instruction.

    Note:
        - If `training` is `False`, `weight`, `bias`, `running_mean` and `running_var` are Tensors.
        - If `training` is `True`, `weight`, `bias`, `running_mean` and `running_var` are Parameters.

    Args:
        input_x (Tensor): Tensor of shape :math:`(N, C)`, with float16 or float32 data type.
        running_mean (Union[Tensor, Parameter]): The shape :math:`(C,)`, has the same data type with `weight`.
        running_var (Union[Tensor, Parameter]): The shape :math:`(C,)`, has the same data type with `weight`.
        weight (Union[Tensor, Parameter]): The shape :math:`(C,)`, with float16 or float32 data type.
        bias (Union[Tensor, Parameter]): The shape :math:`(C,)`, has the same data type with `weight`.
        training (bool, optional): If `training` is `True`, `mean` and `variance` are computed during training.
            If `training` is `False`, they're loaded from checkpoint during inference. Default: ``False`` .
        momentum (float, optional): The hyper parameter to compute moving average for `running_mean` and `running_var`
            (e.g. :math:`new\_running\_mean = (1 - momentum) * running\_mean + momentum * current\_mean`).
            Momentum value must be `[0, 1]`. Default: ``0.1`` .
        eps (float, optional): A small value added for numerical stability. Default: ``1e-5``, value must be `(0, 1]` .

    Returns:
        output_x (Tensor) - The same type and shape as the `input_x`. The shape is :math:`(N, C)`.

    Raises:
        TypeError: If `training` is not a bool.
        TypeError: If dtype of `eps` or `momentum` is not float.
        TypeError: If `input_x`, `weight`, `bias`, `running_mean` or `running_var` is not a Tensor.
        TypeError: If dtype of `input_x`, `weight` is neither float16 nor float32.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor([[1.0, 2.0], [3.0, 4.0]], mindspore.float32)
        >>> running_mean = Tensor([0.5, 1.5], mindspore.float32)
        >>> running_var = Tensor([0.1, 0.2], mindspore.float32)
        >>> weight = Tensor([2.0, 2.0], mindspore.float32)
        >>> bias = Tensor([-1.0, -1.0], mindspore.float32)
        >>> output = ops.batch_norm(input_x, running_mean, running_var, weight, bias)
        >>> print(output)
        [[ 2.1621194  1.2360122]
         [14.810596  10.180061 ]]
    """
    batch_norm_op = _get_cache_prim(P.BatchNorm)(is_training=training, epsilon=eps, momentum=momentum)
    output = batch_norm_op(input_x, weight, bias, running_mean, running_var)
    return output[0]


def bias_add(input_x, bias):
    r"""
    Returns the sum of the `input_x` and the `bias` Tensor. Before adding, the `bias` Tensor will be broadcasted to be
    consistent with the shape of the `input_x` Tensor.

    Args:
        input_x (Tensor): The input tensor. The shape can be 2-5 dimensions. Supported dtypes:

            - Ascend/CPU: all Number type.
            - GPU: float16, float32, int8.

        bias (Tensor): The bias tensor, with shape :math:`(C)`. C must be the same as channel dimension C of
            `input_x`. It has the same type as `input_x`.

    Returns:
        Tensor, with the same shape and data type as `input_x`.

    Raises:
        TypeError: If `input_x` or `bias` is not a Tensor.
        TypeError: If dtype of `input_x` and `bias` is inconsistent.
        TypeError: If dimension of `input_x` is not in the range [2, 5].

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.arange(6).reshape((2, 3)), mindspore.float32)
        >>> bias = Tensor(np.random.random(3).reshape((3)), mindspore.float32)
        >>> output = ops.bias_add(input_x, bias)
        >>> print(output.shape)
        (2, 3)
    """
    bias_add_op = _get_cache_prim(P.BiasAdd)(data_format="NCHW")
    return bias_add_op(input_x, bias)


def binary_cross_entropy(logits, labels, weight=None, reduction='mean'):
    r"""
    Computes the binary cross entropy(Measure the difference information between two probability distributions) between
    predictive value `logits` and target value `labels`.

    Set `logits` as :math:`x`, `labels` as :math:`y`, output as :math:`\ell(x, y)`, the
    weight of nth batch of binary cross entropy is :math:`w_n`.
    Let,

    .. math::
        L = \{l_1,\dots,l_N\}^\top, \quad
        l_n = - w_n \left[ y_n \cdot \log x_n + (1 - y_n) \cdot \log (1 - x_n) \right]

    In which, :math:`L` indicates the loss of all `batch_size`, :math:`l` indicates the loss of one `batch_size`,
    and :math:`n` indicates one `batch_size` in the :math:`1-N` range. Then,

    .. math::
        \ell(x, y) = \begin{cases}
        L, & \text{if reduction} = \text{'none';}\\
        \operatorname{mean}(L), & \text{if reduction} = \text{'mean';}\\
        \operatorname{sum}(L),  & \text{if reduction} = \text{'sum'.}
        \end{cases}

    .. warning::
        - The value of `logits` must range from `0` to `l`.

    Args:
        logits (Tensor): The predictive value whose data type must be float16 or float32.
        labels (Tensor): The target value which has the same shape and data type as `logits`.
            And the data type is float16 or float32.
        weight (Tensor, optional): A rescaling weight applied to the loss of each batch element.
            Its shape must be able to broadcast to that of `logits` and `labels`.
            And it must have the same shape and data type as `logits`. Default: ``None`` . If set to ``None`` ,
            the loss function
            will not consider any sample weights, and each sample will be treated as having equal importance
            when calculating the loss.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor or Scalar. Returns Tensor that has the same dtype and shape as `logits` if `reduction` is ``'none'``.
        Otherwise, returns a scalar Tensor.

    Raises:
        TypeError: If `logits`, `labels` or `weight` is not a Tensor.
        TypeError: If dtype of `logits`, `labels` or `weight` (if given) is neither float16 nor float32.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'`` or ``'sum'``.
        ValueError: If shape of `labels` is not the same as `logits` or `weight` (if given).

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> logits = Tensor(np.array([0.2, 0.7, 0.1]), mindspore.float32)
        >>> labels = Tensor(np.array([0., 1., 0.]), mindspore.float32)
        >>> weight = Tensor(np.array([1, 2, 2]), mindspore.float32)
        >>> output = ops.binary_cross_entropy(logits, labels, weight)
        >>> print(output)
        0.38240486
    """
    binary_cross_entropy_op = _get_cache_prim(P.BinaryCrossEntropy)(reduction=reduction)
    return binary_cross_entropy_op(logits, labels, weight)


def conv3d(input, weight, bias=None, stride=1, pad_mode="valid", padding=0, dilation=1, groups=1):
    r"""
    Applies a 3D convolution over an input tensor. The input tensor is typically of
    shape :math:`(N, C_{in}, D_{in}, H_{in}, W_{in})`, where :math:`N` is batch size, :math:`C`
    is channel number, :math:`D, H, W` are the depth, height and width of the feature graph, respectively.

    The output is calculated based on formula:

    .. math::

        \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
        \sum_{k = 0}^{C_{in} - 1} \text{ccor}({\text{weight}(C_{\text{out}_j}, k), \text{X}(N_i, k)})

    where :math:`bias` is the output channel bias, :math:`ccor` is
    the `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`_
    , :math:`weight` is the convolution kernel value and :math:`X` represents the input feature map.

    Here are the indices' meanings:

    - :math:`i` corresponds to the batch number, the range is :math:`[0, N-1]`,
      where :math:`N` is the batch size of the input.

    - :math:`j` corresponds to the output channel, the range is :math:`[0, C_{out}-1]`,
      where :math:`C_{out}` is the number of
      output channels, which is also equal to the number of kernels.

    - :math:`k` corresponds to the input channel, the range is :math:`[0, C_{in}-1]`,
      where :math:`C_{in}` is the number of
      input channels, which is also equal to the number of channels in the convolutional kernels.

    Therefore, in the above formula, :math:`{bias}(C_{\text{out}_j})` represents the bias of the :math:`j`-th
    output channel, :math:`{weight}(C_{\text{out}_j}, k)` represents the slice of the :math:`j`-th convolutional
    kernel in the :math:`k`-th channel, and :math:`{X}(N_i, k)` represents the slice of the :math:`k`-th input
    channel in the :math:`i`-th batch of the input feature map.

    The shape of the convolutional kernel is given by
    :math:`(\text{kernel_size[0]}, \text{kernel_size[1]}, \text{kernel_size[2]})`
    where :math:`\text{kernel_size[0]}` , :math:`\text{kernel_size[1]}` and :math:`\text{kernel_size[2]}` are the depth,
    height and width of the kernel, respectively.
    If we consider the input and output channels as well as the `groups` parameter, the complete kernel shape
    will be :math:`(C_{out}, C_{in} / \text{groups}, \text{kernel_size[0]},
    \text{kernel_size[1]}, \text{kernel_size[2]})`,
    where `groups` is the number of groups dividing `x`'s input channel when applying group convolution.

    For more details about convolution layer, please refer to `Gradient Based Learning Applied to Document Recognition
    <http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf>`_.

    Note:
        1. On Ascend platform, :math:`groups = 1` must be satisfied.
        2. On Ascend platform, :math:`dilation=1` must be satisfied.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C_{in}, D_{in}, H_{in}, W_{in})`.
        weight (Tensor): Set size of kernel is :math:`(\text{kernel_size[0]}, \text{kernel_size[1]},
            \text{kernel_size[2]})`, then the shape is :math:`(C_{out}, C_{in}, \text{kernel_size[0]},
            \text{kernel_size[1]}, \text{kernel_size[1]})`.
        bias (Tensor, optional): Bias Tensor with shape :math:`(C_{out})`.
            When bias is None, zeros will be used. Default: ``None`` .
        stride (Union[int, tuple[int]], optional): The distance of kernel moving,
            it can be an int number that represents
            the depth, height and width of movement or a tuple of three int numbers that
            represent depth, height and width movement respectively. Default: ``1`` .
        pad_mode (str, optional): Specifies padding mode. The optional values are
            ``"same"`` , ``"valid"`` and ``"pad"`` . Default: ``"valid"`` .

            - ``"same"``: Adopts the way of completion. The depth, height and width of the output will be equal to
              the input `x` divided by stride. The padding will be evenly calculated in head and tail, top and bottom,
              left and right directions possiblily.
              Otherwise, the last extra padding will be calculated from the tail, bottom and the right side.
              If this mode is set, `pad` must be 0.

            - ``"valid"``: Adopts the way of discarding. The possible largest depth, height and width of output
              will be returned without padding. Extra pixels will be discarded. If this mode is set, `pad`
              must be 0.

            - ``"pad"``: Implicit paddings on both sides of the input in depth, height and width.
              The number of `pad` will be padded to the input Tensor borders. `pad` must be greater than or equal to 0.

        padding (Union[int, tuple[int], list[int]], optional): The pad value to be filled. If `pad` is an integer,
            the paddings of head, tail, top, bottom, left and right are the same, equal to pad.
            If `pad` is a tuple/list of 3 integers, the padding of head, tail, top, bottom,
            left and right equal to pad[0], pad[0], pad[1], pad[1], pad[2] and pad[2] correspondingly. Default: ``0`` .
        dilation (Union[int, tuple[int]], optional): The data type is int or a tuple of 3 integers
            :math:`(dilation_d, dilation_h, dilation_w)`. Currently, dilation on depth only supports the case of 1
            on Ascend backend. Specifies the dilation rate to use for dilated convolution. If set :math:`k > 1`,
            there will be :math:`k - 1` pixels skipped for each sampling location.
            The value ranges for the depth, height, and width dimensions are [1, D], [1, H], and [1, W],
            respectively. Default: ``1`` .
        groups (int, optional):The number of groups into which the filter is divided. Default: ``1`` .

    Returns:
        Tensor, the value that applied 3D convolution. The shape is :math:`(N, C_{out}, D_{out}, H_{out}, W_{out})`.
        To see how different pad modes affect the output shape, please refer to
        :class:`mindspore.nn.Conv3d` for more details.

    Raises:
        TypeError: If `out_channel` or `groups` is not an int.
        TypeError: If `stride`, `padding` or `dilation` is neither an int nor a tuple.
        TypeError: If `bias` is not a Tensor.
        ValueError: If the shape of `bias` is not :math:`(C_{out})`.
        ValueError: If `stride` or `dilation` is less than 1.
        ValueError: If `pad_mode` is not one of 'same', 'valid' or 'pad'.
        ValueError: If `padding` is a tuple or list whose length is not equal to 3.
        ValueError: If `pad_mode` is not equal to 'pad' and `pad` is greater than 0.

    Supported Platforms:
        ``Ascend`` ``GPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.ones([16, 3, 10, 32, 32]), mindspore.float16)
        >>> weight = Tensor(np.ones([32, 3, 4, 3, 3]), mindspore.float16)
        >>> output = ops.conv3d(x, weight, pad_mode="same", padding=0, stride=1, dilation=1, groups=1)
        >>> print(output.shape)
        (16, 32, 10, 32, 32)
        >>> output = ops.conv3d(x, weight, pad_mode="valid", padding=0, stride=1, dilation=1, groups=1)
        >>> print(output.shape)
        (16, 32, 7, 30, 30)
        >>> output = ops.conv3d(x, weight, pad_mode="pad", padding=(2, 1, 1), stride=1, dilation=1, groups=1)
        >>> print(output.shape)
        (16, 32, 11, 32, 32)
    """
    weight_shape = weight.shape
    out_channel = weight_shape[0]
    kernel_size = weight_shape[2:5]
    if isinstance(stride, (tuple, list)):
        _check_conv_iterable_lengths(stride, dim=3, iter_name='stride')
    if isinstance(dilation, (tuple, list)):
        _check_conv_iterable_lengths(dilation, dim=3, iter_name='dilation')
    input_shape = input.shape
    in_channel = input_shape[1]
    if not (in_channel % groups == 0 and out_channel % groups == 0):
        raise ValueError("The argument 'groups' should be divisible by 'in_channel' " \
                         "and 'out_channel'")
    if isinstance(padding, (list, tuple)):
        padding = _manipulate_padding(padding, dim=3)
    conv = _get_cache_prim(P.Conv3D)(out_channel, kernel_size, 1, pad_mode, padding, stride, dilation, groups, "NCDHW")
    if bias is None:
        return conv(input, weight)
    if not isinstance(bias, Tensor):
        raise TypeError(f"For 'conv3d', the 'bias' must be a Tensor, but got {type(bias)}.")
    conv_result = conv(input, weight)
    output = bias_add(conv_result, bias)
    return output


def conv3d_ext(input, weight, bias=None, stride=1, padding=0, dilation=1, groups=1):
    r"""
    Applies a 3D convolution over an input tensor. The input tensor is typically of
    shape :math:`(N, C_{in}, D_{in}, H_{in}, W_{in})` or :math:`(C_{in}, D_{in}, H_{in}, W_{in})`,
    where :math:`N` is batch size, :math:`C` is channel number, :math:`D, H, W` are the depth,
    height and width of the feature graph, respectively.

    The output is calculated based on formula:

    .. math::

        \text{out}(N_i, C_{\text{out}_j}) = \text{bias}(C_{\text{out}_j}) +
        \sum_{k = 0}^{C_{in} - 1} \text{ccor}({\text{weight}(C_{\text{out}_j}, k), \text{X}(N_i, k)})

    where :math:`bias` is the output channel bias, :math:`ccor` is
    the `cross-correlation <https://en.wikipedia.org/wiki/Cross-correlation>`_
    , :math:`weight` is the convolution kernel value and :math:`X` represents the input feature map.

    Here are the indices' meanings:

    - :math:`i` corresponds to the batch number, the range is :math:`[0, N-1]`,
      where :math:`N` is the batch size of the input.

    - :math:`j` corresponds to the output channel, the range is :math:`[0, C_{out}-1]`,
      where :math:`C_{out}` is the number of
      output channels, which is also equal to the number of kernels.

    - :math:`k` corresponds to the input channel, the range is :math:`[0, C_{in}-1]`,
      where :math:`C_{in}` is the number of
      input channels, which is also equal to the number of channels in the convolutional kernels.

    Therefore, in the above formula, :math:`{bias}(C_{\text{out}_j})` represents the bias of the :math:`j`-th
    output channel, :math:`{weight}(C_{\text{out}_j}, k)` represents the slice of the :math:`j`-th convolutional
    kernel in the :math:`k`-th channel, and :math:`{X}(N_i, k)` represents the slice of the :math:`k`-th input
    channel in the :math:`i`-th batch of the input feature map.

    The shape of the convolutional kernel is given by :math:`(kd, kh, kw)` where :math:`kd` , :math:`kd` and\
    :math:`kw` are the depth, height and width of the kernel, respectively.
    If we consider the input and output channels as well as the `group` parameter, the complete kernel shape
    will be :math:`(C_{out}, C_{in} / \text{group}, kd, kh, kw)`,
    where `group` is the number of groups dividing `x`'s input channel when applying group convolution.

    For more details about convolution layer, please refer to `Gradient Based Learning Applied to Document Recognition
    <http://vision.stanford.edu/cs598_spring07/papers/Lecun98.pdf>`_.

    The following lists some of the limitations of the parameters.

    - input -- The input to the conv3d. The input must have each dimension size within the range [1, int32_max].
    - weight -- Filters of shape :math:`(C_{out}, C_{in} / groups, kd, kh, kw)`. The value of :math:`kh`
      and :math:`kw` is in the range [1, 511]. The remaining values are in the range [1, int32_max].
      And :math:`kh*kw*k0` is less 65536 (k0 is 16. If data type is float32, k0 is 8).
    - bias -- Bias Tensor with shape :math:`(C_{out})`. The shape must equal the first dimension of the weight.
    - stride -- The distance of kernel moving. It can be an int number or
      tuple (noted by :math:`(stride_d, stride_h, stride_w)`). stride_h and stride_w are in the range [1, 63].
      stride_d is in the range [1, 255].
    - padding -- If padding is an int number, it is in the range [0, 255].
    - dilation -- The value is in the range [1, 255].
    - groups -- The value is in the range [1, 65535].
    - :math:`C_{in} \% \text{groups} == 0 \quad \text{and} \quad C_{out} \% \text{groups} == 0` .
    - :math:`weight[1] == C_{in} / groups` .
    - :math:`H_{in} + PadUp + PadDown >= (kh - 1) * DilationH + 1` .
    - :math:`W_{in} + PadLeft + PadRight >= (kw - 1) * DilationW + 1` .
    - :math:`D_{in} + PadFront + PadBack >= (kd - 1) * DilationD + 1` .
    - :math:`H_{out} = (H_{in} + PadUp + PadDown - ((kh - 1) * DilationH + 1)) / StrideH + 1` .
    - :math:`W_{out} = (W_{in} + PadLeft + PadRight - ((kw - 1) * DilationW + 1)) / StrideW + 1` .
    - :math:`D_{out} = (D_{in} + PadFront + PadBack - ((kd - 1) * DilationD + 1)) / StrideD + 1` .
    - :math:`(D_{in}+PadFront+PadBack - ((kd-1)*DilationD+1)) \% StrideD <= PadBack` .
    - :math:`(H_{in}+PadUp+PadDown - ((kh-1)*Dilationh+1)) \% StrideH <= PadDown` .
    - :math:`stride_d <= kernel_d` .
    - :math:`PadUp < kh` and :math:`PadDown < kh` . When `padding` = ``'valid'``, both PadUp and PadDown are zeros.
      When `padding` = ``'same'``, pad can be calculated by
      :math:`floor(((H_{out}-1) * strideH + (kh - 1) * DilationH + 1 - H_{in}) / 2)` for high dimension.
      It is similar way to calculate the padding for depth and width dimension. And the depth and width
      dimensions also have the same constraints.
    - :math:`((kh - 1) * DilationH - PadUp)` should be in [0, 255]. It is the same constraint for depth
      and width dimension.
    - If `padding` is ``'same'``, `stride` must be 1.

    .. warning::
        This API does not support Atlas series products.

    Args:
        input (Tensor): Tensor of shape :math:`(N, C_{in}, D_{in}, H_{in}, W_{in})`.
        weight (Tensor): Set size of kernel is :math:`(kd, kh,
            kw)`, then the shape is :math:`(C_{out}, C_{in} / groups, kd, kh, kw)`.
        bias (Tensor, optional): Bias Tensor with shape :math:`(C_{out})`.
            When bias is ``None`` , zeros will be used. Default: ``None`` .
        stride (Union(int, tuple[int], list[int]), optional): The distance of kernel moving, an int
            number that represents the depth, the height and width of movement are both strides, or a
            tuple of triple int numbers that
            represent the depth, height and width of movement respectively. Default: ``1`` .
        padding (Union(int, tuple[int], list[int], str), optional): Implicit paddings on both sides of the input `x`.
            Can be a string, one integer or a tuple/list with 3 integers.
            If `padding` is a string, the optional values are ``"same"`` , ``"valid"``.

            - same: Adopts the way of completion. The height and width of the output will be equal to
              the input `x` divided by stride. The padding will be evenly calculated in top and bottom,
              left and right possiblily. Otherwise, the last extra padding will be calculated from the bottom
              and the right side. If this mode is set, `stride` must be 1.

            - valid: Adopts the way of discarding. The possible largest height and width of output will be returned
              without padding. Extra pixels will be discarded.

            If `padding` is one integer, the paddings of top, bottom, left and right are the same, equal to padding.
            If `padding` is a tuple/list with 3 integers, the padding of head, tail, top, bottom,
            left and right equal to pad[0], pad[0], pad[1], pad[1], pad[2] and pad[2] correspondingly. Default: ``0`` .
        dilation (Union[int, tuple[int], list[int]], optional): Controlling the space between the kernel points.
            Default: ``1`` .
        groups (int, optional): Splits `input` into groups. Default: ``1`` .

    Returns:
        Tensor, the same dtype as the `input`, with the shape :math:`(N, C_{out}, D_{out}, H_{out}, W_{out})`
        or :math:`(C_{out}, D_{out}, H_{out}, W_{out})`.

    Raises:
        TypeError: If `stride`, `padding` or `dilation` is neither an int nor a tuple.
        TypeError: `groups` is not an int.
        TypeError: If `bias` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import mint
        >>> x = mindspore.Tensor(np.random.randn(12, 1, 60, 50, 8), mindspore.float16)
        >>> w = mindspore.Tensor(np.random.randn(26, 1, 2, 4, 4), mindspore.float16)
        >>> out = mint.nn.functional.conv3d(x, w)
        >>> print(out.shape)
        (12, 26, 59, 47, 5)
    """

    return conv3d_op(input, weight, bias, stride, padding, dilation, groups)


@_primexpr
def _check_positive_int(arg_value, arg_name=None, prim_name=None):
    validator.check_positive_int(arg_value, arg_name=arg_name, prim_name=prim_name)


@_primexpr
def _check_pxiel_shuffle_valid(num, factor):
    if num % factor ** 2 != 0:
        raise ValueError("For 'pixel_shuffle', the length of third to last dimension is not divisible"
                         "by `upscale_factor` squared.")


def _check_pixel_shuffle_unshuffle_input_shape(input, cls_name):
    """Internal function, used to check whether the shape of pixel shuffle or unshuffle input meets the requirements."""
    if input.ndim < 3:
        raise ValueError(f"For {cls_name}, the dimension of `input` should be larger than 2, but got {input.ndim}.")


def pixel_shuffle(input, upscale_factor):
    r"""
    Applies the PixelShuffle operation over input `input` which implements sub-pixel convolutions
    with stride :math:`1/r` . For more details, refer to
    `Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural Network
    <https://arxiv.org/abs/1609.05158>`_ .

    Typically, the `input` is of shape :math:`(*, C \times r^2, H, W)` , and the output is of shape
    :math:`(*, C, H \times r, W \times r)`, where `r` is an upscale factor and `*` is zero or more batch dimensions.

    Args:
        input (Tensor): Tensor of shape :math:`(*, C \times r^2, H, W)` . The dimension of `input` is larger than 2,
            and the length of third to last dimension can be divisible by `upscale_factor` squared.
        upscale_factor (int): factor to shuffle the input Tensor, and is a positive integer.
            `upscale_factor` is the above-mentioned :math:`r`.

    Returns:
        - **output** (Tensor) - Tensor of shape :math:`(*, C, H \times r, W \times r)` .

    Raises:
        ValueError: If `upscale_factor` is not a positive integer.
        ValueError: If the length of third to last dimension is not divisible by `upscale_factor` squared.
        ValueError: If the dimension of `input` is less than 3.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import ops
        >>> input_x = np.arange(3 * 2 * 9 * 4 * 4).reshape((3, 2, 9, 4, 4))
        >>> input_x = mindspore.Tensor(input_x, mindspore.dtype.int32)
        >>> output = ops.pixel_shuffle(input_x, 3)
        >>> print(output.shape)
        (3, 2, 1, 12, 12)
    """
    _check_positive_int(upscale_factor, "upscale_factor")
    _check_is_tensor("input", input, "pixel_shuffle")
    _check_pixel_shuffle_unshuffle_input_shape(input, "pixel_shuffle")
    idx = shape_(input)
    length = input.ndim
    pre = idx[:-3]
    c, h, w = idx[-3:]
    _check_pxiel_shuffle_valid(c, upscale_factor)
    c = c // upscale_factor ** 2
    input_perm = pre + (c, upscale_factor, upscale_factor, h, w)
    input = reshape_(input, input_perm)
    input_perm = [i for i in range(length - 2)]
    input_perm = input_perm + [length, length - 2, length + 1, length - 1]
    input_perm = tuple(input_perm)
    input = transpose_(input, input_perm)
    input = reshape_(input, (pre + (c, upscale_factor * h, upscale_factor * w)))
    return input


@_primexpr
def _check_pxiel_unshuffle_valid(num1, num2, factor):
    if num1 % factor != 0 or num2 % factor != 0:
        raise ValueError("For 'pixel_unshuffle', the length of second to last 2 dimension should be divisible "
                         "by downscale_factor.")


def pixel_unshuffle(input, downscale_factor):
    r"""
    Applies the PixelUnshuffle operation over input `input` which is the inverse of PixelShuffle. For more details,
    refer to `Real-Time Single Image and Video Super-Resolution Using an Efficient Sub-Pixel Convolutional Neural
    Network <https://arxiv.org/abs/1609.05158>`_ .

    Typically, the input is of shape :math:`(*, C, H \times r, W \times r)` , and the output is of shape
    :math:`(*, C \times r^2, H, W)` , where `r` is a downscale factor and `*` is zero or more batch dimensions.

    Args:
        input (Tensor): Tensor of shape :math:`(*, C, H \times r, W \times r)` . The dimension of `input` is larger than
            2, and the length of second to last dimension or last dimension can be divisible by `downscale_factor` .
        downscale_factor (int): factor to unshuffle the input Tensor, and is a positive integer.
            `downscale_factor` is the above-mentioned :math:`r`.

    Returns:
        - **output** (Tensor) - Tensor of shape :math:`(*, C \times r^2, H, W)` .

    Raises:
        ValueError: If `downscale_factor` is not a positive integer.
        ValueError: If the length of second to last dimension or last dimension is not divisible by `downscale_factor` .
        ValueError: If the dimension of `input` is less than 3.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = np.arange(8 * 8).reshape((1, 1, 8, 8))
        >>> input_x = mindspore.Tensor(input_x, mindspore.dtype.int32)
        >>> output = ops.pixel_unshuffle(input_x, 2)
        >>> print(output.shape)
        (1, 4, 4, 4)
    """
    _check_positive_int(downscale_factor, "downscale_factor")
    _check_is_tensor("input", input, "pixel_unshuffle")
    _check_pixel_shuffle_unshuffle_input_shape(input, "pixel_unshuffle")
    idx = shape_(input)
    length = input.ndim
    pre = idx[:-3]
    c, h, w = idx[-3:]
    _check_pxiel_unshuffle_valid(h, w, downscale_factor)
    h = h // downscale_factor
    w = w // downscale_factor
    input_perm = pre + (c, h, downscale_factor, w, downscale_factor)
    input = reshape_(input, input_perm)
    input_perm = [i for i in range(length - 2)]
    input_perm = input_perm + [length - 1, length + 1, length - 2, length]
    input_perm = tuple(input_perm)
    input = transpose_(input, input_perm)
    input = reshape_(input, (pre + (c * downscale_factor * downscale_factor, h, w)))
    return input


def glu(x, axis=-1):
    r"""
    Computes GLU (Gated Linear Unit activation function) of input tensors.

    .. math::
        {GLU}(a, b)= a \otimes \sigma(b)

    where :math:`a` is the first half of the input matrices and :math:`b` is the second half.

    Here :math:`\sigma` is the sigmoid function, and :math:`\otimes` is the Hadamard product.
    See `Language Modeling with Gated Convluational Networks <https://arxiv.org/abs/1612.08083>`_.

    Args:
        x (Tensor): Tensor to be split. Its dtype is Number, and shape is :math:`(\ast_1, N, \ast_2)`
            where `*` means, any number of additional dimensions.
        axis (int, optional): the axis to split the input. It must be int. Default: ``-1`` , the last axis of `x`.

    Returns:
        Tensor, the same dtype as the `x`, with the shape :math:`(\ast_1, M, \ast_2)` where :math:`M=N/2`.

    Raises:
        TypeError: If dtype of `x` is not Number.
        TypeError: If `x` is not a Tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([[0.1,0.2,0.3,0.4],[0.5,0.6,0.7,0.8]])
        >>> output = ops.glu(input)
        >>> print(output)
        [[0.05744425 0.11973753]
         [0.33409387 0.41398472]]
    """
    spilt = _get_cache_prim(P.Split)(axis=axis, output_num=2)
    x, y = spilt(x)
    y = sigmoid_(y)
    return x * y


def glu_ext(input, dim=-1):
    r"""
    Computes GLU (Gated Linear Unit activation function) of the input tensor.

    .. math::
        {GLU}(a, b)= a \otimes \sigma(b)

    where :math:`a` is the first half of the `input` Tensor after `input` is split and :math:`b` is the second half.

    Here :math:`\sigma` is the sigmoid function, and :math:`\otimes` is the Hadamard product.
    See `Language Modeling with Gated Convluational Networks <https://arxiv.org/abs/1612.08083>`_.

    Args:
        input (Tensor): Tensor to be calculated. Dtype is floating point and the shape
            is :math:`(\ast_1, N, \ast_2)` where `*` means, any number of additional dimensions. :math:`N`
            is required to be an even number, where :math:`N` is the size of `input` on the dimension
            selected by `dim`.
        dim (int, optional): The dimension to split the input `input`. The value range is `[-r, r)` where `r`
            is the number of dimensions of `input`. Default: ``-1`` , the last dimension in `input`.

    Returns:
        Tensor, the same dtype as the input `input`. The shape is :math:`(\ast_1, M, \ast_2)` where :math:`M=N/2`.

    Raises:
        TypeError: If `input` is not a Tensor or `dim` is not an int.
        IndexError: If the value of `dim` is out of the range of `[-r, r)`, where `r` is the number
            of dimensions of `input`.
        RuntimeError: If dtype of `input` is not supported.
        RuntimeError: If the length of `input` in the dimension selected by `dim` is not even.

    Supported Platforms:
        ``Ascend`` ``CPU``

    Examples:
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]])
        >>> output = ops.function.nn_func.glu_ext(input)
        >>> print(output)
        [[0.05744425 0.11973753]
         [0.33409387 0.41398472]]
    """
    return _get_cache_prim(P.GLU)(axis=dim)(input)


def multi_margin_loss(input, target, p=1, margin=1, weight=None, reduction='mean'):
    r"""
    Hinge loss for optimizing a multi-class classification.

    Optimizes a multi-class classification hinge
    loss (margin-based loss) between input and
    output.

    For each mini-batch sample, the loss in terms of the 1D input :math:`x` and scalar output :math:`y` is:

    .. math::
        \text{loss}(x, y) = \frac{\sum_i \max(0, \text{margin} - x[y] + x[i])^p}{\text{x.size}(0)}

    where :math:`i\in \{0,⋯,x.size(0)-1\}` and :math:`i \ne y`.

    Args:
        input (Tensor): Input , with shape :math:`(N, C)`. Data type only support float32, float16 or float64.
            It is :math:`x` in the above formula.
        target (Tensor): Ground truth labels, with shape :math:`(N,)`. Data type only support int64. The
            value of target should be non-negative, less than C. It is :math:`y` in the above formula.
        p (int, optional): The norm degree for pairwise distance. Should be 1 or 2. Default: ``1`` .
        margin (int, optional): A parameter to change pairwise distance. Default: ``1`` .
        weight (Tensor, optional): The rescaling weight to each class with shape :math:`(C,)`. Data type only
            support float16, float32 or float64. Default: ``None`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        - **outputs** - Tensor. If `reduction` is ``'none'``, returns a Tensor with the same shape as `target`.
          Otherwise, it is a scalar.

    Raises:
        TypeError: If dtype of `p` or `target` is not int.
        TypeError: If dtype of `margin` is not int.
        TypeError: If dtype of `reduction` is not str.
        TypeError: If dtype of `input` is not float16, float or float64.
        TypeError: If dtype of `weight` and `input` is not the same.
        ValueError: If `p` is not 1 or 2.
        ValueError: If `reduction` is not one of {'none','sum','mean'}.
        ValueError: If shape[0] of `input` is not equal to shape[0] of `target`.
        ValueError: If shape[1] of `input` is not equal to shape[0] of `weight`.
        ValueError: If rank of `weight` is not 1 or rank of `target` is not 1 or `input` is not 2.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> inputs = Tensor(np.ones(shape=[3, 3]), mindspore.float32)
        >>> target = Tensor(np.array([1, 2, 1]), mindspore.int64)
        >>> weight = Tensor(np.array([1, 1, 1]), mindspore.float32)
        >>> output = ops.multi_margin_loss(inputs, target, weight=weight)
        >>> print(output)
        0.6666667
    """

    if not isinstance(margin, int):
        raise TypeError(f"For 'multi_margin_loss', the type of 'margin' must be int, but got {type(margin)}.")
    margin_ = float(margin)
    loss = _get_cache_prim(P.MultiMarginLoss)(p, margin_, reduction)
    outputs = loss(input, target, weight)
    return outputs


def multilabel_margin_loss(input, target, reduction='mean'):
    r"""
    Hinge loss for optimizing a multi-label classification.

    Creates a criterion that optimizes a multi-label multi-classification
    hinge loss (margin-based loss) between input :math:`x` (a 2D mini-batch `Tensor`)
    and output :math:`y` (which is a 2D `Tensor` of target class indices).
    For each sample in the mini-batch:

    .. math::
        \text{loss}(x, y) = \sum_{ij}\frac{\max(0, 1 - (x[y[j]] - x[i]))}{\text{x.size}(0)}

    where :math:`x \in \left\{0, \; \cdots , \; \text{x.size}(0) - 1\right\}`, \
    :math:`y \in \left\{0, \; \cdots , \; \text{y.size}(0) - 1\right\}`, \
    :math:`0 \leq y[j] \leq \text{x.size}(0)-1`, \
    and :math:`i \neq y[j]` for all :math:`i` and :math:`j`.
    :math:`y` and :math:`x` must have the same size.
    The criterion only considers a contiguous block of non-negative targets that
    starts at the front.
    This allows for different samples to have variable amounts of target classes.

    Args:
        input (Tensor): Predict data, :math:`x` in the formula above. Tensor of shape :math:`(C)`
            or :math:`(N, C)`, where :math:`N` is the batch size and :math:`C` is the number of classes.
            Data type must be float16 or float32.
        target (Tensor): Ground truth data, :math:`y` in the formula above, with the same shape as `input`,
            data type must be int32 and label targets padded by -1.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        - **outputs** (Union[Tensor, Scalar]) - The loss of MultilabelMarginLoss.
          If `reduction` is ``"none"``, its shape is :math:`(N)`.
          Otherwise, a scalar value will be returned.

    Raises:
        TypeError: If `input` or `target` is not a Tensor.
        TypeError: If dtype of `input` is neither float16 nor float32.
        TypeError: If dtype of `target` is not int32.
        ValueError: If length of shape of `input` is neither 1 nor 2.
        ValueError: If shape of `input` is not the same as `target`.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``.

    Supported Platforms:
        ``Ascend`` ``GPU``

    Examples:
       >>> import mindspore
       >>> import numpy as np
       >>> from mindspore import Tensor, ops
       >>> inputs = Tensor(np.array([[0.1, 0.2, 0.4, 0.8], [0.2, 0.3, 0.5, 0.7]]), mindspore.float32)
       >>> target = Tensor(np.array([[1, 2, 0, 3], [2, 3, -1, 1]]), mindspore.int32)
       >>> output = ops.multilabel_margin_loss(inputs, target)
       >>> print(output)
       0.325
    """

    loss = _get_cache_prim(P.MultilabelMarginLoss)(reduction)
    outputs, _ = loss(input, target)
    return outputs


def multilabel_soft_margin_loss(input, target, weight=None, reduction='mean'):
    r"""
    Calculates the MultiLabelSoftMarginLoss.
    The multi-label soft margin loss is a commonly used loss function in multi-label classification tasks
    where an input sample can belong to multiple classes.
    Given an input :math:`input` and binary labels :math:`output` of size :math:`(N,C)`,
    where :math:`N` denotes the number of samples
    and :math:`C` denotes the number of classes.

    .. math::
        \mathcal{loss\left( input , output \right)} = - \frac{1}{N}\frac{1}{C}\sum_{i = 1}^{N}
        \sum_{j = 1}^{C}\left(output_{ij}\log\frac{1}{1 + e^{- input_{ij}}} + \left( 1 - output_{ij}
        \right)\log\frac{e^{-input_{ij}}}{1 + e^{-input_{ij}}} \right)

    where :math:`input_{ij}` represents the predicted score of sample :math:`i` for class :math:`j`.
    :math:`output_{ij}` represents the binary label of sample :math:`i` for class :math:`j`, where
    sample :math:`i` belongs to class :math:`j` if :math:`output_{ij}=1` , and sample :math:`i` does
    not belong to class :math:`j` if :math:`output_{ij}=0`. For a multi-label classification task, each
    sample may have multiple labels with a value of 1 in the binary label :math:`output`. `weight` will
    multiply to the loss of each class if given.

    Args:
        input (Tensor): A tensor of shape :math:`(N, C)` , where N is batch size and C is number of classes.
        target (Tensor): The label target Tensor which has the same shape as `input`.
        weight (Union[Tensor, int, float], optional): The manual rescaling weight given to each class.
            Default: ``None``.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the weighted mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor, the data type is the same as input, if the `reduction` is ``'none'``,
        its shape is :math:`(N)` , otherwise it is zero.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([[0.3, 0.6, 0.6], [0.9, 0.4, 0.2]])
        >>> target = Tensor([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
        >>> loss = ops.multilabel_soft_margin_loss(input, target, reduction='mean')
        >>> print(loss.asnumpy())
        0.84693956
    """
    cls_name = "multilabel_soft_margin_loss"
    _check_is_tensor('input', input, cls_name)
    _check_is_tensor('target', target, cls_name)

    input_shape = input.shape
    if ops.is_sequence_value_unknown(input_shape):
        input_shape = tensor_shape_(input)

    pos = log_(add_(exp_(-input), 1))
    neg = log_(add_(exp_(input), 1))
    loss = mul_(target, pos) + mul_(1 - target, neg)
    if weight is not None:
        loss = mul_(loss, weight)
    class_dim = input.ndim - 1
    loss = loss.sum(axis=class_dim) / input_shape[class_dim]
    return _get_loss(loss, reduction, cls_name)


def gelu(input, approximate='none'):
    r"""
    Gaussian Error Linear Units activation function.

    GeLU is described in the paper `Gaussian Error Linear Units (GELUs) <https://arxiv.org/abs/1606.08415>`_.
    And also please refer to `BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding
    <https://arxiv.org/abs/1810.04805>`_.

    When `approximate` argument is `none`, GeLU is defined as follows:

    .. math::
        GELU(x_i) = x_i*P(X < x_i),

    where :math:`P` is the cumulative distribution function of the standard Gaussian distribution,
    :math:`x_i` is the input element.

    When `approximate` argument is `tanh`, GeLU is estimated with:

    .. math::
        GELU(x_i) = 0.5 * x_i * (1 + \tanh(\sqrt(2 / \pi) * (x_i + 0.044715 * x_i^3)))

    GELU Activation Function Graph:

    .. image:: ../images/GELU.png
        :align: center

    Args:
        input (Tensor): The input of the activation function GeLU, the data type is float16, float32 or float64.
        approximate (str, optional): the gelu approximation algorithm to use.
            Acceptable vaslues are ``'none'`` and ``'tanh'`` .
            Default: ``'none'`` .

    Returns:
        Tensor, with the same type and shape as `input`.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not bfloat16, float16, float32 or float64.
        ValueError: If `approximate` value is neither `none` nor `tanh`.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> x = Tensor([1.0, 2.0, 3.0], mindspore.float32)
        >>> result = ops.gelu(x, approximate='none')
        >>> print(result)
        [0.8413447 1.9544997 2.9959505]
    """
    if approximate not in ['none', 'tanh']:
        raise ValueError("For ops.gelu, approximate value should be either 'none' or 'tanh'.")

    x_dtype = dtype_(input)
    if x_dtype not in [mstype.float16, mstype.float32, mstype.float64, mstype.bfloat16]:
        raise TypeError(f"For gelu, the input dtype must be float16, float32 or float64, "
                        f"but got {x_dtype}.")
    if approximate == 'tanh':
        output = gelu_(input)
    else:
        output = sqrt_(Tensor(2.0, x_dtype))
        output = div_(input, output)
        output = erf_(output) + Tensor(1.0, x_dtype)
        output = input * output * Tensor(0.5, x_dtype)

    return output


def channel_shuffle(x, groups):
    r"""
    Divide the channels in a tensor of shape :math:`(*, C, H, W)` into :math:`g` groups and
    rearrange them as :math:`(*, \frac{C}{g}, g, H*W)`, while retaining the original tensor
    shape in the final output.

    Args:
        x (Tensor): The input tensor.
        groups (int): Number of groups to divide channels in.

    Returns:
        Tensor

    Supported Platforms:
        ``Ascend`` ``CPU``

    Examples:
        >>> import mindspore
        >>> x = mindspore.tensor(mindspore.ops.arange(0, 16, dtype=mindspore.int16).reshape(1, 4, 2, 2))
        >>> y = mindspore.ops.channel_shuffle(x, groups=2)
        >>> print(y)
        [[[[ 0  1]
           [ 2  3]]
           [[ 8  9]
           [10 11]]
           [[ 4  5]
           [ 6  7]]
           [[12 13]
           [14 15]]]]
    """
    channel_shuffle_func = ChannelShuffle(group=groups)
    y = channel_shuffle_func(x)
    return y


def lp_pool1d(x, norm_type, kernel_size, stride=None, ceil_mode=False):
    r"""
    Applying 1D LPPooling operation on an input Tensor can be regarded as forming a 1D input plane.

    Typically the input is of shape :math:`(N, C, L_{in})` or :math:`(C, L_{in})`, the output is of shape
    :math:`(N, C, L_{out})` or :math:`(C, L_{out})`.

    .. math::
        L_{out} = \left\lfloor\frac{L_{in} - \text{kernel_size}}{\text{stride}} + 1\right\rfloor

    The operation is as follows.

    .. math::
        f(X) = \sqrt[p]{\sum_{x \in X} x^{p}}

    Note:
        This interface currently does not support Atlas A2 training series products.

    Args:
        x (Tensor): Tensor of shape :math:`(N, C, L_{in})` or :math:`(C, L_{in})`.
        norm_type (Union[int, float]): Type of normalization, represents p in the formula, can not be 0,

            - if p = 1, the result obtained is the sum of elements in the pool nucleus(Proportional to average pooling).
            - if p = :math:`\infty`, the result is the result of maximum pooling.

        kernel_size (int): The size of kernel window.
        stride (int): The distance of kernel moving, an int number that represents
            the width of movement is stride. Default: ``None`` , which indicates the moving step is `kernel_size` .
        ceil_mode (bool): Whether to use ceil or floor to calculate output shape. Default: ``False`` .

    Returns:
        - **output** (Tensor) - LPPool1d result, with shape :math:`(N, C, L_{out})` or :math:`(C, L_{out})`,
          It has the same data type as `x`, where

          .. math::
              L_{out} = \left\lfloor\frac{L_{in} - \text{kernel_size}}{\text{stride}} + 1\right\rfloor

    Raises:
        TypeError: If `x` is not a Tensor.
        TypeError: If `kernel_size` or `stride` is not an int.
        TypeError: If `ceil_mode` is not a bool.
        TypeError: If `norm_type` is neither float nor int.
        ValueError: If `norm_type` is equal to 0.
        ValueError: If `kernel_size` or `stride` is less than 1.
        ValueError: If length of shape of `x` is not equal to 2 or 3.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> from mindspore import Tensor
        >>> import numpy as np
        >>> x = Tensor(np.arange(2 * 3 * 4).reshape((2, 3, 4)), dtype=ms.float32)
        >>> out = ops.lp_pool1d(x, norm_type=1, kernel_size=3, stride=1, ceil_mode=False)
        >>> print(out)
        [[[ 3.  6.]
          [15. 18.]
          [27. 30.]]
         [[39. 42.]
          [51. 54.]
          [63. 66.]]]
    """
    if isinstance(norm_type, (float, int)):
        norm_type = float(norm_type)
    else:
        raise TypeError(f"For lp_pool1d, the type of 'norm_type' must be float or int, but got {type(norm_type)}")
    if norm_type == 0:
        raise ValueError(f"For lp_pool1d, the value of 'norm_type' can not be 0.")
    sign = _get_cache_prim(ops.Sign)()
    squeeze = _get_cache_prim(ops.Squeeze)(0)
    expand_dims = _get_cache_prim(ops.ExpandDims)()
    _is_squeeze = False
    if len(x.shape) == 2:
        x = expand_dims(x, 0)
        _is_squeeze = True
    if stride is None:
        stride = kernel_size
    out = ops.avg_pool1d(x.pow(norm_type), kernel_size=kernel_size, stride=stride, padding=0, ceil_mode=ceil_mode)
    if _is_squeeze:
        out = squeeze(out)
    return ((sign(out) * ops.relu(ops.abs(out))) * kernel_size).pow(1.0 / norm_type)


def lp_pool2d(x, norm_type, kernel_size, stride=None, ceil_mode=False):
    r"""
    Applying 2D LPPooling operation on an input Tensor can be regarded as forming a 2D input plane.

    Typically the input is of shape :math:`(N, C, H_{in}, W_{in})`, the output is of shape
    :math:`(N, C, H_{in}, W_{in})`, with the same shape as input, the operation is as follows.

    .. math::
        f(X) = \sqrt[p]{\sum_{x \in X} x^{p}}

    Note:
        This interface currently does not support Atlas A2 training series products.

    Args:
        x (Tensor): Tensor of shape :math:`(N, C, H_{in}, W_{in})`.
        norm_type (Union[int, float]): Type of normalization, represents p in the formula, can not be 0,

            - if p = 1, the result obtained is the sum of elements in the pool nucleus(Proportional to average pooling).
            - if p = :math:`\infty`, the result is the result of maximum pooling.

        kernel_size (Union[int, tuple[int]]): The size of kernel window.
            The data type of kernel_size must be int and the value represents the height and width,
            or a tuple of two int numbers that represent height and width respectively.
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents
            the height and width of movement are both strides, or a tuple of two int numbers that
            represent height and width of movement respectively.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        ceil_mode (bool): Whether to use ceil or floor to calculate output shape. Default: ``False`` .

    Returns:
        - **output** (Tensor) - LPPool2d result, with shape :math:`(N, C, H_{in}, W_{in})`,
          It has the same data type as `x`, where

          .. math::
              H_{out} = \left\lfloor\frac{H_{in} - \text{kernel_size}[0]}{\text{stride}[0]} + 1\right\rfloor

          .. math::
              W_{out} = \left\lfloor\frac{W_{in} - \text{kernel_size}[1]}{\text{stride}[1]} + 1\right\rfloor

    Raises:
        TypeError: If `x` is not a Tensor.
        TypeError: If `kernel_size` or `stride` is neither int nor tuple.
        TypeError: If `ceil_mode` is not a bool.
        TypeError: If `norm_type` is neither float nor int.
        ValueError: If `norm_type` is equal to 0.
        ValueError: If `kernel_size` or `stride` is less than 1.
        ValueError: If `kernel_size` or `stride` is a tuple whose length is not equal to `2`.
        ValueError: If length of shape of `x` is not equal to 4.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> from mindspore import Tensor
        >>> import numpy as np
        >>> x = Tensor(np.arange(2 * 3 * 4 * 5).reshape((2, 3, 4, 5)), dtype=ms.float32)
        >>> out = ops.lp_pool2d(x, norm_type=1, kernel_size=3, stride=1, ceil_mode=False)
        >>> print(out)
        [[[[  54.   63.   72.]
           [  99.  108.  117.]]
          [[ 234.  243.  252.]
           [ 279.  288.  297.]]
          [[ 414.  423.  432.]
           [ 459.  468.  477.]]]
         [[[ 594.  603.  612.]
           [ 639.  648.  657.]]
          [[ 774.  783.  792.]
           [ 819.  828.  837.]]
          [[ 954.  963.  972.]
           [ 999. 1008. 1017.]]]]

    """
    if isinstance(norm_type, (float, int)):
        norm_type = float(norm_type)
    else:
        raise TypeError(f"For lp_pool2d, the type of 'norm_type' must be float or int, but got {type(norm_type)}")
    if norm_type == 0:
        raise ValueError(f"For lp_pool2d, the value of 'norm_type' can not be 0.")
    sign = _get_cache_prim(ops.Sign)()
    if not isinstance(kernel_size, tuple):
        kernel_size = (kernel_size, kernel_size)
    if stride is None:
        stride = kernel_size
    out = ops.avg_pool2d(x.pow(norm_type), kernel_size=kernel_size, stride=stride, padding=0, ceil_mode=ceil_mode)
    return ((sign(out) * ops.relu(ops.abs(out))) * (kernel_size[0] * kernel_size[1])).pow(1.0 / norm_type)


def relu(input, inplace=False):
    r"""
    Computes ReLU (Rectified Linear Unit activation function) of input tensors element-wise.

    It returns :math:`\max(input,\  0)` element-wise. Specially, the neurons with the negative output
    will be suppressed and the active neurons will stay the same.

    .. math::

        ReLU(input) = (input)^+ = \max(0, input)

    ReLU Activation Function Graph:

    .. image:: ../images/ReLU.png
        :align: center

    Args:
        input (Tensor): The input Tensor.
        inplace (bool, optional): Whether to use inplace mode, Defaults to ``False``.

    Returns:
        Tensor, with the same dtype and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is not Number type.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> output = ops.relu(input)
        >>> print(output)
        [[0. 4. 0.]
         [2. 0. 9.]]
    """
    if inplace:
        return inplace_relu_op(input)
    return relu_op(input)


def relu_(input):
    r"""
    ReLuComputes ReLU (Rectified Linear Unit activation function) inplace of input tensors element-wise.

    It returns :math:`\max(input,\  0)` element-wise. Specially, the neurons with the negative output
    will be suppressed and the active neurons will stay the same.

    .. math::

        ReLU(input) = (input)^+ = \max(0, input)

    ReLU Activation Function Graph:

    .. image:: ../images/ReLU.png
        :align: center

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        input (Tensor): The input Tensor.

    Returns:
        Tensor, with the same dtype and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is not Number type.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> ops.relu_(input)
        >>> print(input)
        [[0. 4. 0.]
         [2. 0. 9.]]
    """
    return inplace_relu_op(input)


def mse_loss(input, target, reduction='mean'):
    r"""
    Calculates the mean squared error between the predicted value and the label value.

    For detailed information, please refer to :class:`mindspore.nn.MSELoss`.

    Args:
        input (Tensor): Tensor of any dimension.
        target (Tensor): The input label. Tensor of any dimension, same shape as the `input` in common cases.
            However, it supports that the shape of `input` is different from the shape of `target`
            and they should be broadcasted to each other.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor, loss of type float, the shape is zero if `reduction` is ``'mean'`` or ``'sum'`` ,
        while the shape of output is the broadcasted shape if `reduction` is ``'none'`` .

    Raises:
        ValueError: If `reduction` is not one of ``'none'`` , ``'mean'`` or ``'sum'``.
        ValueError: If `input` and `target` have different shapes and cannot be broadcasted.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> logits = Tensor(np.array([1, 2, 3]), mindspore.float32)
        >>> labels = Tensor(np.array([[1, 1, 1], [1, 2, 2]]), mindspore.float32)
        >>> output = ops.mse_loss(logits, labels, reduction='none')
        >>> print(output)
        [[0. 1. 4.]
         [0. 0. 1.]]
    """
    if not isinstance(input, (Tensor, Tensor_)):
        raise TypeError("For ops.mse_loss, the `input` must be tensor")
    if not isinstance(target, (Tensor, Tensor_)):
        raise TypeError("For ops.mse_loss, the `target` must be tensor")
    if reduction not in ['mean', 'none', 'sum']:
        raise ValueError("For ops.mse_loss, `reduction` value should be either 'mean', 'none' or 'sum'.")

    x = square_(input - target)
    float_type = (mstype.float16, mstype.float32, mstype.float64)
    if x.dtype not in float_type:
        input_dtype = mstype.float32
    else:
        input_dtype = x.dtype
    x = cast_(x, mstype.float32)

    average_flag = True
    reduce_flag = True
    if reduction == 'sum':
        average_flag = False
    if reduction == 'none':
        reduce_flag = False

    if reduce_flag and average_flag:
        x = reduce_mean_(x, _get_axis(x))

    if reduce_flag and not average_flag:
        x = reduce_sum_(x, _get_axis(x))

    return cast_(x, input_dtype)


def msort(input):
    r"""
    Return a tensor obtained by sorting the input tensor in ascending order along its first dimension.

    `ops.msort(input)` is equivalent to `ops.sort(axis=0)(input)[0]`. See also :class:`mindspore.ops.Sort()` for more
    details.

    Args:
        input (Tensor): The input tensor to sort.

    Returns:
        Tensor

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> input = mindspore.tensor([[8, 2, 1],
        ...                           [5, 9, 3],
        ...                           [4, 6, 7]])
        >>> mindspore.ops.msort(input)
        Tensor(shape=[3, 3], dtype=Int64, value=
        [[4, 2, 1],
         [5, 6, 3],
         [8, 9, 7]])
        >>> # is equivalent to `ops.sort(axis=0)(input)[0]`
        >>> mindspore.ops.sort(input, axis=0)[0]
        Tensor(shape=[3, 3], dtype=Int64, value=
        [[4, 2, 1],
         [5, 6, 3],
         [8, 9, 7]])
    """
    return ops.Sort(axis=0)(input)[0]


def triplet_margin_loss(anchor, positive, negative, margin=1.0, p=2, eps=1e-06, swap=False, reduction='mean'):
    """
    TripletMarginLoss operation.
    See :class:`mindspore.nn.TripletMarginLoss` for details.

    Args:
        anchor (Tensor): A sample randomly selected from the training set. Data type must be BasicType.
        positive (Tensor): A sample belonging to the same category as `anchor`, with the same type and shape
            as `anchor`.
        negative (Tensor): A sample belonging to the different class from `anchor`, with the same type and shape
            as `anchor`.
        margin (float, optional): Make a margin between the positive pair and the negative pair. The shape of margin
            must be 0. Default: ``1.0`` .
        p (int, optional): The degree of norm for pairwise distance. Default: ``2`` .
        eps (float, optional): Add small value to avoid division by zero. Default: ``1e-06``.
        swap (bool, optional): The distance swap change the negative distance to the distance between positive
            sample and negative sample. Default: ``False`` .
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .

            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.

    Returns:
        Tensor. If `reduction` is ``"none"``, its shape is :math:`(N)`. Otherwise, a scalar value will be returned.

    Raises:
        TypeError: If `anchor` or `positive` or `negative` is not a Tensor.
        TypeError: If dtype of `anchor`, `positive` and `negative` is not the same.
        TypeError: If `margin` is not a float.
        TypeError: If `p` is not an int.
        TypeError: If `eps` is not a float.
        TypeError: If `swap` is not a bool.
        ValueError: If dimensions of input `anchor`, `positive` and `negative` are less than or equal to 1 at the
            same time.
        ValueError: If the dimension of input `anchor` or `positive` or `negative` is bigger than or equal to 8.
        ValueError: If shape of `anchor`, `positive` and `negative` cannot broadcast.
        ValueError: If `reduction` is not one of ``'none'``, ``'mean'``, ``'sum'``.

    Supported Platforms:
        ``GPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> anchor = Tensor(np.array([[0.3, 0.7], [0.5, 0.5]]), mindspore.float32)
        >>> positive = Tensor(np.array([[0.4, 0.6], [0.4, 0.6]]), mindspore.float32)
        >>> negative = Tensor(np.array([[0.2, 0.9], [0.3, 0.7]]), mindspore.float32)
        >>> output = ops.triplet_margin_loss(anchor, positive, negative)
        >>> print(output)
        0.8881968
    """
    if not isinstance(margin, Tensor):
        margin_tensor = Tensor(margin, mstype.float32)
    else:
        margin_tensor = margin
    triplet_margin_loss_op = _get_cache_prim(TripletMarginLoss)(p=p, eps=eps, swap=swap, reduction=reduction)
    return triplet_margin_loss_op(anchor, positive, negative, margin_tensor)


def linear(x, w, b):
    """inner linear"""
    out = ops.matmul(x, w.swapaxes(-1, -2))
    if b is not None:
        out = out + b
    return out


def _inner_dropout(x, p, training):
    """inner dropout"""
    _dropout = _get_cache_prim(P.Dropout)(1 - p)
    if 0. < p <= 1. and training:
        return _dropout(x)[0]
    return x


def _in_projection(q, k, v, w_q, w_k, w_v, b_q=None, b_k=None, b_v=None):
    """in projection function"""
    Eq, Ek, Ev = q.shape[-1], k.shape[-1], v.shape[-1]
    w_q_shape, w_k_shape, w_v_shape = w_q.shape, w_k.shape, w_v.shape

    if w_q_shape != (Eq, Eq):
        raise ValueError(f"Expecting query weights shape of {(Eq, Eq)}, but got {w_q_shape}")
    if w_k_shape != (Eq, Ek):
        raise ValueError(f"Expecting key weights shape of {(Eq, Ek)}, but got {w_k_shape}")
    if w_v_shape != (Eq, Ev):
        raise ValueError(f"Expecting value weights shape of {(Eq, Ev)}, but got {w_v_shape}")
    if b_q is not None:
        b_q_shape = b_q.shape
        if b_q_shape != (Eq,):
            raise ValueError(f"Expecting query bias shape of {(Eq,)}, but got {b_q_shape}")
    if b_k is not None:
        b_k_shape = b_k.shape
        if b_k_shape != (Eq,):
            raise ValueError(f"Expecting key bias shape of {(Eq,)}, but got {b_k_shape}")
    if b_v is not None:
        b_v_shape = b_v.shape
        if b_v_shape != (Eq,):
            raise ValueError(f"Expecting value bias shape of {(Eq,)}, but got {b_v_shape}")
    return linear(q, w_q, b_q), linear(k, w_k, b_k), linear(v, w_v, b_v)


def _in_projection_packed(q, k, v, w, b, k_is_v, q_is_k):
    """in projecktion packed function"""
    E = q.shape[-1]
    if k_is_v:
        if q_is_k:
            # self-attention
            return linear(q, w, b).tensor_split(3, axis=-1)
        # encoder-decoder attention
        w_q, w_kv = w.split([E, E * 2])
        if b is None:
            b_q = b_kv = None
        else:
            b_q, b_kv = b.split([E, E * 2])
        return (linear(q, w_q, b_q),) + linear(k, w_kv, b_kv).tensor_split(2, axis=-1)
    w_q, w_k, w_v = w.tensor_split(3)
    if b is None:
        b_q = b_k = b_v = None
    else:
        b_q, b_k, b_v = b.tensor_split(3)
    return linear(q, w_q, b_q), linear(k, w_k, b_k), linear(v, w_v, b_v)


def _scaled_dot_product_attention(query, key, value, attn_mask, dropout_p, is_causal, is_training, dtype):
    """scaled dot product attention"""
    embed_size = query.shape[-1]
    embed_size_tensor = scalar_to_tensor_(embed_size, dtype)
    scaling_factor = embed_size_tensor.sqrt().sqrt()
    query = query / scaling_factor

    if is_causal:
        L = query.shape[-2]
        S = key.shape[-2]
        attn_mask = ops.ones((L, S), mstype.bool_).tril()

    attn = ops.matmul(query, key.swapaxes(-2, -1) / scaling_factor)
    if attn_mask is not None:
        attn = attn + attn_mask
    attn = ops.softmax(attn, -1)
    attn = _inner_dropout(attn, dropout_p, is_training)
    output = ops.matmul(attn, value)

    return (output, attn)


@_primexpr
def _check_qkv_shape(query_ndim, key_ndim, value_ndim):
    """Check the expected shape for `query, `key`, `value` and returns whether the input is batched."""
    # Shape check.
    if query_ndim == 3:
        # Batched Inputs
        is_batched = True
        if key_ndim != 3 or value_ndim != 3:
            raise ValueError(f"For batched `query`, the `key` and `value` must be 3D tensor, "
                             f"but got `key` with {key_ndim}D and `value` with {value_ndim}D.")
    elif query_ndim == 2:
        # Unbatched Inputs
        is_batched = False
        if key_ndim != 2 or value_ndim != 2:
            raise ValueError(f"For unbatched `query`, the `key` and `value` must be 2D tensor, "
                             f"but got `key` with {key_ndim}D and `value` with {value_ndim}D.")
    else:
        raise ValueError(f"The `query` should be unbatched 2D or batched 3D tensor, "
                         f"but got `query` with {query_ndim}D.")

    return is_batched


@_primexpr
def _check_kpm_shape(query_ndim, kmp_ndim):
    """check key_padding_mask shape"""
    if query_ndim == 3:
        if kmp_ndim != 2:
            raise ValueError(f"For batched `query`, the `key_padding_mask` must be `None` or 2D, "
                             f"but got `key_padding_mask` with {kmp_ndim}D.")

    elif query_ndim == 2:
        if kmp_ndim != 1:
            raise ValueError(f"For unbatched `query`, the `key_padding_mask` must be `None` or 1D, "
                             f"but got `key_padding_mask` with {kmp_ndim}D.")


@_primexpr
def _check_attn_mask_shape(query_ndim, query_shape, key_shape, attn_mask_ndim,
                           attn_mask_shape, num_heads):
    """
    Check the expected shape for `attn_mask`.
    """
    # Shape check.
    if query_ndim == 3:
        if attn_mask_ndim not in (2, 3):
            raise ValueError(f"For batched `query`, the `attn_mask` must be `None`, 2-D or 3-D, "
                             f"but got `attn_mask` with{attn_mask_ndim}D.")
    elif query_ndim == 2:
        if attn_mask_ndim not in (2, 3):
            raise ValueError(f"For unbatched `query`, the `attn_mask` must be `None`, 2-D or 3-D, "
                             f"but got `attn_mask` with{attn_mask_ndim}D.")

        if attn_mask_ndim == 3:
            expected_shape = (num_heads, query_shape[0], key_shape[0])
            if attn_mask_shape != expected_shape:
                raise ValueError(f"The shape of `attn_mask` must to be {expected_shape}, "
                                 f"but got {attn_mask_shape}.")


def _inner_pad(x, padding, value=None):
    """inner pad function for bool type."""
    x_dtype = x.dtype
    if x_dtype == mstype.bool_:
        x = x.astype(mstype.int32)
    x = pad(x, padding, value=value)
    x = x.astype(x_dtype)
    return x


def multi_head_attention_forward(query, key, value, embed_dim_to_check, num_heads, in_proj_weight,
                                 in_proj_bias, bias_k, bias_v, add_zero_attn, dropout_p, out_proj_weight,
                                 out_proj_bias, training=True, key_padding_mask=None, attn_mask=None,
                                 use_separate_proj_weight=False, q_proj_weight=None, k_proj_weight=None,
                                 v_proj_weight=None, static_k=None, static_v=None, average_attn_weights=True,
                                 is_causal=False, k_is_v=False, q_is_k=False, dtype=mstype.float32):
    """multi head attetion forward function"""
    is_batched = _check_qkv_shape(query.ndim, key.ndim, value.ndim)
    if key_padding_mask is not None:
        _check_kpm_shape(query.ndim, key_padding_mask.ndim)
    if attn_mask is not None:
        _check_attn_mask_shape(query.ndim, query.shape, key.shape, attn_mask.ndim,
                               attn_mask.shape, num_heads)

    if not is_batched:
        query = query.expand_dims(1)
        key = key.expand_dims(1)
        value = value.expand_dims(1)
        if key_padding_mask is not None:
            key_padding_mask = key_padding_mask.expand_dims(0)

    tgt_len, bsz, embed_dim = query.shape
    src_len, _, _ = key.shape
    if key_padding_mask is not None:
        _kpm_dtype = key_padding_mask.dtype
        if _kpm_dtype != mstype.bool_ and not ops.is_floating_point(key_padding_mask):
            raise ValueError("The `key_padding_mask` only supports bool and floating dtypes.")
    if embed_dim != embed_dim_to_check:
        raise ValueError(f"The `embed_dim` should be {embed_dim_to_check}, but got {embed_dim}.")

    head_dim = embed_dim // num_heads
    if head_dim * num_heads != embed_dim:
        raise ValueError(f"The `embed_dim` {embed_dim} can not be divisible by `num_heads` {num_heads}.")
    if use_separate_proj_weight:
        # allow MHA to have different embedding dims when separate projection weights are used
        if key.shape[:2] != value.shape[:2]:
            raise ValueError(f"The sequence length and batch dims of `key`: {key.shape[:2]} do not match "
                             f"`value`: {value.shape[:2]}.")
    else:
        if key.shape != value.shape:
            raise ValueError(f"The shape of `key` {key.shape} does not match `value` {value.shape}.")

    # compute in-projection
    if not use_separate_proj_weight:
        if in_proj_weight is None:
            raise ValueError("`use_separate_proj_weight` is ``False`` but `in_proj_weight` got ``None``.")
        q, k, v = _in_projection_packed(query, key, value, in_proj_weight, in_proj_bias, k_is_v, q_is_k)
    else:
        if q_proj_weight is None:
            raise ValueError("`use_separate_proj_weight` is ``True`` but `q_proj_weight` got ``None``.")
        if k_proj_weight is None:
            raise ValueError("`use_separate_proj_weight` is ``True`` but `k_proj_weight` got ``None``.")
        if v_proj_weight is None:
            raise ValueError("`use_separate_proj_weight` is ``True`` but `v_proj_weight` got ``None``.")
        if in_proj_bias is None:
            b_q = b_k = b_v = None
        else:
            b_q, b_k, b_v = in_proj_bias.tensor_split(3)
        q, k, v = _in_projection(query, key, value, q_proj_weight, k_proj_weight, v_proj_weight, b_q, b_k, b_v)

    # prep attention mask
    if attn_mask is not None:
        if attn_mask.dtype == mstype.uint8:
            attn_mask = attn_mask.astype(mstype.bool_)
        else:
            if not ops.is_floating_point(attn_mask) and attn_mask.dtype != mstype.bool_:
                raise ValueError(f"`attn_mask` only support float, byte, and bool types, "
                                 f"but got not {attn_mask.dtype}.")
        # ensure attn_mask's ndim is 3
        if attn_mask.ndim == 2:
            correct_2d_size = (tgt_len, src_len)
            if attn_mask.shape != correct_2d_size:
                raise ValueError(f"The shape of the `attn_mask` should be {correct_2d_size}, "
                                 f"but got {attn_mask.shape}.")
            attn_mask = attn_mask.expand_dims(0)
        elif attn_mask.ndim == 3:
            correct_3d_size = (bsz * num_heads, tgt_len, src_len)
            if attn_mask.shape != correct_3d_size:
                raise ValueError(f"The shape of the `attn_mask` should be {correct_3d_size}, "
                                 f"but got {attn_mask.shape}.")
        else:
            raise ValueError(f"The ndim of `attn_mask` only support 2 or 3, "
                             f"but got {attn_mask.ndim}.")

    if bias_k is not None and bias_v is not None:
        if static_k is not None:
            raise ValueError("The bias_k cannot be added to static_k.")
        if static_v is not None:
            raise ValueError("The bias_v cannot be added to static_v.")
        k = ops.cat([k, bias_k.tile((1, bsz, 1))])
        v = ops.cat([v, bias_v.tile((1, bsz, 1))])
        if attn_mask is not None:
            attn_mask = _inner_pad(attn_mask, (0, 1))
        if key_padding_mask is not None:
            key_padding_mask = _inner_pad(key_padding_mask, (0, 1))
    else:
        if bias_k is not None or bias_v is not None:
            raise ValueError("The bias_k and bias_v should be ``None``"
                             "at the same time.")

    q = q.view((tgt_len, bsz * num_heads, head_dim)).swapaxes(0, 1)
    if static_k is None:
        k = k.view((k.shape[0], bsz * num_heads, head_dim)).swapaxes(0, 1)
    else:
        if static_k.shape[0] != bsz * num_heads:
            raise ValueError(f"The shape[0] of `static_k` should be {bsz * num_heads}, "
                             f"but got {static_k.shape[0]}")
        if static_k.shape[2] != head_dim:
            raise ValueError(f"The shape[2] of `static_k` should be {head_dim}, "
                             f"but got {static_k.shape[2]}")
        k = static_k
    if static_v is None:
        v = v.view((v.shape[0], bsz * num_heads, head_dim)).swapaxes(0, 1)
    else:
        if static_v.shape[0] != bsz * num_heads:
            raise ValueError(f"The shape[0] of `static_v` should be {bsz * num_heads}, "
                             f"but got {static_v.shape[0]}")
        if static_v.shape[2] != head_dim:
            raise ValueError(f"The shape[2] of `static_v` should be {head_dim}, "
                             f"but got {static_v.shape[2]}")
        v = static_v

    if add_zero_attn:
        zero_attn_shape = (bsz * num_heads, 1, head_dim)
        k = ops.cat([k, ops.zeros(zero_attn_shape, dtype=k.dtype)], axis=1)
        v = ops.cat([v, ops.zeros(zero_attn_shape, dtype=v.dtype)], axis=1)
        if attn_mask is not None:
            attn_mask = _inner_pad(attn_mask, (0, 1))
        if key_padding_mask is not None:
            key_padding_mask = _inner_pad(key_padding_mask, (0, 1))

    src_len = k.shape[1]

    if key_padding_mask is not None:
        if key_padding_mask.shape != (bsz, src_len):
            raise ValueError(f"The shape of `key_padding_mask` should be {(bsz, src_len)}, "
                             f"but got {key_padding_mask.shape}.")

        key_padding_mask = key_padding_mask.view((bsz, 1, 1, src_len)). \
            tile((1, num_heads, 1, 1)).reshape(bsz * num_heads, 1, src_len)
        if attn_mask is None:
            attn_mask = key_padding_mask
        elif attn_mask.dtype == mstype.bool_:
            attn_mask = attn_mask.logical_or(key_padding_mask)
        else:
            attn_mask = attn_mask + key_padding_mask

    if attn_mask is not None and attn_mask.dtype == mstype.bool_:
        new_attn_mask = ops.zeros_like(attn_mask, dtype=q.dtype)
        attn_mask = new_attn_mask.masked_fill(attn_mask, ops.cast(float("-inf"), new_attn_mask.dtype))

    if attn_mask is not None:
        if attn_mask.shape[0] == 1:
            attn_mask = attn_mask.expand_dims(0)
        else:
            attn_mask = attn_mask.view((bsz, num_heads, -1, src_len))

    q = q.view((bsz, num_heads, tgt_len, head_dim))
    k = k.view((bsz, num_heads, src_len, head_dim))
    v = v.view((bsz, num_heads, src_len, head_dim))

    attn_output, attn_output_weights = _scaled_dot_product_attention(
        q, k, v, attn_mask, dropout_p, is_causal, training, dtype)
    attn_output = attn_output.transpose(2, 0, 1, 3).view((bsz * tgt_len, embed_dim))

    attn_output = linear(attn_output, out_proj_weight, out_proj_bias)
    attn_output = attn_output.view((tgt_len, bsz, attn_output.shape[1]))

    attn_output_weights = attn_output_weights.view((bsz, num_heads, tgt_len, src_len))
    if average_attn_weights:
        attn_output_weights = attn_output_weights.sum(axis=1) / num_heads

    if not is_batched:
        attn_output = attn_output.squeeze(1)
        attn_output_weights = attn_output_weights.squeeze(0)
    return attn_output, attn_output_weights


def max_pool2d(x, kernel_size, stride=None, padding=0, dilation=1, return_indices=False, ceil_mode=False):
    r"""
    Performs a 2D max pooling on the input Tensor.

    Typically, the input is a Tensor with shape :math:`(N_{in}, C_{in}, H_{in}, W_{in})`, outputs
    regional maximum in the :math:`(H_{in}, W_{in})`-dimension. Given `kernel_size`
    :math:`ks = (h_{ker}, w_{ker})` and `stride` :math:`s = (s_0, s_1)`, the operation is as follows:

    .. math::
        \text{output}(N_i, C_j, h, w) =
        \max_{m=0, \ldots, h_{ker}-1} \max_{n=0, \ldots, w_{ker}-1}
        \text{input}(N_i, C_j, s_0 \times h + m, s_1 \times w + n)

    Args:
        x (Tensor): Tensor of shape :math:`(N_{in}, C_{in}, H_{in}, W_{in})` with data type of int8,
            int16, int32, int64, uint8, uint16, uint32, uint64, float16, float32 or float64 in CPU or GPU
            while that of uint16 in Ascend.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value and arg
            value, is an int number that represents height and width of the kernel, or a tuple of
            two int numbers that represent height and width respectively.
        stride (Union[int, tuple[int]]): The distance of kernel moving, an int number that represents
            the height and width of movement are both stride, or a tuple of two int numbers that
            represent height and width of movement respectively.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]]): An int number that represents the height and width of movement are both
            strides, or a tuple of two int numbers that represent height and width of movement respectively.
            Default: ``0`` .
        dilation (Union[int, tuple[int]]): Control the stride of elements in the kernel. Default: ``1`` .
        return_indices (bool): Whether to output the indices of max value. Default: ``False`` .
        ceil_mode (bool): Whether to use ceil instead of floor to calculate output shape. Default: ``False`` .

    Returns:
        If `return_indices` is ``False`` , return a Tensor `output`, else return a tuple (`output`, `argmax`).

        - **output** (Tensor) - Maxpooling result, with shape :math:`(N_{out}, C_{out}, H_{out}, W_{out})`.
          It has the same data type as `x`.

        .. math::
            H_{out} = \left\lfloor\frac{H_{in} + 2 * \text{padding[0]} - \text{dilation[0]}
                \times (\text{kernel_size[0]} - 1) - 1}{\text{stride[0]}} + 1\right\rfloor

        .. math::
            W_{out} = \left\lfloor\frac{W_{in} + 2 * \text{padding[1]} - \text{dilation[1]}
                \times (\text{kernel_size[1]} - 1) - 1}{\text{stride[1]}} + 1\right\rfloor

        - **argmax** (Tensor) - Index corresponding to the maximum value. In CPU and GPU, data type is int64
          while that is uint16 in Ascend. It will be return only when `return_indices` is True.

    Raises:
        TypeError: If `x` is not a Tensor.
        ValueError: If length of shape of `x` is not equal to 4.
        TypeError: If `kernel_size` , `stride` , `padding` or `dilation` is not int or tuple.
        ValueError: If `kernel_size`, `stride` or `dilation` is less than 1.
        ValueError: If `padding` is less than 0.
        ValueError: If `padding` is more than half of `kernel_size`.
        TypeError: If `ceil_mode` is not bool.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.arange(20 * 16 * 50 * 32).reshape((20, 16, 50, 32)), mindspore.float32)
        >>> output_tensor, argmax = ops.max_pool2d(x, kernel_size=(3, 2), stride=(2, 1), return_indices=True)
        >>> print(output_tensor.shape)
        (20, 16, 24, 31)
        >>> print(argmax.shape)
        (20, 16, 24, 31)
    """
    strides = stride if (stride is not None) else kernel_size
    max_pool_with_argmax_v2_ = _get_cache_prim(NN_OPS.MaxPoolWithArgmaxV2)(
        kernel_size, strides, padding, dilation, ceil_mode)
    out, indices = max_pool_with_argmax_v2_(x)
    if return_indices:
        return out, indices
    return out


def max_pool2d_ext(input, kernel_size, stride=None, padding=0, dilation=1, ceil_mode=False, return_indices=False):
    r"""
    Performs a 2D max pooling on the input Tensor.

    Typically, the input is a Tensor with shape :math:`(N_{in}, C_{in}, H_{in}, W_{in})`, outputs
    regional maximum in the :math:`(H_{in}, W_{in})`-dimension. Given `kernel_size`
    :math:`ks = (h_{ker}, w_{ker})` and `stride` :math:`s = (s_0, s_1)`, the operation is as follows:

    .. math::
        \text{output}(N_i, C_j, h, w) =
        \max_{m=0, \ldots, h_{ker}-1} \max_{n=0, \ldots, w_{ker}-1}
        \text{input}(N_i, C_j, s_0 \times h + m, s_1 \times w + n)

    .. warning::
        Only support on Atlas A2 training series.

    Args:
        input (Tensor): Tensor of shape :math:`(N_{in}, C_{in}, H_{in}, W_{in})` with data type of float32
            in Ascend.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value and arg
            value, is an int number that represents height and width of the kernel, or a tuple of
            two int numbers that represent height and width respectively.
        stride (Union[int, tuple[int], None], optional): The distance of kernel moving, an int number that represents
            the height and width of movement are both stride, or a tuple of two int numbers that
            represent height and width of movement respectively.
            Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]], optional):
            An int number that represents the height and width of movement are both
            strides, or a tuple of two int numbers that represent height and width of movement respectively.
            Default: ``0`` .
        dilation (Union[int, tuple[int]], optional): Control the stride of elements in the kernel. Default: ``1`` .
        ceil_mode (bool, optional): Whether to use ceil instead of floor to calculate output shape. Default: ``False`` .
        return_indices (bool, optional): Whether to output the indices of max value. Default: ``False`` .

    Returns:
        If `return_indices` is ``False`` , return a Tensor `output`, else return a tuple (`output`, `argmax`).

        - **output** (Tensor) - Maxpooling result,
          with shape :math:`(N_{out}, C_{out}, H_{out}, W_{out})`.
          It has the same data type as `input`.

        .. math::
            H_{out} = \left\lfloor\frac{H_{in} + 2 * \text{padding[0]} - \text{dilation[0]}
                \times (\text{kernel_size[0]} - 1) - 1}{\text{stride[0]}} + 1\right\rfloor

        .. math::
            W_{out} = \left\lfloor\frac{W_{in} + 2 * \text{padding[1]} - \text{dilation[1]}
                \times (\text{kernel_size[1]} - 1) - 1}{\text{stride[1]}} + 1\right\rfloor

        - **argmax** (Tensor) - Index corresponding to the maximum value. In Ascend, data type is int32.
          It will be return only when `return_indices` is True.

    Raises:
        TypeError: If `input` is not a Tensor.
        ValueError: If length of shape of `input` is not equal to 4.
        TypeError: If `kernel_size` , `stride` , `padding` or `dilation` is not int or tuple.
        ValueError: If `kernel_size`, `stride` or `dilation` is less than 1.
        ValueError: If `dilation` is not all 1.
        ValueError: If `padding` is less than 0.
        ValueError: If `padding` is more than half of `kernel_size`.
        TypeError: If `ceil_mode` is not bool.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.arange(20 * 16 * 50 * 32).reshape((20, 16, 50, 32)), mindspore.float32)
        >>> output_tensor, argmax = ops.function.nn_func.max_pool2d_ext(input, kernel_size=(3, 2), stride=(2, 1),
        ...                                                             ceil_mode=False, return_indices=True)
        >>> print(output_tensor.shape)
        (20, 16, 24, 31)
        >>> print(argmax.shape)
        (20, 16, 24, 31)
    """
    out, indices = func_max_pool2d_op(input, kernel_size, stride, padding, dilation, ceil_mode, return_indices)
    if return_indices:
        return out, indices
    return out


def prompt_flash_attention(query, key, value, attn_mask=None, actual_seq_lengths=None, actual_seq_lengths_kv=None,
                           pse_shift=None, deq_scale1=None, quant_scale1=None, deq_scale2=None, quant_scale2=None,
                           quant_offset2=None, num_heads=1, scale_value=1.0, pre_tokens=2147483647, next_tokens=0,
                           input_layout='BSH', num_key_value_heads=0, sparse_mode=0, inner_precise=1):
    r"""
    The interface for fully inference.

    - B: Batch size
    - N: Num of attention heads
    - S: Sequence length
    - D: Head dim
    - H: Hidden layer size

    Self attention constructs an attention model based on the relationship between input samples themselves. The
    principle is to assume that there is an input sample sequence :math:`x` of length :math:`n`, and each
    element of :math:`x` is a :math:`d` dimensional vector, which can be viewed as a token embedding. This sequence
    can be transformed through 3 weight matrices to obtain 3 matrices with dimensions of :math:`n\times d`.

    The self attention calculation formula is defined as:

    .. math::
        Attention(Q,K,V)=Softmax(\frac{QK^{T} }{\sqrt{d} } )V

    where the product of :math:`Q` and :math:`K^{T}` represents the attention of input :math:`x`. To avoid the value
    becoming too large, it is usually scaled by dividing it by the square root of :math:`d` and perform softmax
    normalization on each row, yields a matrix of :math:`n\times d` after multiplying :math:`V`.

    .. warning::
        - Support dtype of float16 for `attn_mask` will be deprecated in the future.
        - When `sparse_mode` is 2, 3 or 4, the shape of `attn_mask` must be :math:`(2048, 2048)` /
          :math:`(B, 1, 2048, 2048)` / :math:`(1, 1, 2048, 2048)`.

    Note:
        - Maximum Support for each axis

          - Supports B-axis values less than or equal to 65536 (64k).
            When the input type includes int8 with D-axis not aligned to 32, or the input type is
            float16 or bfloat16 with D-axis not aligned to 16, the B-axis supports up to 128 only.
          - Supports N-axis values less than or equal to 256.
          - Supports S-axis values less than or equal to 20971520 (20M).
          - Supports D-axis values less than or equal to 512.

        - Quantization

          - int8 Input, int8 Output: Parameters `deq_scale1`, `quant_scale1`, `deq_scale2`, and `quant_scale2`
            must all be provided. `quant_offset2` is optional (default is 0 if not provided).
          - int8 Input, float16 Output: Parameters `deq_scale1`, `quant_scale1`, and `deq_scale2` must all be provided.
            If `quant_offset2` or `quant_scale2` is provided (i.e., not null), it will result in an error.
          - float16 or bfloat16 Input, int8 Output: Parameter `quant_scale2` must be provided. `quant_offset2` is
            optional (default is 0 if not provided). If `deq_scale1`, `quant_scale1`, or `deq_scale2` is
            provided (i.e., not null), it will result in an error.
          - int8 Output:

            - `quant_scale2` and `quant_offset2` in per-channel format do not support scenarios with
              left padding, Ring Attention, or non-32-byte aligned D-axis.
            - In GE mode: `quant_scale2` and `quant_offset2` in per-tensor format do not support scenarios
              with non-32-byte aligned D-axis.
            - Does not support sparse as band and `pre_tokens`/`next_tokens` being negative.

          - `quant_scale2` and `quant_offset2` can be bfloat16 only when `query` is bfloat16.


        - Other Usage Caveats:

          - :math:`N` of parameter `query` must be equal to `num_heads`. :math:`N` of parameter `key` and parameter
            `value` must be equal to `num_key_value_heads`.
          - `num_heads` must be divisible by `num_key_value_heads` and `num_heads` divided by `num_key_value_heads`
            can not be greater than 64.
          - When `query` dtype is bfloat16, D axis should align with 16.
          - Each element of `actual_seq_lengths` must not exceed q_S and element
            of `actual_seq_lengths_kv` must not exceed kv_S.

    .. warning::
        Only support on Atlas A2 training series.

    Args:
        query (Tensor): The query tensor with data type of int8, float16 or bfloat16.
            The shape is :math:`(B, q_S, q_H)` / `(B, q_N, q_S, q_D)`.
        key (Tensor): The key tensor with the same dtype as `query`.
            The shape is :math:`(B, kv_S, kv_H)` / `(B, kv_N, kv_S, kv_D)`.
        value (Tensor): The value tensor with the same dtype as `query`.
            The shape is :math:`(B, kv_S, kv_H)` / `(B, kv_N, kv_S, kv_D)`.
        attn_mask (Tensor, optional) - The attention mask tensor with data type of bool, int8, uint8 or float16.
            For each element, 0/False indicates retention and 1/True indicates discard.
            If `sparse_mode` is 0 or 1: the shape is :math:`(q_S, kv_S)` / :math:`(B, q_S, kv_S)` /
            :math:`(1, q_S, kv_S)` / :math:`(B, 1, q_S, kv_S)` / :math:`(1, 1, q_S, kv_S)`.
            If `sparse_mode` is 2, 3 or 4, the shape is :math:`(2048, 2048)` / :math:`(1, 2048, 2048)` /
            :math:`(1, 1, 2048, 2048)`.
            Default: ``None``.
        actual_seq_lengths (Union[Tensor, tuple[int], list[int]], optional): Describe actual sequence length of each
            batch of `query` with data type of int64. The shape is :math:`(B, )` and every element should be
            positive integer.
            Default: ``None``.
        actual_seq_lengths_kv (Union[Tensor, tuple[int], list[int]], optional): Describe actual sequence length of each
            batch of `key` or `value` with data type of int64. The shape is :math:`(B, )` and every element should be
            positive integer.
            Default: ``None``.
        pse_shift (Tensor, optional): The position encoding tensor with data type of float16 or bfloat16.
            Input tensor of shape :math:`(B, N, q_S, kv_S)` / :math:`(1, N, q_S, kv_S)`.
            Default: ``None``.

            - q_S must be greater than or equal to the query's S length, and kv_S must be greater than or
              equal to the key's S length.'
            - If `pse_shift` has dtype float16, `query` should have dtype float16 or int8, in which case high
              precision mode is enabled automatically.
            - If `pse_shift` has dtype bfloat16, `query` should have dtype bfloat16.

        deq_scale1 (Tensor, optional): Quantitative parametor, the tensor with data type of uint64 or float32.
            Input Tensor of shape :math:`(1,)`.
            Default: ``None``.
        quant_scale1 (Tensor, optional): Quantitative parametor, the tensor with data type of float32.
            Input Tensor of shape :math:`(1,)`.
            Default: ``None``.
        deq_scale2 (Tensor, optional): Quantitative parametor, input Tensor of shape :math:`(1,)` and it has
            the same dtype as `deq_scale1`.
            Default: ``None``.
        quant_scale2 (Tensor, optional): Quantitative parametor, the tensor with data type of float32 or bfloat16.
            The suggested shape is :math:`(1,)` / :math:`(1, 1, q_H)` / :math:`(q_H, )` when output layout is BSH,
            :math:`(1,)` / :math:`(1, q_N, 1, D)` / :math:`(q_N, D) when layout is BNSD.
            Default: ``None``.
        quant_offset2 (Tensor, optional): Quantitative parametor, the tensor with data type of float32 or bfloat16.
            It has the same dtype and shape as `quant_scale2`.
            Default: ``None``.
        num_heads (int, optional): The number of heads. It is an integer in range [0, 256].
            Default: ``1``.
        scale_value (double, optional): The scale value indicating the scale coefficient, which is used as the scalar of
            Muls in the calculation.
            Default: ``1.0``.
        pre_tokens (int, optional): For sparse cumputing, indicating the number of previous tokens Attention needs to
            associated with.
            Default: ``2147483647``.
        next_tokens (int, optional): For sparse cumputing, indicating the number of next tokens Attention needs to
            associated with.
            Default: ``0``.
        input_layout (str, optional): the data layout of the input qkv, support `(BSH)` and `(BNSD)`.
            Default ``BSH``.
        num_key_value_heads (int, optional): An int indicates head numbers of ``key``/``value`` which are used
            in GQA algorithm. The value 0 indicates if the key and value have the same head nums, use `num_heads`.
            It it is specified(not 0), it must be a factor of `num_heads` and it must be equal to kv_n.
            Default: ``0``.
        sparse_mode (int, optional): An int specifies sparse mode, can be int from {0, 1, 2, 3, 4}.
            Default: ``0``.

            - sparseMode = 0: If `attn_mask` is a null pointer, `pre_tokens` and `next_tokens` inputs are ignored
              (internally set to INT_MAX).
            - sparseMode = 2, 3, 4: `attn_mask` shape must be :math:`(S, S)` or :math:`(1, S, S)` or
              :math:`(1, 1, S, S)`, with S fixed at 2048. User must ensure that `attn_mask` is lower triangular.
              If not provided or incorrect shape, it will result in an error.
            - sparseMode = 1, 2, 3: Ignores `pre_tokens`, `next_tokens` inputs and sets values according
              to specific rules.
            - sparseMode = 4: `pre_tokens` and `next_tokens` must be non-negative.

        inner_precise (int, optional): An int number from {0, 1} indicates computing mode.
            ``0`` for high precision mode for float16 dtype. ``1`` for high performance mode.
            Default: ``1``.

    Returns:
        attention_out (Tensor) - Output tensor, has the same shape as `query` of
        :math:`(B, q_S, q_H)` / :math:`(B, q_N, q_S, q_D)`.
        Output dtype is determined by multiple factors, please refer to Note above for details.

    Raises:
        TypeError: Dtype of `query` is not int8, float16 or bfloat16.
        TypeError: `query`, `key` and `value` don't have the same dtype.
        TypeError: Dtype of `attn_mask` is not bool, int8 or uint8.
        TypeError: Dtype of `pse_shift` is not bfloat16 or float16.
        TypeError: `scale_value` is not a double number.
        TypeError: `input_layout` is not a string.
        TypeError: `num_key_value_heads` is not an int.
        TypeError: `sparse_mode` is not an int.
        TypeError: `sparse_inner_precisemode` is not an int.
        TypeError: `quant_scale1` is not Tensor of type float32.
        TypeError: `deq_scale1` is not Tensor of type uint64 or float32.
        TypeError: `quant_scale2` is not Tensor of type float32.
        TypeError: `deq_scale2` is not Tensor of type uint64 or float32.
        TypeError: `quant_offset2` is not Tensor of type float32.
        ValueError: `input_layout` is a string but of `(BSH)` or `(BNSD)`.
        RuntimeError: `num_heads` is not divisible by `num_key_value_heads`.
        RuntimeError: `num_heads` is not greater than 0.
        RuntimeError: `num_key_value_heads` is not greater than or equal to 0.
        RuntimeError: kv_n is not equal to `num_key_value_heads`.
        RuntimeError: `attn_mask` shape is not valid.
        RuntimeError: `sparse_mode` is specified but is not 0, 1, 2, 3 or 4.
        RuntimeError: `query` dtype is bfloat16 and D axis is not aligned with 16.
        RuntimeError: `input_layout` is BSH and kv_h is not divisible by `num_key_value_heads`.
        RuntimeError: D-axis of `query`, `key` and `value` is not the same.
        RuntimeError: In post quant per-channel scenario, D-axis is not 32 Byte aligned.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> from mindspore import Tensor, ops
        >>> import numpy as np
        >>> B = 1
        >>> N = 16
        >>> S = 256
        >>> D = 16
        >>> query = Tensor(np.ones((B, N, S, D), dtype=np.float16))
        >>> key = Tensor(np.ones((B, N, S, D), dtype=np.float16))
        >>> value = Tensor(np.ones((B, N, S, D), dtype=np.float16))
        >>> out = ops.prompt_flash_attention(query, key, value, None, None, None, None, None, None, None, None,
        ...                                  None, N, input_layout='BNSD')
        >>> print(out.shape)
        (1, 16, 256, 16)
    """

    pfa = _get_cache_prim(PromptFlashAttention)(num_heads, scale_value, pre_tokens, next_tokens, input_layout,
                                                num_key_value_heads, sparse_mode, inner_precise)
    return pfa(query, key, value, attn_mask, actual_seq_lengths, actual_seq_lengths_kv, pse_shift, deq_scale1,
               quant_scale1, deq_scale2, quant_scale2, quant_offset2)


def incre_flash_attention(query, key, value, attn_mask=None, actual_seq_lengths=None, pse_shift=None,
                          dequant_scale1=None, quant_scale1=None, dequant_scale2=None, quant_scale2=None,
                          quant_offset2=None, antiquant_scale=None, antiquant_offset=None, block_table=None,
                          num_heads=1, input_layout='BSH', scale_value=1.0, num_key_value_heads=0,
                          block_size=0, inner_precise=1, kv_padding_size=None):
    r"""
    The interface for incremental inference.

    - B: Batch size
    - N: Num of attention heads
    - kvN: Num of `key` / `value` heads
    - S: Sequence length
    - D: Head dim
    - H: Hidden layer size
    - kvH: Hidden size of `key` / `value`

    where :math:`H=N\times D`, :math:`kvH=kvN\times D`.

    Self attention constructs an attention model based on the relationship between input samples themselves. The
    principle is to assume that there is a length of the input sample sequence :math:`x` of :math:`n`, and each
    element of :math:`x` is a :math:`d` dimensional vector, which can be viewed as a token embedding. This sequence
    can be transformed through 3 weight matrices to obtain 3 matrices with dimensions of :math:`n\times d`. The self
    attention calculation formula is defined as:

    .. math::
        Attention(Q,K,V)=Softmax(\frac{QK^{T} }{\sqrt{d} } )V

    where the product of :math:`Q` and :math:`K^{T}` represents the attention of input :math:`x`. To avoid the value
    becoming too large, it is usually scaled by dividing it by the square root of :math:`d` and perform softmax
    normalization on each row, yields a matrix of :math:`n\times d` after multiplying :math:`V`.

    Note:
      - If there is no input parameter and no default value, ``None`` needs to be passed.
      - The shape of the tensor corresponding to the `key` and `value` parameters needs to be completely consistent.
      - :math:`N` of parameter `query` is equal with `num_heads`. :math:`N` of parameter `key` and parameter `value`
        is equal with `num_key_value_heads`. `num_heads` is a multiple of `num_key_value_heads`.
      - Quantization

        - When the data type of `query`, `key`, and `value` is float16 and the data type of output is int8, the input
          parameter `quant_scale2` is required and `quant_offset2` is optional.
        - When `antiquant_scale` exists, `key` and `value` need to be passed by int8. `antiquant_offset` is optional.
        - The data type of `antiquant_scale` and `antiquant_offset` should be consistenct with that of `query`.
      - `pse_shift`

        - The `pse_shift` data type needs to be consistent with `query`, and only supports D-axis alignment,
          which means that the D-axis can be divided by 16.
      - Page attention:

        - The necessary condition for enabling page attention is that the `block_table` exists, and the `key`
          and `value` are arranged in a contiguous memory according to the index in the `block_table`. The support
          dtype for `key` and `value` is float16/bfloat16/int8.
        - In the enabling scenario of page attention, 16 alignment is required when input types of `key`
          and `value` are float16/bfloat16, and 32 alignment is required when input dtype of `key` and `value`
          is int8. It is recommended to use 128.
        - The maximum max_block_num_per_seq currently supported by blocktable is 16k, and exceeding 16k will result
          in interception and error messages; If you encounter :math:`S` being too large and causing
          max_block_num_per_seq to exceed 16k, you can increase the `block_size` to solve the problem.
        - The multiplication of all dimensions of the shape of the parameters `key` and `value` in the page attention
          scenario cannot exceed the representation range of int32.
        - When performing per-channel post quantization, page attention cannot be enabled simultaneously.
      - `kv_padding_size`:

        - The calculation formula for the starting point of KV cache transfer is
          :math:`S-kv\_padding\_size-actual\_seq\_lengths`. The calculation formula for the transfer endpoint of KV
          cache is :math:`S-kv\_padding\_size`. When the starting or ending point of the KV cache transfer is less
          than 0, the returned data result is all 0.
        - When `kv_padding_size` is less than 0, it will be set to 0.
        - `kv_padding_size` needs to be enabled together with the `actual_seq_lengths` parameter, otherwise it is
          considered as the KV right padding scene.
        - It needs to be enabled together with the atten_mask parameter and ensure that the meaning of atten_mask is
          correct, that is, it can correctly hide invalid data. Otherwise, it will introduce accuracy issues.
        - `kv_padding_size` does not support page attention scenarios.

    .. warning::
        Only support on Atlas A2 training series.

    Args:
        query (Tensor): The query tensor with data type of float16 or bfloat16.
            The shape is :math:`(B, 1, H)` / :math:`(B, N, 1, D)`.
        key (Union[tuple, list]): The key tensor with data type of float16 or bfloat16 or int8.
            The shape is :math:`(B, S, kvH)` / :math:`(B, kvN, S, D)`.
        value (Union[tuple, list]): The value tensor with data type of float16 or bfloat16 or int8.
            The shape is :math:`(B, S, kvH)` / :math:`(B, kvN, S, D)`.
        attn_mask (Tensor, optional): The attention mask tensor with data type of bool or int8 or uint8.
            The shape is :math:`(B, S)` / :math:`(B, 1, S)` / :math:`(B, 1, 1, S)`. Default: ``None``.
        actual_seq_lengths (Union[Tensor, tuple[int], list[int]], optional): Describe actual sequence length of each
            input with data type of int64. The shape is :math:`(B, )`. Default: ``None``.
        pse_shift (Tensor, optional): The position encoding tensor with data type of float16 or bfloat16. Input tensor
            of shape :math:`(1, N, 1, S)` / :math:`(B, N, 1, S)`. Default: ``None``.
        dequant_scale1 (Tensor, optional): Quantitative parametor, the tensor with data type of uint64 or float32. It
            is disable now. Default: ``None``.
        quant_scale1 (Tensor, optional): Quantitative parametor, the tensor with data type of float32. It is disable
            now. Default: ``None``.
        dequant_scale2 (Tensor, optional): Quantitative parametor, the tensor with data type of uint64 or float32. It
            is disable now. Default: ``None``.
        quant_scale2 (Tensor, optional): Post Quantitative parametor, the tensor with data type of float32.
            The shape is :math:`(1,)`. Default: ``None``.
        quant_offset2 (Tensor, optional): Post Quantitative parametor, the tensor with data type of float32.
            The shape is :math:`(1,)`. Default: ``None``.
        antiquant_scale (Tensor, optional): Pseudo Quantitative parametor, the tensor with data type of float16 or
            bfloat16. The shape is :math:`(2, kvN, 1, D)` when input_layout is 'BNSD' or :math:`(2, kvH)` when
            input_layout is 'BSH'. Default: ``None``.
        antiquant_offset (Tensor, optional): Pseudo Quantitative parametor, the tensor with data type of float16 or
            bfloat16. The shape is :math:`(2, kvN, 1, D)` when input_layout is 'BNSD' or :math:`(2, kvH)` when
            input_layout is 'BSH'. Default: ``None``.
        block_table (Tensor, optional): The tensor with data type of int32. The shape is
            :math:`(B, max\_block\_num\_per\_seq)`,
            where :math:`max\_block\_num\_per\_seq = ceil(\frac{max(actual\_seq\_length)}{block\_size} )`.
            Default: ``None``.
        num_heads (int, optional): The number of heads.  Default: ``1``.
        input_layout (str, optional): The data layout of the input qkv, support 'BSH' and 'BNSD'. Default ``'BSH'``.
        scale_value (double, optional): The scale value indicating the scale coefficient, which is used as
            the scalar of Muls in the calculation. Default: ``1.0``.
        num_key_value_heads (int, optional): Head numbers of `key`/`value` which are used in GQA algorithm.
            The value 0 indicates if the `key` and `value` have the same head nums, use numHeads.  Default: ``0``.
        block_size (int, optional): The maximum number of tokens stored in each block of KV in page attention.
            Default: ``0``.
        inner_precise (int, optional): An int number from {0, 1} indicates computing mode.
            ``0`` for high precision mode for float16 dtype. ``1`` for high performance mode.
            Default: ``1``.
        kv_padding_size (Tensor, optional): The tensor with data type of int64. The range of values is
            :math:`0\le kv\_padding\_size \le  S-max(actual\_seq\_length)`. The shape is :math:`()` or :math:`(1,)`.
            Default: ``None``.

    Returns:
        attention_out (Tensor), the shape is :math:`(B, 1, H)` / :math:`(B, N, 1, D)`.

    Raises:
        TypeError: dtype of `query` is not float16 or bfloat16.
        TypeError: `key` and `value` don't have the same dtype.
        TypeError: dtype of `attn_mask` is not bool, int8 or uint8.
        TypeError: dtype of `pse_shift` is not bfloat16 or float16.
        TypeError: `scale_value` is not a double number.
        TypeError: `input_layout` is not a string.
        TypeError: `num_key_value_heads` or `num_heads` is not an int.
        TypeError: `inner_precise` is not an int.
        TypeError: `quant_scale1` is not Tensor of type float32.
        TypeError: `quant_scale2` is not Tensor of type float32.
        TypeError: `quant_offset2` is not Tensor of type float32.
        ValueError: size of `actual_seq_lengths` is not 1 or B.
        ValueError: `input_layout` is a string but of `(BSH)` or `(BNSD)`.
        ValueError: `num_heads` is not divisible by Q_H.
        ValueError: `num_heads` is not divisible by `num_key_value_heads`.
        RuntimeError: `num_heads` is not greater than 0.
        RuntimeError: `attn_mask` shape is not valid.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> from mindspore import ops
        >>> from mindspore.common import Tensor
        >>> from mindspore.common import dtype as mstype
        >>> import numpy as np
        >>> B, N, S, D, kvN = 1, 4, 10, 128, 1
        >>> query = Tensor(np.random.randn(B, 1, N * D), mstype.float16)
        >>> key = [Tensor(np.random.randn(B, S, kvN * D), mstype.float16)]
        >>> value = [Tensor(np.random.randn(B, S, kvN * D), mstype.float16)]
        >>> ifa_ms = ops.incre_flash_attention
        >>> attn_out = ifa_ms(query, key, value, num_heads=N, num_key_value_heads=kvN)
        >>> attn_out
        Tensor(shape=[1, 1, 512], dtype=Float16, value=
        [[[ 1.6104e+00,  7.3438e-01,  1.0684e+00 ... -8.7891e-01,  1.7695e+00,  1.0264e+00]]])
    """
    _ifa = _get_cache_prim(NN_OPS.IncreFlashAttention)(num_heads, input_layout, scale_value, num_key_value_heads,
                                                       block_size, inner_precise)
    return _ifa(query, key, value, attn_mask, actual_seq_lengths, pse_shift, dequant_scale1, quant_scale1,
                dequant_scale2, quant_scale2, quant_offset2, antiquant_scale, antiquant_offset, block_table,
                kv_padding_size)


def embedding(input, weight, padding_idx=None, max_norm=None, norm_type=2.0, scale_grad_by_freq=False):
    r"""
    Retrieve the word embeddings in `weight` using indices specified in `input`.

    .. warning::
        On Ascend, the behavior is unpredictable when the value of input is invalid.

    Args:
        input (Tensor): The indices used to lookup in the `weight`. The data type must be mindspore.int32 or
            mindspore.int64, and the value should be in range `[0, weight.shape[0])`.
        weight (Union[Parameter, Tensor]): The matrix where to lookup from. The shape must be 2D.
        padding_idx (int, optional): If the value is not None, the corresponding row of `weight` will not be updated
            in training. The value should be in range `[-weight.shape[0], weight.shape[0])` if it's not ``None``.
            Default ``None``.
        max_norm (float, optional): If not None, firstly get the p-norm result of the `weight` specified by `input`
            where p is specified by `norm_type`; if the result is larger then `max_norm`, update the `weight`
            with :math:`\frac{max\_norm}{result+1e^{-7}}` in-place. Default ``None``.
        norm_type (float, optional): Indicates the value of p in p-norm. Default ``2.0``.
        scale_grad_by_freq (bool, optional): If ``True`` the gradients will be scaled by the inverse of frequency of
            the index in `input`. Default ``False``.

    Returns:
        Tensor, has the same data type as `weight`, the shape is :math:`(*input.shape, weight.shape[1])`.

    Raises:
        ValueError: If `padding_idx` is out of valid range.
        ValueError: If the shape of `weight` is invalid.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, Parameter, ops
        >>> input = Tensor([[1, 0, 1, 1], [0, 0, 1, 0]])
        >>> weight = Parameter(np.random.randn(3, 3).astype(np.float32))
        >>> output = ops.embedding(input, weight, max_norm=0.4)
        >>> print(output)
        [[[ 5.49015924e-02,  3.47811311e-01, -1.89771220e-01],
          [ 2.09307984e-01, -2.24846993e-02,  3.40124398e-01],
          [ 5.49015924e-02,  3.47811311e-01, -1.89771220e-01],
          [ 5.49015924e-02,  3.47811311e-01, -1.89771220e-01]],
         [[ 2.09307984e-01, -2.24846993e-02,  3.40124398e-01],
          [ 2.09307984e-01, -2.24846993e-02,  3.40124398e-01],
          [ 5.49015924e-02,  3.47811311e-01, -1.89771220e-01],
          [ 2.09307984e-01, -2.24846993e-02,  3.40124398e-01]]]
    """
    return embedding_op(input, weight, padding_idx, max_norm, norm_type, scale_grad_by_freq)


def speed_fusion_attention(query, key, value, head_num, input_layout, *, pse=None, padding_mask=None, atten_mask=None,
                           scale=1.0, keep_prob=1.0, pre_tokens=2147483647, next_tokens=2147483647, inner_precise=0,
                           prefix=None, actual_seq_qlen=None, actual_seq_kvlen=None, sparse_mode=0,
                           gen_mask_parallel=True, sync=False, pse_type=1, q_start_idx=None, kv_start_idx=None):
    r"""
    The interface is used for self-attention fusion computing.
    If `pse_type` is ``1`` , calculation formula is:

    .. math::
        attention\_out = Dropout(Softmax(Mask(scale * (pse + query * key^{T}), atten\_mask)), keep\_prob) * value

    If `pse_type` is other valid value, calculation formula is:

    .. math::
        attention\_out = Dropout(Softmax(Mask(scale * (query * key^{T}) + pse, atten\_mask)), keep\_prob) * value

    - B: Batch size. Value range 1 to 2k.
    - S1: Sequence length of query. Value range 1 to 512k.
    - S2: Sequence length of key and value. Value range 1 to 512k.
    - N1: Num heads of query. Value range 1 to 256.
    - N2: Num heads of key and value, and N2 must be a factor of N1.
    - D: Head size. The value ranges is a multiple of 16, with the max value of 512.
    - H1: Hidden size of query, which equals to N1 * D.
    - H2: Hidden size of key and value, which equals to N2 * D.

    .. warning::
        - This is an experimental API that is subject to change or deletion.
        - Only support on Atlas A2 training series.

    Note:
        This interface is not supported in `graph mode (mode=mindspore.GRAPH_MODE)
        <https://www.mindspore.cn/tutorials/en/master/compile/static_graph.html>`_.

    Args:
        query (Tensor): The query tensor. Input tensor of shape :math:`(B, S1, H1)`,
            :math:`(B, N1, S1, D)`, :math:`(S1, B, H1)`, :math:`(B, S1, N1, D)` or :math:`(T1, N1, D)`.
        key (Tensor): The key tensor. Input tensor of shape :math:`(B, S2, H2)`,
            :math:`(B, N2, S2, D)`, :math:`(S2, B, H2)`, :math:`(B, S2, N2, D)` or :math:`(T2, N2, D)`.
        value (Tensor): The value tensor. Input tensor of shape :math:`(B, S2, H2)`,
            :math:`(B, N2, S2, D)`, :math:`(S2, B, H2)`, :math:`(B, S2, N2, D)` or :math:`(T2, N2, D)`.
            The `key` and `value` should have the same shape.
        head_num (int): The head num of query, equal to N1.
        input_layout (str): Specifies the layout of input `query`, `key` and `value`. The value can be ``"BSH"`` ,
            ``"BNSD"`` , ``"SBH"`` , ``"BSND"`` or ``"TND"`` . ``"TND"`` is an experimental format.
            When `input_layout` is ``"TND"`` , the following restrictions must be met.
            There are two lists that represent the length of the input sequence: list_seq_q and list_seq_k. Each
            value in the list indicates the length of the sequence in the batch. For example, list_seq_q = [4, 2, 6],
            list_seq_k = [10, 3, 9]. The element of list indicate S. T1 is sum(list_seq_q) = 12, T2 is
            sum(list_seq_k) = 22.
            max_seqlen_q = max(list_seq_q), max_seqlen_k = max(list_seq_k).
            qk_pointer = sum(list_seq_q * list_seq_k), which is the sum of the element multiplication.

            - The lengths of two lists are the same, and size of list is batch. batch is less than or equal to 1024.
            - When `input_layout` is ``"TND"`` , `actual_seq_qlen` and `actual_seq_kvlen` must be not ``None`` .
              Otherwise, they are ``None`` .
            - The `actual_seq_qlen` and `actual_seq_kvlen` are the cumulative sum of sequence of key/value, so they must
              be non-decreasing.
            - If `pse` is not ``None`` , list_seq_q and list_seq_k must be same. The maximum value of list_seq_q and
              list_seq_k is greater than 1024. `pse` should be :math:`(B, N1, 1024, S2)` and
              :math:`(1, N1, 1024, S2)`, and S2 is equal to max_seqlen_k.
            - `atten_mask` must be a lower trianglar matrix, so `sparse_mode` should be 2 or 3. The shape of
              `atten_mask` should be :math:`(2048, 2048)`.
            - Prefix is ``None`` .
            - `next_tokens` is 0, and `pre_tokens` is not less than max_seqlen_q.
            - When `sparse_mode` is 3, S1 of each batch should be less than or equal to S2.
            - 0 should not exist in list_seq_k.

    Keyword Args:
        pse (Tensor, optional): The position embedding code, dtype is same as `query`.  Default: ``None`` .
            If S is greater than 1024 and the mask of the lower triangle is used, enter only the inverse 1024 lines of
            the lower triangle for memory optimization. Input tensor of shape :math:`(B, N1, S1, S2)`,
            :math:`(1, N1, S1, S2)`, :math:`(B, N1, 1024, S2)`, :math:`(1, N1, 1024, S2)`.

            - ALiBi scenario: `pse` must meet the ALiBi rule, and `sparse_mode` is 2 or 3 for the lower triangle.
              In this scenario, `pse` is :math:`(B, N1, 1024, S2)`, :math:`(1, N1, 1024, S2)`.
            - Non-ALiBi scenario: `pse` is :math:`(B, N1, S1, S2)`, :math:`(1, N1, S1, S2)`.
            - The shape of `pse` should be :math:`(B, N1, 1024, S2)` and :math:`(1, N1, 1024, S2)` when `input_layout`
              is ``"TND"`` .
            - If `pse_type` is 2 or 3, dtype of `pse` must be float32, and shape of `pse` should be :math:`(B, N1)` or
              :math:`(N1,)`.

        padding_mask (Tensor, optional): Reserved parameter. Not implemented yet. Default: ``None`` .
        atten_mask (Tensor, optional): The attention mask tensor. For each element, 0/False indicates retention and
            1/True indicates discard. Input tensor of shape :math:`(B, N1, S1, S2)`, :math:`(B, 1, S1, S2)`,
            :math:`(S1, S2)` or :math:`(2048, 2048)`. Default: ``None`` .

            - In compression scenario, `sparse_mode` is 2, 3, or 4, `atten_mask` must be :math:`(2048, 2048)`.
            - When `sparse_mode` is 5, `atten_mask` must be :math:`(B, N1, S1, S2)`, :math:`(B, 1, S1, S2)`.
            - When `sparse_mode` is 0 and 1, `atten_mask` should be :math:`(B, N1, S1, S2)`, :math:`(B, 1, S1, S2)`,
              :math:`(S1, S2)`.

        scale (float, optional): The scale factor of score. Generally, the value is 1.0 / (D ** 0.5). Default: ``1.0`` .
        keep_prob (float, optional): The keep probability of dropout. Value range is (0.0, 1.0]. Default: ``1.0`` .
        pre_tokens (int, optional): Parameter for sparse computation, represents how many tokens are counted forward.
            When `sparse_mode` is set to 1, 2, 3, or 5, this parameter does not take effect. Default: ``2147483647`` .
        next_tokens (int, optional): Parameter for sparse computation, represents how many tokens are counted backward.
            When `sparse_mode` is set to 1, 2, 3, or 5, this parameter does not take effect. Default: ``2147483647`` .
            The value of pre_tokens corresponds to S1, and the value of next_tokens corresponds to S2. They define the
            valid area on the `atten_mask` matrix. It must ensure that the band is not empty.
            The following values are not allowed:

            - pre_tokens < 0 and next_tokens < 0.
            - (pre_tokens < 0 and next_tokens >= 0) and (next_tokens < abs(pre_tokens) or abs(pre_tokens) >= S2).
            - (pre_tokens >= 0 and next_tokens < 0) and (abs(next_tokens) > pre_tokens or abs(next_tokens) >= S1).

        inner_precise (int, optional): The parameter is reserved and not implemented yet. Default: ``0`` .
        prefix (Union[tuple[int], list[int]], optional): N value of each Batch in the prefix sparse calculation
            scenario. Input tensor of shape :math:`(B,)`. B max value 32. Not none only when sparse_mode is 5.
            If S1 > S2, N ranges from 0 to S2. If S1 <= S2, N ranges from S2 - S1 to S2. Default: ``None`` .
        actual_seq_qlen (Union[tuple[int], list[int]], optional): Size of query corresponding to each batch, array
            with increasing values and the last value equal to T1. Default: ``None`` .
        actual_seq_kvlen (Union[tuple[int], list[int]], optional): Size of key and value corresponding to each batch,
            array with increasing values and the last value equal to T2. Default: ``None`` .
        sparse_mode (int, optional): Indicates sparse mode. Default ``0`` .

            - 0: Indicates the defaultMask mode. If `atten_mask` is not passed, the mask operation is not performed,
              and preTokens and nextTokens(internally assigned as INT_MAX) are ignored. If passed in, the full
              `atten_mask` matrix (S1 * S2) needs to be passed in, indicating that the part between preTokens and
              nextTokens needs to be calculated.
            - 1: Represents allMask, that is, passing in the complete `atten_mask` matrix.
            - 2: Representing the leftUpCausal mode corresponds to the lower triangle scenario divided by the left
              vertex, and the optimized `atten_mask` matrix (2048*2048) is required.
            - 3: Representing the rightDownCausal model corresponds to the lower triangle scene divided by the lower
              right vertex, and the optimized `atten_mask` matrix (2048*2048) is required.
            - 4: Represents the band scenario, that is, the part between counting preTokens and nextTokens, and the
              optimized `atten_mask` matrix (2048*2048) is required.
            - 5: Represents the prefix scenario, that is, on the basis of rightDownCasual, a matrix with length S1 and
              width N is added to the left side. The value of N is obtained by the new input prefix, and the N value
              of each Batch axis is different. Currently not enabled.
            - 6: Represents the global scenario. Currently not enabled.
            - 7: Represents the dilated scenario. Currently not enabled.
            - 8: Represents the block_local scenario. Currently not enabled.

        gen_mask_parallel (bool, optional): Debug parameter, a switch to control dropout_gen_mask execution method.
            If ``True`` , dropout_gen_mask is executed in parallel. If ``False`` , execution is serial.
            Not implemented yet. Default: ``True`` .
        sync (bool, optional): Debug parameter, a switch to control dropout_gen_mask execution method.
            If ``True`` , dropout_gen_mask is executed synchronously. If ``False`` , execution is asynchronous.
            Not implemented yet. Default: ``False`` .
        pse_type (int, optional): Indicates how to use `pse`. Default ``1`` .

            - 0: `pse` is passed from outside, and the calculation process is to first mul `scale` and then add `pse`.
            - 1: `pse` is passed from outside, and the calculation process is to add `pse` first and then mul `scale`.
            - 2: `pse` is generated internally and generates standard alibi position information. The internally
              generated alibi matrix 0 line is aligned with the upper left corner of :math:`query * key^{T}`.
            - 3: `pse` is generated internally, and the generated alibi position information is based on the standard
              and then the square root of sqrt is done. The internally generated alibi matrix 0 line is aligned with
              the upper left corner of :math:`query * key^{T}`.

        q_start_idx (Union[tuple[int], list[int]], optional): Int array with length 1. Default: ``None`` .
            When pse_type is configured as ``2`` or ``3`` , it indicates the number of cells that the internally
            generated alibi code is offset in the S1 direction. A positive number indicates that 0 moves diagonally
            upward.
        kv_start_idx (Union[tuple[int], list[int]], optional): Int array with length 1. Default: ``None`` .
            When pse_type is configured as ``2`` or ``3`` , it indicates the number of cells that the internally
            generated alibi code is offset in the S2 direction. A positive number indicates that 0 moves diagonally
            upward.

    Returns:
        A tuple of tensors containing `attention_out`, `softmax_max`, `softmax_sum`, `softmax_out`, `seed`, `offset`
        and `numels` .

        - `attention_out` is the output of attention, it's shape, and data type are the same as the query.
        - `softmax_max` is the max intermediate result calculated by Softmax, used for grad calculation.
        - `softmax_sum` is the sum intermediate result calculated by Softmax, used for grad calculation.
        - `softmax_out` is a reserved parameter.
        - `seed` is generated seed, used for Dropout.
        - `offset` is generated offset, used for Dropout.
        - `numels` is the length of generated dropout_mask.

    Raises:
        TypeError: `query`, `key` and `value` don't have the same dtype.
        TypeError: Dtype of `atten_mask` is not bool or uint8.
        TypeError: `scale` or `keep_prob` is not a float number.
        TypeError: `input_layout` is not a string.
        TypeError: `head_num` is not an int.
        TypeError: `sparse_mode` is not an int.
        TypeError: `pse` is not Tensor type.
        TypeError: `padding_mask` is not Tensor type.
        TypeError: `atten_mask` is not Tensor type.
        TypeError: `pse_type` is not an int.
        ValueError: `input_layout` is a string but not valid.
        ValueError: The specified value of `sparse_mode` is invalid.
        ValueError: The specified value of `pse_type` is invalid.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> import mindspore.common.dtype as mstype
        >>> import numpy as np
        >>> from mindspore import ops, Tensor
        >>> query = Tensor(np.ones([2, 4, 64]), dtype=mstype.float16)
        >>> key = Tensor(np.ones([2, 4, 64]), dtype=mstype.float16)
        >>> value = Tensor(np.ones([2, 4, 64]), dtype=mstype.float16)
        >>> head_num = 4
        >>> input_layout = "BSH"
        >>> output = ops.speed_fusion_attention(query, key, value, head_num, input_layout)
        >>> print(output[0].shape)
        (2, 4, 64)
    """
    seed, offset = default_generator._step(generator_step_)  # pylint: disable=protected-access
    return speed_fusion_attention_op(query, key, value, head_num, input_layout, seed, offset, pse, padding_mask,
                                     atten_mask, scale, keep_prob, pre_tokens, next_tokens, inner_precise, prefix,
                                     actual_seq_qlen, actual_seq_kvlen, sparse_mode, gen_mask_parallel, sync, pse_type,
                                     q_start_idx, kv_start_idx)


__all__ = [
    'adaptive_avg_pool1d',
    'adaptive_avg_pool2d',
    'adaptive_avg_pool2d_ext',
    'adaptive_avg_pool3d',
    'adaptive_max_pool1d',
    'adaptive_max_pool2d',
    'adaptive_max_pool3d',
    'avg_pool1d',
    'avg_pool2d',
    'avg_pool3d',
    'batch_norm',
    'bias_add',
    'bidense',
    'binary_cross_entropy',
    'binary_cross_entropy_with_logits',
    'cosine_embedding_loss',
    'max_pool2d',
    'max_pool3d',
    'kl_div',
    'celu',
    'dense',
    'deformable_conv2d',
    'dropout1d',
    'dropout2d',
    'dropout3d',
    'embedding',
    'fast_gelu',
    'fractional_max_pool2d',
    'fractional_max_pool3d',
    'speed_fusion_attention',
    'pixel_shuffle',
    'pixel_unshuffle',
    'hardshrink',
    'is_floating_point',
    'incre_flash_attention',
    'prompt_flash_attention',
    'flash_attention_score',
    'fused_infer_attention_score',
    'flip',
    'fliplr',
    'flipud',
    'intopk',
    'interpolate',
    'upsample',
    'layer_norm',
    'mse_loss_ext',
    'log_softmax',
    'mish',
    'lrn',
    'hardswish',
    'hardtanh',
    'huber_loss',
    'softsign',
    'softshrink',
    'soft_shrink',
    'softplus',
    'selu',
    'silu',
    'softmax',
    'softmin',
    'pdist',
    'pad',
    'prelu',
    'mirror_pad',
    'cross_entropy',
    'grid_sample',
    'smooth_l1_loss',
    'l1_loss',
    'threshold',
    'leaky_relu',
    'nll_loss',
    'ctc_loss',
    'ctc_greedy_decoder',
    'dropout',
    'conv3d_transpose',
    'conv1d',
    'conv2d',
    'conv_transpose2d',
    'sigmoid',
    'soft_margin_loss',
    'logsigmoid',
    'relu',
    'relu6',
    'rrelu',
    'swiglu',
    'conv3d',
    'glu',
    'margin_ranking_loss',
    'multi_margin_loss',
    'multilabel_margin_loss',
    'multilabel_soft_margin_loss',
    'elu',
    'gelu',
    'hinge_embedding_loss',
    'gaussian_nll_loss',
    'lp_pool1d',
    'lp_pool2d',
    'moe_token_permute',
    'moe_token_unpermute',
    'ring_attention_update',
    'max_unpool1d',
    'max_unpool2d',
    'max_unpool3d',
    'mse_loss',
    'msort',
    'triplet_margin_loss',
    'channel_shuffle',
    'hardsigmoid',
    'add_layer_norm',
    'group_norm',
    'rms_norm',
    'add_rms_norm',
]
__all__.sort()
