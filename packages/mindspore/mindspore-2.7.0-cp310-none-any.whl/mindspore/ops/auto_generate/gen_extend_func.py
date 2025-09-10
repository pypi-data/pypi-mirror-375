# Copyright 2023 Huawei Technologies Co., Ltd
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

from mindspore.common import dtype as mstype
from mindspore.ops.auto_generate.pyboost_inner_prim import *


def atan(input):
    r"""
    Computes the trigonometric inverse tangent of the input element-wise.
    
    .. math::
    
        out_i = \tan^{-1}(input_i)
    
    Args:
        input (Tensor): The shape of tensor is
            :math:`(N,*)` where :math:`*` means, any number of additional dimensions.
    
    Returns:
        Tensor, has the same shape as `input`. The dtype of output is float32 when dtype of `input` is in [bool, int8, uint8, int16, int32, int64]. Otherwise output has the same dtype as `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([1.0, 0.0]), mindspore.float32)
        >>> output = ops.atan_ext(input)
        >>> print(output)
        [0.7853982 0.       ]
    """
    return atan_impl(input)


def frac(input):
    r"""
    Calculates the fractional part of each element in the input.
    
    .. math::
        out_i = input_i - \lfloor |input_i| \rfloor * sgn(input_i)
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): The input Tensor.
    
    Returns:
        Tensor, has the same shape and type as input.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor([2, 4.2, -2.5], mindspore.float16)
        >>> output = ops.frac_ext(x)
        >>> print(output)
          [ 0.      0.1992 -0.5   ]
    """
    return frac_impl(input)


def asin(input):
    r"""
    Computes arcsine of input tensors element-wise.
    
    .. math::
    
        out_i = \sin^{-1}(input_i)
    
    Args:
        input (Tensor): The shape of tensor is
            :math:`(N,*)`, where :math:`*` means any number of additional dimensions.
    
    Returns:
        Tensor, has the same shape as `input`. The dtype of output is float32 when dtype of `input` is in [bool, int8, uint8, int16, int32, int64]. Otherwise output has the same dtype as `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([0.74, 0.04, 0.30, 0.56]), mindspore.float32)
        >>> output = ops.asin_ext(input)
        >>> print(output)
        [0.8330927  0.04001068  0.30469266  0.59438497 ]
    """
    return asin_impl(input)


def avg_pool1d(input, kernel_size, stride=None, padding=0, ceil_mode=False, count_include_pad=True):
    r"""
    Applies a 1D average pooling over an input Tensor which can be regarded as a composition of 1D input planes.
    
    Typically the input is of shape :math:`(N_{in}, C_{in}, L_{in})`, avg_pool1d outputs regional average in the
    :math:`(L_{in})`-dimension. Given kernel size as :math:`ks = l_{ker}` and `stride` as :math:`s = s_0`, the
    operation is as follows.
    
    .. math::
        \text{output}(N_i, C_j, l) = \frac{1}{l_{ker}} \sum_{n=0}^{l_{ker}-1}
        \text{input}(N_i, C_j, s_0 \times l + n)
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): Tensor of shape :math:`(N, C_{in}, L_{in})`.
        kernel_size (Union(int, tuple[int])): The size of kernel window used to take the average value.
        stride (Union(int, tuple[int]), optional): The distance of kernel moving. `stride` can either be an int
            number or a tuple of one int number. Default: ``None``, the same value as `kernel_size`.
        padding (Union(int, tuple[int]), optional): The pad length to be filled. `padding` can either be an integer
            or a tuple of one integer. Default: ``0`` .
        ceil_mode (bool, optional): If True, apply ceil instead of floor to compute the output shape. Default: ``False``.
        count_include_pad (bool, optional): If True, include the zero-padding in the averaging calculation. Default: ``True`` .
    
    Returns:
        Tensor of shape :math:`(N, C_{in}, L_{out})`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `kernel_size` or `stride` is not an int.
        TypeError: If `ceil_mode` or `count_include_pad` is not a bool.
        ValueError: If `kernel_size` or `stride` is less than `1`.
        ValueError: If `kernel_size` or `stride` or `padding` is not int nor a tuple whose length is greater than `1`.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.random.randint(0, 10, [1, 3, 6]), mindspore.float32)
        >>> output = ops.auto_generate.avg_pool1d_ext(input_x, kernel_size=6, stride=1)
        >>> print(output.shape)
        (1, 3, 1)
    """
    return avg_pool1d_impl(input, kernel_size, stride, padding, ceil_mode, count_include_pad)


def cumsum(input, dim, dtype=None):
    r"""
    Computes the cumulative sum of input Tensor along `dim`.
    
    .. math::
    
        y_i = x_1 + x_2 + x_3 + ... + x_i
    
    Args:
        input (Tensor): The input Tensor.
        dim (int): Dim along which the cumulative sum is computed.
        dtype (:class:`mindspore.dtype`, optional): The desired dtype of returned Tensor. If specified,
            the input Tensor will be cast to `dtype` before the computation. This is useful for preventing overflows.
            If not specified, stay the same as original Tensor. Default: ``None`` .
    
    Returns:
        Tensor, the shape of the output Tensor is consistent with the input Tensor's.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        ValueError: If the `dim` is out of range.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> import mindspore.ops as ops
        >>> x = Tensor(np.array([[3, 4, 6, 10], [1, 6, 7, 9], [4, 3, 8, 7], [1, 3, 7, 9]]).astype(np.float32))
        >>> # case 1: along the dim 0
        >>> y = ops.auto_generate.cumsum_ext(x, 0)
        >>> print(y)
        [[ 3.  4.  6. 10.]
        [ 4. 10. 13. 19.]
        [ 8. 13. 21. 26.]
        [ 9. 16. 28. 35.]]
        >>> # case 2: along the dim 1
        >>> y = ops.auto_generate.cumsum_ext(x, 1)
        >>> print(y)
        [[ 3.  7. 13. 23.]
        [ 1.  7. 14. 23.]
        [ 4.  7. 15. 22.]
        [ 1.  4. 11. 20.]]
    """
    return cumsum_impl(input, dim, dtype)


def sub_tensor_(input, other, alpha=1):
    r"""
    None
    """
    return sub_tensor_impl(input, other, alpha)


def unfold(input, kernel_size, dilation=1, padding=0, stride=1):
    r"""
    Extracts sliding local blocks from a batched input tensor.
    
    Consider a batched input tensor of shape :math:`(N, C, *)`,
    where :math:`N` is the batch dimension, :math:`C` is the channel dimension,
    and :math:`*` represent arbitrary spatial dimensions. This operation flattens
    each sliding `Kernel_size`- sized block within the spatial dimensions
    of `input` into a column (i.e., last dimension) of a 3-D output
    tensor of shape :math:`(N, C \times \prod(\text{kernel_size}), L)`, where
    :math:`C \times \prod(\text{kernel_size})` is the total number of values
    within each block (a block has :math:`\prod(\text{kernel_size})` spatial
    locations each containing a `C`-channeled vector), and :math:`L` is
    the total number of such blocks:
    
    .. math::
        L = \prod_d \left\lfloor\frac{\text{spatial_size}[d] + 2 \times \text{padding}[d] %
            - \text{dilation}[d] \times (\text{kernel_size}[d] - 1) - 1}{\text{stride}[d]} + 1\right\rfloor,
    
    where :math:`\text{spatial_size}` is formed by the spatial dimensions
    of `input` (:math:`*` above), and :math:`d` is over all spatial
    dimensions.
    
    Therefore, indexing `output` at the last dimension (column dimension)
    gives all values within a certain block.
    
    The `dilation`, `padding` and `stride` arguments specify
    how the sliding blocks are retrieved.
    
    .. warning::
        - Currently, batched(4D) image-like tensors are supported.
        - For Ascend, it is only supported on platforms above Atlas A2.
    
    Args:
        input (Tensor): 4-D Tensor.
        kernel_size (Union[int, tuple[int], list[int]]): The size of the kernel, should be two int
            for height and width. If type is int, it means that height equal with width. Must be specified.
        dilation (Union[int, tuple[int], list[int]], optional): The dilation of the window, should be two int
            for height and width. If type is int, it means that height equal with width. Default: ``1`` .
        padding (Union[int, tuple[int], list[int]], optional): The pad of the window, should be two int
            for height and width. If type is int, it means that height equal with width. Default: ``0`` .
        stride (Union[int, tuple[int], list[int]], optional): The stride of the window, should be two int
            for height and width. If type is int, it means that height equal with width. Default: ``1`` .
    
    Returns:
        A Tensor, with same type as `input` .
    
    Shape:
        - Input: :math:`(N, C, *)`
        - Output: :math:`(N, C \times \prod(\text{kernel_size}), L)`
    
    Raises:
        TypeError: If any data type of `kernel_size`, `stride`, `dilation`, `padding` is not int, tuple or list.
        ValueError: If `kernel_size`, `dilation`, `stride` value is not
            greater than zero or elements number more than `2`.
        ValueError: If `padding` value is less than zero.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.random.rand(4, 4, 32, 32), mindspore.float32)
        >>> output = ops.auto_generate.unfold_ext(x, kernel_size=3, dilation=1, stride=1)
        >>> print(output.shape)
        (4, 36, 900)
    """
    return unfold_impl(input, converted_kernel_size, converted_dilation, converted_padding, converted_stride)


def inplace_adds(input, other, alpha=1):
    r"""
    None
    """
    return inplace_adds_impl(input, other, alpha)


def asinh(input):
    r"""
    Computes inverse hyperbolic sine of the input element-wise.
    
    .. math::
    
        out_i = \sinh^{-1}(input_i)
    
    Args:
        input (Tensor): The input tensor of inverse hyperbolic sine function.
    
    Returns:
        Tensor, has the same shape as `input`. The dtype of output is float32 when dtype of `input` is in [bool, int8, uint8, int16, int32, int64]. Otherwise output has the same dtype as `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([-5.0, 1.5, 3.0, 100.0]), mindspore.float32)
        >>> output = ops.asinh_ext(input)
        >>> print(output)
        [-2.3124385  1.1947632  1.8184465  5.298342 ]
    """
    return asinh_impl(input)


def argmin(input, dim=None, keepdim=False):
    r"""
    Return the indices of the minimum values of a tensor across a dimension.
    
    Args:
        input (Tensor): Input tensor.
        dim (Union[int, None], optional): Specify the axis for calculation. If `dim` is ``None`` , the indices of the minimum
            value within the flattened input will be returned. Default: ``None`` .
        keepdim (bool, optional): Whether the output tensor retains the specified
            dimension. Ignored if `dim` is None. Default: ``False`` .
    
    Returns:
        Tensor, indices of the minimum values of the input tensor across a dimension.
    
    Raises:
        TypeError: If `keepdim` is not bool.
        ValueError: If `dim` is out of range.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> x = Tensor(np.array([[1, 20, 5], [67, 8, 9], [130, 24, 15]]).astype(np.float32))
        >>> output = ops.auto_generate.argmin_ext(x, dim=-1)
        >>> print(output)
        [0 1 2]
    """
    return argmin_impl(input, dim, keepdim)


def log_softmax(input, dim=None, dtype=None):
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
            If set to None, stay the same as original Tensor. Default: ``None`` . Supported data type is {float16, float32, double, bfloat16}.
    
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
        >>> output = ops.auto_generate.log_softmax(logits, dim=-1)
        >>> print(output)
        [-4.4519143 -3.4519143 -2.4519143 -1.4519144 -0.4519144]
    """
    return log_softmax_impl(input, dim, dtype)


def matrix_inverse(input):
    r"""
    Compute the inverse of the input matrix.
    
    Args:
        input (Tensor): A matrix to be calculated. Input `input` must be at least two dimensions, and the size of
            the last two dimensions must be the same size.
    
    Returns:
        Tensor, has the same type and shape as input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        ValueError: If the size of the last two dimensions of `input` is not the same.
        ValueError: If the dimension of `input` is 1.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> x = Tensor([[1., 2.], [3., 4.]], mstype.float32)
        >>> print(ops.matrix_inverse_ext(x))
        [[-2.   1. ]
         [ 1.5 -0.5]]
    """
    return matrix_inverse_impl(input)


def histc(input, bins=100, min=0, max=0):
    r"""
    Computes the histogram of a tensor.
    
    The elements are sorted into equal width bins between `min` and `max`.
    If `min` and `max` are both zero, the minimum and maximum values of the data are used.
    
    Elements lower than min or higher than max are ignored.
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
        If input is int64, valid values fit within int32; exceeding this may cause precision errors.
    
    Args:
        input (Tensor): the input tensor.
        bins (int, optional): Number of histogram bins, optional. If specified, must be positive. Default: ``100`` .
        min (int, float, optional): the lower end of the range (inclusive), optional. Default: ``0`` .
        max (int, float, optional): the upper end of the range (inclusive), optional. Default: ``0`` .
    
    Returns:
        A 1-D Tensor, has the same type as `input` with the shape :math:`(bins, )`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `input` datatype is not in support list.
        TypeError: If attr `min` or `max` is not float or int.
        TypeError: If attr `bins` is not int.
        ValueError: If attr value `min` > `max`.
        ValueError: If attr `bins` <= 0.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> from mindspore import Tensor, ops
        >>> x = Tensor([1., 2, 1])
        >>> y = ops.histc_ext(x, bins=4, min=0, max=3)
        >>> print(y)
        [0 2 1 0]
    """
    return histc_impl(input, bins, min, max)


def acosh(input):
    r"""
    Computes inverse hyperbolic cosine of the inputs element-wise.
    
    .. math::
    
        out_i = \cosh^{-1}(input_i)
    
    .. note::
        Given an input tensor input, the function computes inverse hyperbolic cosine of every element.
        Input range is [1, inf].
    
    Args:
        input (Tensor): The input tensor of inverse hyperbolic cosine function.
    
    Returns:
        Tensor, has the same shape as `input`. The dtype of output is float32 when dtype of `input` is in [bool, int8, uint8, int16, int32, int64]. Otherwise output has the same dtype as `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([1.0, 1.5, 3.0, 100.0]), mindspore.float32)
        >>> output = ops.acosh_ext(input)
        >>> print(output)
        [0.        0.9624236 1.7627472 5.298292 ]
    """
    return acosh_impl(input)


def sub(input, other, alpha=1):
    r"""
    Subtracts scaled other value from input Tensor.
    
    .. math::
    
        out_{i} = input_{i} - alpha \times other_{i}
    
    Note:
        - When the two inputs have different shapes,
          they must be able to broadcast to a common shape.
        - The two inputs and alpha comply with the implicit type conversion rules to make the data types
          consistent.
    
    Args:
        input (Union[Tensor, number.Number, bool]): The first input is a number.Number or
            a bool or a tensor whose data type is
            `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
            `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
        other (Union[Tensor, number.Number, bool]): The second input, is a number.Number or
            a bool or a tensor whose data type is
            `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
            `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
        alpha (number.Number): A scaling factor applied to `other`, default 1.
    
    Returns:
        Tensor with a shape that is the same as the broadcasted shape of the input `input` and `other`,
        and the data type is the one with higher precision or higher digits among the two inputs and alpha.
    
    Raises:
        TypeError: If the type of `input`, `other`, or `alpha` is not one of the following: Tensor, number.Number, bool.
        TypeError: If `alpha` is of type float but `input` and `other` are not of type float.
        TypeError: If `alpha` is of type bool but `input` and `other` are not of type bool.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import numpy as np
        >>> import mindspore
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> x = Tensor(np.array([4, 5, 6]).astype(np.float32))
        >>> y = Tensor(1, mindspore.int32)
        >>> alpha = 0.5
        >>> output = ops.auto_generate.sub_ext(x, y, alpha)
        >>> print(output)
        [3.5 4.5 5.5]
        >>> # the data type of x is float32, the data type of y is int32,
        >>> # alpha is a float, and the output is the data format of higher precision float32.
        >>> print(output.dtype)
        Float32
    """
    return sub_impl(input, other, alpha)


def tril(input, diagonal=0):
    r"""
    None
    """
    return tril_impl(input, diagonal)


def argsort(input, dim=-1, descending=False, stable=False):
    r"""
    Sorts the input tensor along the given dimension in specified order and return the sorted indices.
    
    .. warning::
            This is an experimental optimizer API that is subject to change.
    
    Args:
        input(Tensor): The input tensor to sort.
        dim (int, optional): The dim to sort along. Default: ``-1`` , means the last dimension.
            The Ascend backend only supports sorting the last dimension.
        descending (bool, optional): The sort order. If `descending` is ``True`` then the elements
            are sorted in descending order by value. Otherwise sort in ascending order. Default: ``False`` .
        stable (bool, optional): Whether to use stable sorting algorithm. Default: ``False``.
    
    Returns:
        Tensor, the indices of sorted input tensor. Data type is int64.
    
    Raises:
        ValueError: If `dim` is out of range.
        TypeError: If dtype of `dim` is not int32.
        TypeError: If dtype of `descending` is not bool.
        TypeError: If dtype of `stable` is not bool.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[8, 2, 1], [5, 9, 3], [4, 6, 7]]), mindspore.float16)
        >>> sort = ops.auto_generate.argsort_ext(x)
        >>> print(sort)
        [[2 1 0]
         [2 0 1]
         [0 1 2]]
    """
    return argsort_impl(input, dim, descending, stable)


def acos(input):
    r"""
    Computes arccosine of input tensors element-wise.
    
    .. math::
    
        out_i = \cos^{-1}(input_i)
    
    Args:
        input (Tensor): The shape of tensor is
            :math:`(N,*)`, where :math:`*` means any number of additional dimensions.
    
    Returns:
        Tensor, has the same shape as `input`. The dtype of output is float32 when dtype of `input` is in [bool, int8, uint8, int16, int32, int64]. Otherwise output has the same dtype as `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([0.74, 0.04, 0.30, 0.56]), mindspore.float32)
        >>> output = ops.acos_ext(input)
        >>> print(output)
        [0.7377037  1.5307857 1.2661037 0.9764114]
    """
    return acos_impl(input)


def mm(input, mat2):
    r"""
    Returns the matrix product of two arrays.
    If `input` is a :math:`(n \times m)` Tensor, `mat2` is a
    :math:`(m \times p)` Tensor, `out` will be a :math:`(n \times p)` Tensor.
    
    Note:
        This function cannot support broadcasting.
        Refer to :func:`mindspore.ops.matmul` instead if you need a broadcastable function.
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): The first matrix of matrix multiplication.
            The last dimension of `input` must be the same size as the first dimension of `mat2`.
        mat2 (Tensor): The second matrix of matrix multiplication.
            The last dimension of `input` must be the same size as the first dimension of `mat2`.
    
    Returns:
        Tensor, the matrix product of the inputs.
    
    Raises:
        ValueError: If the last dimension of `input` is not the same size as the
            second-to-last dimension of `mat2`.
        TypeError: If `input` or `mat2` is not a Tensor.
        TypeError: If dtype of `input` or `mat2` is not float16, float32 or bfloat16.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> import numpy as np
        >>> x1 = ms.Tensor(np.random.rand(2, 3), ms.float32)
        >>> x2 = ms.Tensor(np.random.rand(3, 4), ms.float32)
        >>> out = ops.mm_ext(x1, x2)
        >>> print(out.shape)
        (2, 4)
    """
    return mm_impl(input, mat2)


def log2(input):
    r"""
    Returns the logarithm to the base 2 of a tensor element-wise.
    
    .. math::
        y_i = \log_2(x_i)
    
    .. warning::
        - If the input value of operator Log2 is within the range (0, 0.01] or [0.95, 1.05], the output accuracy
          may be affacted.
    
    Args:
        input (Tensor): Input Tensor of any dimension. The value must be greater than 0.
    
    Returns:
        Tensor, has the same shape as the `input`. If `input.dtype` is of integer or boolean type, the output dtype
        will be float32. Otherwise, the output dtype will be the same as `input.dtype`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([3.0, 5.0, 7.0]), mindspore.float32)
        >>> output = ops.auto_generate.log2_ext(x)
        >>> print(output)
        [1.5849625 2.321928  2.807355 ]
    """
    return log2_impl(input)


def softplus(input, beta=1, threshold=20):
    r"""
    Applies softplus function to `input` element-wise.
    
    The softplus function is shown as follows, x is the element of `input` :
    
    .. math::
    
        \text{output} = \frac{1}{beta}\log(1 + \exp(\text{beta * x}))
    
    where :math:`input * beta > threshold`, the implementation converts to the linear function to ensure numerical stability.
    
    Args:
        input (Tensor): Tensor of any dimension. Supported dtypes: 
    
            - Ascend: float16, float32, bfloat16.
        beta (number.Number, optional): Scaling parameters in the softplus function. Default: ``1`` .
        threshold (number.Number, optional): For numerical stability, the softplus function is converted 
            to a threshold parameter of a linear function. Default: ``20`` .
    
    Returns:
        Tensor, with the same type and shape as the input.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not float16, float32, bfloat16.
    
    Supported Platforms:
        ``Ascend`` 
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([0.1, 0.2, 30, 25]), mindspore.float32)
        >>> output = ops.auto_generate.softplus_ext(input)
        >>> print(output)
        [0.74439657 0.7981388 30. 25.]
    """
    return softplus_impl(input, beta, threshold)


def sum(input, dim=None, keepdim=False, dtype=None):
    r"""
    Calculate sum of Tensor elements over a given dim.
    
    Note:
        The `dim` with tensor type is only used for compatibility with older versions and is not recommended.
    
    Args:
        input (Tensor): The input tensor.
        dim (Union[None, int, tuple(int), list(int), Tensor]): Dimensions along which a sum is performed.
            If ``None`` , sum all the elements of the input tensor.
            If the `dim` is a tuple or list of ints, a sum is performed on all the dimensions specified in the tuple.
            Must be in the range :math:`[-input.ndim, input.ndim)` . Default: ``None`` .
        keepdim (bool): Whether the output tensor has `dim` retained or not.
            If ``True`` , keep these reduced dimensions and the length is 1.
            If ``False`` , don't keep these dimensions. Default: ``False`` .
        dtype (:class:`mindspore.dtype`): The desired data type of returned Tensor. Default: ``None`` .
    
    Returns:
        A Tensor, sum of elements over a given `dim` in `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `dim` is not an int, tulpe(int), list(int), Tensor or None.
        ValueError: If `dim` is not in the range :math:`[-input.ndim, input.ndim)` .
        TypeError: If `keepdim` is not a bool.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> x = Tensor(np.array([[[1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]],
        ...                      [[4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [6, 6, 6, 6, 6, 6]],
        ...                      [[7, 7, 7, 7, 7, 7], [8, 8, 8, 8, 8, 8], [9, 9, 9, 9, 9, 9]]]), mstype.float32)
        >>> out = ops.sum_ext(x)
        >>> print(out)
        270.0
        >>> out = ops.sum_ext(x, dim=2)
        >>> print(out)
        [[ 6. 12. 18.]
        [24. 30. 36.]
        [42. 48. 54.]]
        >>> out = ops.sum_ext(x, dim=2, keepdim=True)
        >>> print(out)
        [[[ 6.]
        [12.]
        [18.]]
        [[24.]
        [30.]
        [36.]]
        [[42.]
        [48.]
        [54.]]]
    """
    return sum_impl(input, dim, keepdim, dtype)


def matmul(input, other):
    r"""
    None
    """
    return matmul_impl(input, other)


def bmm(input, mat2):
    r"""
    Performs batch matrix-matrix multiplication of two three-dimensional tensors.
    
    .. math::
        \text{output}= \text{input} @ \text{mat2}
    
    Args:
        input (Tensor): The first batch of matrices to be multiplied. Must be a three-dimensional tensor of shape `(b, n, m)`.
        mat2 (Tensor): The second batch of matrices to be multiplied. Must be a three-dimensional tensor of shape `(b, m, p)`.
    
    Returns:
        Tensor, the output tensor of shape `(b, n, p)`, where each matrix is the product of the corresponding matrices in the input batches.
    
    Raises:
        ValueError: If `input` or `mat2` is not three-dimensional tensors.
        ValueError: If the length of the third dimension of `input` is not equal to the length of the second dimension of `mat2`.
        ValueError: If the batch size of the inputs is not equal to the batch size of the mat2.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> a = Tensor(np.ones(shape=[2, 3, 4]), mindspore.float32)
        >>> b = Tensor(np.ones(shape=[2, 4, 5]), mindspore.float32)
        >>> output = ops.auto_generate.bmm_ext(a, b)
        >>> print(output)
        [[[4. 4. 4. 4. 4.]
          [4. 4. 4. 4. 4.]
          [4. 4. 4. 4. 4.]]
         [[4. 4. 4. 4. 4.]
          [4. 4. 4. 4. 4.]
          [4. 4. 4. 4. 4.]]]
    """
    return bmm_impl(input, mat2)


def stack(tensors, dim=0):
    r"""
    Stacks a list of tensors in specified dim.
    
    Stacks the list of input tensors with the same rank `R`, output is a tensor of rank `(R+1)`.
    
    Given input tensors of shape :math:`(x_1, x_2, ..., x_R)`. Set the number of input tensors as `N`.
    If :math:`dim \ge 0`, the shape of the output tensor is
    :math:`(x_1, x_2, ..., x_{dim}, N, x_{dim+1}, ..., x_R)`.
    
    Args:
        tensors (Union[tuple, list]): A Tuple or list of Tensor objects with the same shape and type.
        dim (int, optional): Dimension to stack. The range is [-(R+1), R+1). Default: ``0`` .
    
    Returns:
        Tensor. A stacked Tensor with the same type as `tensors`.
    
    Raises:
        TypeError: If the data types of elements in `tensors` are not the same.
        ValueError: If `dim` is out of the range [-(R+1), R+1);
                    or if the shapes of elements in `tensors` are not the same.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> import numpy as np
        >>> data1 = Tensor(np.array([0, 1]).astype(np.float32))
        >>> data2 = Tensor(np.array([2, 3]).astype(np.float32))
        >>> output = ops.auto_generate.stack_ext([data1, data2], 0)
        >>> print(output)
        [[0. 1.]
         [2. 3.]]
    """
    return stack_impl(tensors, dim)


def isneginf(input):
    r"""
    Determines which elements are -inf for each position.
    
    .. warning::
        - This API can be used only on the Atlas A2 training series.
    
    Args:
        input (Tensor): Input Tensor.
    
    Returns:
        Tensor with the same shape as the input, where elements are `True` if the corresponding element in the `input` is negative infinity, and `False` otherwise.
    
    Raises:
        TypeError: If the input is not a tensor.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> from mindspore import ops, Tensor
        >>> from mindspore import dtype as mstype
        >>> output = ops.isneginf(Tensor([[-float("inf"), float("inf")], [1, -float("inf")]], mstype.float32))
        >>> print(output)
        [[ True False]
         [False  True]]
    """
    return isneginf_impl(input)


def max_unpool2d(input, indices, kernel_size, stride=None, padding=0, output_size=None):
    r"""
    Computes the inverse of `max_pool2d`.
    
    `max_unpool2d` keeps the maximal value and set all position of non-maximal values to zero. Typically the input is of shape :math:`(N, C, H_{in}, W_{in})` or :math:`(C, H_{in}, W_{in})`, and the output is of shape :math:`(N, C, H_{out}, W_{out})` or :math:`(C, H_{out}, W_{out})`. The operation is as follows.
    
    .. math::
        \begin{array}{ll} \\
        H_{out} = (H_{in} - 1) \times stride[0] - 2 \times padding[0] + kernel\_size[0] \\
        W_{out} = (W_{in} - 1) \times stride[1] - 2 \times padding[1] + kernel\_size[1] \\
        \end{array}
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): The input Tensor to invert. Tensor of shape :math:`(N, C, H_{in}, W_{in})` or :math:`(C, H_{in}, W_{in})`.
        indices (Tensor): Max values' index represented by the indices. Tensor of shape must be same with input 'input'. Values of indices must belong to :math:`[0, H_{in} \times W_{in} - 1]`. Data type must be in int32 or int64.
        kernel_size (Union[int, tuple[int]]): The size of kernel used to take the maximum value, an int number that represents height and width of the kernel, or a tuple of two int numbers that represent height and width respectively.
        stride (Union[int, tuple[int]], optional): The distance of kernel moving, an int number that represents the height and width of movement are both stride, or a tuple of two int numbers that represent height and width of movement respectively. Default: ``None`` , which indicates the moving step is `kernel_size` .
        padding (Union[int, tuple[int]], optional): The pad value to be filled. Default: ``0`` . If `padding` is an integer, the paddings of height and width are the same, equal to padding. If `padding` is a tuple of two integers, the padding of height and width equal to padding[0] and padding[1] correspondingly.
        output_size (tuple[int], optional): The target output size. Default: ``None`` . If output_size == (), then the shape of output computed by `kernel_size`, `stride` and `padding`. If output_size != (), then output_size must be :math:`(N, C, H, W)` , :math:`(C, H, W)` or :math:`(H, W)` and output_size must belong to :math:`[(N, C, H_{out} - stride[0], W_{out} - stride[1]), (N, C, H_{out} + stride[0], W_{out} + stride[1])]`.
    
    Returns:
        Tensor, with shape :math:`(N, C, H_{out}, W_{out})` or :math:`(C, H_{out}, W_{out})`, with the same data type with `input`.
    
    Raises:
        TypeError: If data type of `input` or `indices` is not supported.
        TypeError: If `kernel_size`, `stride` or `padding` is neither an int nor a tuple.
        ValueError: If numbers in `stride`, `padding` or `kernel_size` are not positive.
        ValueError: If the shapes of `input` and `indices` are different.
        ValueError: If the length of `input` is not 3 or 4.
        ValueError: If the type of `output_size` is not tuple.
        ValueError: If `output_size` is not close to output size computed by attr `kernel_size`, `stride`, `padding`.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[[[0, 1], [8, 9]]]]).astype(np.float32))
        >>> indices = Tensor(np.array([[[[0, 1], [2, 3]]]]).astype(np.int64))
        >>> output = ops.max_unpool2d_ext(input, indices, 1, stride=1, padding=0)
        >>> print(output.asnumpy())
        [[[[0. 1.]
           [8. 9.]]]]
    """
    return max_unpool2d_impl(input, indices, kernel_size, stride, padding, output_size)


def add(input, other, alpha=1):
    r"""
    Adds scaled other value to input Tensor.
    
    .. math::
    
        out_{i} = input_{i} + alpha \times other_{i}
    
    Note:
        - When the two inputs have different shapes,
          they must be able to broadcast to a common shape.
        - The two inputs and alpha comply with the implicit type conversion rules to make the data types
          consistent.
    
    Args:
        input (Union[Tensor, number.Number, bool]): The first input is a number.Number or
            a bool or a tensor whose data type is
            `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
            `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
        other (Union[Tensor, number.Number, bool]): The second input, is a number.Number or
            a bool or a tensor whose data type is
            `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
            `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
        alpha (number.Number): A scaling factor applied to `other`, default 1.
    
    Returns:
        Tensor with a shape that is the same as the broadcasted shape of the input `input` and `other`,
        and the data type is the one with higher precision or higher digits among the two inputs and alpha.
    
    Raises:
        TypeError: If the type of `input`, `other`, or `alpha` is not one of the following: Tensor, number.Number, bool.
        TypeError: If `alpha` is of type float but `input` and `other` are not of type float.
        TypeError: If `alpha` is of type bool but `input` and `other` are not of type bool.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import numpy as np
        >>> import mindspore
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> x = Tensor(1, mindspore.int32)
        >>> y = Tensor(np.array([4, 5, 6]).astype(np.float32))
        >>> alpha = 0.5
        >>> output = ops.auto_generate.add_ext(x, y, alpha)
        >>> print(output)
        [3. 3.5 4.]
        >>> # the data type of x is int32, the data type of y is float32,
        >>> # alpha is a float, and the output is the data format of higher precision float32.
        >>> print(output.dtype)
        Float32
    """
    return add_impl(input, other, alpha)


def prod(input, dim=None, keepdim=False, dtype=None):
    r"""
    Reduces a dimension of a tensor by multiplying all elements in the dimension, by default. And also can
    reduce a dimension of `input` along the `dim`. Determine whether the dimensions of the output and input are the
    same by controlling `keepdim`.
    
    Args:
        input (Tensor[Number]): The input tensor. The dtype of the tensor to be reduced is number.
            :math:`(N, *)` where :math:`*` means, any number of additional dimensions.
        dim (int): The dimensions to reduce. Default: ``None`` , reduce all dimensions.
            Only constant value is allowed. Assume the rank of `input` is r, and the value range is [-r,r).
        keepdim (bool): If ``True`` , keep these reduced dimensions and the length is 1.
            If ``False`` , don't keep these dimensions. Default: ``False`` .
        dtype (:class:`mindspore.dtype`): The desired data type of returned Tensor. Default: ``None`` .
    
    Returns:
        Tensor, has the same data type as input tensor.
    
        - If `dim` is ``None`` , and `keepdim` is  ``False`` ,
          the output is a 0-D tensor representing the product of all elements in the input tensor.
        - If `dim` is int, set as 1, and `keepdim` is  ``False`` ,
          the shape of output is :math:`(input_0, input_2, ..., input_R)`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `dim` is not one of the following: int or None.
        TypeError: If `keepdim` is not a bool.
        ValueError: If `dim` is out of range.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.random.randn(3, 4, 5, 6).astype(np.float32))
        >>> output = ops.prod_ext(x, 1, keepdim=True)
        >>> result = output.shape
        >>> print(result)
        (3, 1, 5, 6)
        >>> # case 1: Reduces a dimension by multiplying all elements in the dimension.
        >>> x = Tensor(np.array([[[1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]],
        ...                      [[4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [6, 6, 6, 6, 6, 6]],
        ...                      [[7, 7, 7, 7, 7, 7], [8, 8, 8, 8, 8, 8], [9, 9, 9, 9, 9, 9]]]), mindspore.float32)
        >>> output = ops.prod_ext(x)
        >>> print(output)
        2.2833798e+33
        >>> print(output.shape)
        ()
        >>> # case 2: Reduces a dimension along dim 0.
        >>> output = ops.prod_ext(x, 0, True)
        >>> print(output)
        [[[ 28.  28.  28.  28.  28.  28.]
        [ 80.  80.  80.  80.  80.  80.]
        [162. 162. 162. 162. 162. 162.]]]
        >>> # case 3: Reduces a dimension along dim 1.
        >>> output = ops.prod_ext(x, 1, True)
        >>> print(output)
        [[[  6.   6.   6.   6.   6.   6.]]
        [[120. 120. 120. 120. 120. 120.]]
        [[504. 504. 504. 504. 504. 504.]]]
        >>> # case 4: Reduces a dimension along dim 2.
        >>> output = ops.prod_ext(x, 2, True)
        >>> print(output)
        [[[1.00000e+00]
        [6.40000e+01]
        [7.29000e+02]]
        [[4.09600e+03]
        [1.56250e+04]
        [4.66560e+04]]
        [[1.17649e+05]
        [2.62144e+05]
        [5.31441e+05]]]
    """
    return prod_impl(input, dim, keepdim, dtype)


def logsumexp(input, dim, keepdim=False):
    r"""
    Computes the logarithm of the sum of exponentiations of all elements along the specified `dim` dimension of the `input` (with numerical stabilization), and retains the dimension based on the `keepdim` parameter.
    
    .. math::
    
        logsumexp(input) = \log(\sum(e^{input-input_{max}})) + input_{max}
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): Input Tensor.
        dim (Union[int, tuple(int), list(int)], optional): The dimension to be reduced (the value should be within `[0, len(input.shape) - 1]`), when the `dim` is `()`, all dimensions are reduced.
        keepdim (bool, optional): Whether the output tensor retains the dimension `dim`, default: `False`.
    
    Returns:
        Tensor, the dtype changes according to the `input.dtype`, and the shape changes according to the values of `dim` and `keepdim`.
    
        - If `input.dtype` is in [float16, float32, bfloat16], the output dtype is the same as the `input.dtype`.
        - If `input.dtype` is an integer or boolean type, the output dtype is float32.
        - If `dim` is (), and `keepdim` is False, the output is a 0-D tensor representing the logarithm of the sum of exponentiations of all elements in the `input` tensor.
        - If `dim` is `1`, and `keepdim` is False, the shape of output is :math:`(input.shape[0], input.shape[2], ..., input.shape[n])`.
        - If `dim` is `(1, 2)`, and `keepdim` is False, the shape of output is :math:`(input.shape[0], input.shape[3], ..., input.shape[n])`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not one of: bool, int8, int16, int32, int64, uint8, float16, float32, bfloat16.
        TypeError: If `dim` is not an int or tuple(int) or list(list).
        TypeError: If `keepdim` is not a bool.
        ValueError: If the value of any elements of `dim` is not in the range `[0, len(input.shape) - 1]`.
        RuntimeError: If any element of `dim` is repeated.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.random.randn(3, 4, 5, 6).astype(np.float32))
        >>> output = ops.auto_generate.logsumexp_ext(x, 1, keepdim=True)
        >>> print(output.shape)
        (3, 1, 5, 6)
    """
    return logsumexp_impl(input, dim, keepdim)


def ffn(x, weight1, weight2, expertTokens=None, bias1=None, bias2=None, scale=None, offset=None, deqScale1=None, deqScale2=None, antiquant_scale1=None, antiquant_scale2=None, antiquant_offset1=None, antiquant_offset2=None, activation='fastgelu', inner_precise=0):
    r"""
    None
    """
    return ffn_impl(x, weight1, weight2, expertTokens, bias1, bias2, scale, offset, deqScale1, deqScale2, antiquant_scale1, antiquant_scale2, antiquant_offset1, antiquant_offset2, converted_activation, inner_precise)


def diag(input, diagonal=0):
    r"""
    If input is a vector (1-D tensor), then returns a 2-D square tensor with the elements of input as the diagonal.
    
    If input is a matrix (2-D tensor), then returns a 1-D tensor with the diagonal elements of input.
    
    The argument diagonal controls which diagonal to consider:
    
    - If `diagonal` = 0, it is the main diagonal.
    
    - If `diagonal` > 0, it is above the main diagonal.
    
    - If `diagonal` < 0, it is below the main diagonal.
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): The input tensor.
        diagonal (int, optional): the diagonal to consider. Defaults: ``0``.
    
    Returns:
        Tensor, has the same dtype as the `input`, its shape is up to `diagonal`.
    
        - If `input` shape is :math:`(x_0)` : then output shape is :math:`(x_0 + \left | diagonal \right | , x_0 + \left | diagonal \right | )` 2-D Tensor.
    
        - If `input` shape is :math:`(x_0, x_1)` : then output shape is main diagonal to move :math:`(\left | diagonal \right |)` elements remains elements' length 1-D Tensor.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        ValueError: If shape of `input` is not 1-D and 2-D.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> from mindspore import Tensor, ops
        >>> input = Tensor([1, 2, 3, 4]).astype('int32')
        >>> output = ops.auto_generate.diag_ext(input)
        >>> print(output)
        [[1 0 0 0]
         [0 2 0 0]
         [0 0 3 0]
         [0 0 0 4]]
    """
    return diag_impl(input, diagonal)


def adaptive_avg_pool3d(input, output_size):
    r"""
    None
    """
    return adaptive_avg_pool3d_impl(input, output_size)


def mean(input, dim=None, keepdim=False, dtype=None):
    r"""
    Reduces all dimension of a tensor by averaging all elements in the dimension, by default.
    And reduce a dimension of `input` along the specified `dim`. `keepdim`
    determines whether the dimensions of the output and input are the same.
    
    Note:
        The `dim` with tensor type is only used for compatibility with older versions and is not recommended.
    
    Args:
        input (Tensor[Number]): The input tensor. The dtype of the tensor to be reduced is number.
            :math:`(N, *)` where :math:`*` means, any number of additional dimensions.
        dim (Union[int, tuple(int), list(int), Tensor]): The dimensions to reduce. Default: ``None`` ,
            reduce all dimensions. Only constant value is allowed. Assume the rank of `input` is r,
            and the value range is [-r,r).
        keepdim (bool): If ``True`` , keep these reduced dimensions and the length is 1.
            If ``False`` , don't keep these dimensions. Default: ``False`` .
        dtype (:class:`mindspore.dtype`): The desired data type of returned Tensor. Default: ``None`` .
    
    Returns:
        Tensor, has the same data type as input tensor.
    
        - If `dim` is ``None`` , and `keepdim` is ``False`` ,
          the output is a 0-D tensor representing the product of all elements in the input tensor.
        - If `dim` is int, set as 1, and `keepdim` is ``False`` ,
          the shape of output is :math:`(x_0, x_2, ..., x_R)`.
        - If `dim` is tuple(int), set as (1, 2), and `keepdim` is ``False`` ,
          the shape of output is :math:`(x_0, x_3, ..., x_R)`.
        - If `dim` is 1-D Tensor, set as [1, 2], and `keepdim` is ``False`` ,
          the shape of output is :math:`(x_0, x_3, ..., x_R)`.
    
    Raises:
        TypeError: If `x` is not a Tensor.
        TypeError: If `dim` is not one of the following: int, tuple, list or Tensor.
        TypeError: If `keepdim` is not a bool.
        ValueError: If `dim` is out of range.
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.random.randn(3, 4, 5, 6).astype(np.float32))
        >>> output = ops.mean_ext(x, 1, keepdim=True)
        >>> result = output.shape
        >>> print(result)
        (3, 1, 5, 6)
        >>> # case 1: Reduces a dimension by averaging all elements in the dimension.
        >>> x = Tensor(np.array([[[2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2]],
        ... [[4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [6, 6, 6, 6, 6, 6]],
        ... [[6, 6, 6, 6, 6, 6], [8, 8, 8, 8, 8, 8], [10, 10, 10, 10, 10, 10]]]),
        ... mindspore.float32)
        >>> output = ops.mean_ext(x)
        >>> print(output)
        5.0
        >>> print(output.shape)
        ()
        >>> # case 2: Reduces a dimension along the dim 0
        >>> output = ops.mean_ext(x, 0, True)
        >>> print(output)
        [[[4. 4. 4. 4. 4. 4.]
        [5. 5. 5. 5. 5. 5.]
        [6. 6. 6. 6. 6. 6.]]]
        >>> # case 3: Reduces a dimension along the dim 1
        >>> output = ops.mean_ext(x, 1, True)
        >>> print(output)
        [[[2. 2. 2. 2. 2. 2.]]
        [[5. 5. 5. 5. 5. 5.]]
        [[8. 8. 8. 8. 8. 8.]]]
        >>> # case 4: Reduces a dimension along the dim 2
        >>> output = ops.mean_ext(x, 2, True)
        >>> print(output)
        [[[ 2.]
        [ 2.]
        [ 2.]]
        [[ 4.]
        [ 5.]
        [ 6.]]
        [[ 6.]
        [ 8.]
        [10.]]]
    """
    return mean_impl(input, dim, keepdim, dtype)


def index_select(input, dim, index):
    r"""
    Generates a new Tensor that accesses the values of `input` along the specified `dim` dimension
    using the indices specified in `index`. The new Tensor has the same number of dimensions as `input`,
    with the size of the `dim` dimension being equal to the length of `index`, and the size of all other
    dimensions will be unchanged from the original `input` Tensor.
    
    .. note::
        The value of index must be in the range of `[0, input.shape[dim])`, the result is undefined out of range.
    
    Args:
        input (Tensor): The input Tensor.
        dim (int): The dimension to be indexed.
        index (Tensor): A 1-D Tensor with the indices.
    
    Returns:
        Tensor, has the same dtype as input Tensor.
    
    Raises:
        TypeError: If `input` or `index` is not a Tensor.
        TypeError: If `dim` is not int number.
        ValueError: If the value of `dim` is out the range of `[-input.ndim, input.ndim - 1]`.
        ValueError: If the dimension of `index` is not equal to 1.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> import numpy as np
        >>> input = Tensor(np.arange(16).astype(np.float32).reshape(2, 2, 4))
        >>> print(input)
        [[[ 0.  1.  2.  3.]
        [ 4.  5.  6.  7.]]
        [[ 8.  9. 10. 11.]
        [12. 13. 14. 15.]]]
        >>> index = Tensor([0,], mindspore.int32)
        >>> y = ops.auto_generate.index_select_ext(input, 1, index)
        >>> print(y)
        [[[ 0.  1.  2.  3.]]
        [[ 8.  9. 10. 11.]]]
    """
    return index_select_impl(input, dim, index)


def selu(input):
    r"""
    Activation function SELU (Scaled exponential Linear Unit).
    
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
    
    SELU Activation Function Graph:
    
    .. image:: ../images/SeLU.png
        :align: center
    
    Args:
        input (Tensor): Tensor of any dimension.
            The data type is float16, float32, bfloat16.
    
    Returns:
        Tensor, with the same type and shape as the `input`.
    
    Raises:
        TypeError: If dtype of `input` is not float16, float32, bfloat16.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> import numpy as np
        >>> input = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> output = ops.auto_generate.selu_ext(input)
        >>> print(output)
        [[-1.1113307 4.202804 -1.7575096]
         [ 2.101402 -1.7462534 9.456309 ]]
    """
    return selu_impl(input)


def topk(input, k, dim=-1, largest=True, sorted=True):
    r"""
    Finds values and indices of the `k` largest or smallest entries along a given dimension.
    
    .. warning::
        - If sorted is set to False, due to different memory layout and traversal methods on different platforms,
          the display order of calculation results may be inconsistent when `sorted` is False.
    
    If the `input` is a one-dimensional Tensor, finds the `k` largest  or smallest entries in the Tensor,
    and outputs its value and index as a Tensor. values[`k`] is the `k` largest item in `input`,
    and its index is indices [`k`].
    
    For a multi-dimensional matrix,
    calculates the first or last `k` entries in a given dimension, therefore:
    
    .. math::
    
        values.shape = indices.shape
    
    If the two compared elements are the same, the one with the smaller index value is returned first.
    
    Args:
        input (Tensor): Input to be computed.
        k (int): The number of top or bottom elements to be computed along the last dimension.
        dim (int, optional): The dimension to sort along. Default: ``-1`` .
        largest (bool, optional): If largest is ``False``  then the k smallest elements are returned.
            Default: ``True`` .
        sorted (bool, optional): If ``True`` , the obtained elements will be sorted by the values in descending
            order or ascending order according to `largest`. If ``False`` , the obtained elements will not be
            sorted. Default: ``True`` .
    
    Returns:
        A tuple consisting of `values` and `indices`.
    
        - values (Tensor) - The `k` largest or smallest elements in each slice of the given dimension.
        - indices (Tensor) - The indices of values within the last dimension of input.
    
    Raises:
        TypeError: If `sorted` is not a bool.
        TypeError: If `input` is not a Tensor.
        TypeError: If `k` is not an int.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore as ms
        >>> from mindspore import ops
        >>> x = ms.Tensor([[0.5368, 0.2447, 0.4302, 0.9673],
        ...                [0.4388, 0.6525, 0.4685, 0.1868],
        ...                [0.3563, 0.5152, 0.9675, 0.8230]], dtype=ms.float32)
        >>> output = ops.topk_ext(x, 2, dim=1)
        >>> print(output)
        (Tensor(shape=[3, 2], dtype=Float32, value=
        [[ 9.67299998e-01,  5.36800027e-01],
         [ 6.52499974e-01,  4.68499988e-01],
         [ 9.67499971e-01,  8.23000014e-01]]), Tensor(shape=[3, 2], dtype=Int64, value=
        [[3, 0],
         [1, 2],
         [2, 3]]))
        >>> output2 = ops.topk_ext(x, 2, dim=1, largest=False)
        >>> print(output2)
        (Tensor(shape=[3, 2], dtype=Float32, value=
        [[ 2.44700000e-01,  4.30200011e-01],
         [ 1.86800003e-01,  4.38800007e-01],
         [ 3.56299996e-01,  5.15200019e-01]]), Tensor(shape=[3, 2], dtype=Int64, value=
        [[1, 2],
         [3, 0],
         [0, 1]]))
    """
    return topk_impl(input, k, dim, largest, sorted)


def outer(input, vec2):
    r"""
    Return outer product of `input` and `vec2`. If `input` is a vector of size :math:`n`
    and `vec2` is a vector of size :math:`m` , then output must be a matrix of shape :math:`(n, m)` .
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    .. note::
        This function does not broadcast.
    
    Args:
        input (Tensor): 1-D input vector.
        vec2 (Tensor): 1-D input vector.
    
    Returns:
        out, 2-D matrix, the outer product of two vectors.
    
    Raises:
        TypeError: If `input` or `vec2` is not a Tensor.
        TypeError: The implicitly converted data types of `input` and `vec2` are not one of float16, float32, float64, bool, uint8, int8, int16, int32, int64, complex64, complex128, bfloat16
        ValueError: If the dimension of `input` or `vec2` is not equal to 1.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> input = Tensor(np.array([7, 8, 9]), mindspore.int32)
        >>> vec2 = Tensor(np.array([7, 10, 11]), mindspore.int32)
        >>> out = ops.outer(input, vec2)
        >>> print(out)
        [[49 70 77]
         [56 80 88]
         [63 90 99]]
    """
    return outer_impl(input, vec2)


def logaddexp(input, other):
    r"""
    Computes the logarithm of the sum of exponentiations of the inputs.
    This function is useful in statistics where the calculated probabilities of events may be
    so small as to exceed the range of normal floating point numbers.
    
    .. math::
    
        out_i = \log(exp(input_i) + \exp(other_i))
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): Input Tensor. The dtype of `input` must be float.
        other (Tensor): Input Tensor. The dtype of `other` must be float.
            If the shape of `input` is not equal to the shape of `other`,
            they must be broadcastable to a common shape.
    
    Returns:
        Tensor, with the same dtype as `input` and `other`.
    
    Raises:
        TypeError: If `input` or `other` is not a Tensor.
        TypeError: The dtype of `input` or `other` is not float.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x1 = Tensor(np.array([1, 2, 3]).astype(np.float16))
        >>> x2 = Tensor(np.array(2).astype(np.float16))
        >>> output = ops.logaddexp_ext(x1, x2)
        >>> print(output)
        [2.312 2.693 3.312]
    """
    return logaddexp_impl(input, other)


def trace(input):
    r"""
    Returns a new tensor that is the sum of the `input` main trace.
    
    Args:
        input (Tensor): 2-D Tensor.
    
    Returns:
        Tensor, when the data type of `input` is integer or bool, its data type is int64, otherwise it is the same as `input`, and size equals to 1.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        ValueError: If the dimension of `input` is not equal to 2.
        TypeError:  If the dtype of `input` is not one of float16, float32, float64, bool, uint8, int8, int16, int32, int64, complex64, complex128, bfloat16.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[10, 11, 12], [13, 14, 15], [16, 17, 18]]), mindspore.float32)
        >>> output = ops.trace_ext(input)
        >>> print(output)
        42.0
        >>> input = Tensor(np.arange(1, 13).reshape(3, 4), mindspore.float32)
        >>> output = ops.trace_ext(input)
        >>> print(output)
        18.0
        >>> input = Tensor(np.arange(12, 0, -1).reshape(4, 3), mindspore.float32)
        >>> output = ops.trace_ext(input)
        >>> print(output)
        24.0
    """
    return trace_impl(input)


def t(input):
    r"""
    Transpose the input tensor.
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): The input tensor.
    
    Returns:
        Tensor, transpose 2D tensor, return 1D tensor as it is.
    
    Raises:
        ValueError: If the dimension of `input` is greater than 2.
        ValueError: If `input` is empty.
        TypeError: If `input` is not a tensor.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[1, 2, 3], [4, 5, 6]]), mindspore.float32)
        >>> output = ops.t_ext(input)
        >>> print(output)
        [[ 1. 4.]
         [ 2. 5.]
         [ 3. 6.]]
    """
    return t_impl(input)


def adaptive_avg_pool2d_grad(grad_output, x):
    r"""
    None
    """
    return adaptive_avg_pool2d_grad_impl(grad_output, x)


def argmax(input, dim=None, keepdim=False):
    r"""
    argmax(input) -> Tensor
    
    Return the indices of the maximum values of a tensor.
    
    Args:
        input (Tensor): Input tensor.
    
    Returns:
        Tensor.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> x = Tensor(np.array([[1, 20, 5], [67, 8, 9], [130, 24, 15]]).astype(np.float32))
        >>> output = ops.auto_generate.argmax_ext(x)
        >>> print(output)
        6
    
    .. function:: argmax(input, dim, keepdim=False) -> Tensor
        :noindex:
    
    Return the indices of the maximum values of a tensor across a dimension.
    
    Args:
        input (Tensor): Input tensor.
        dim (int): The dimension to reduce. 
        keepdim (bool, optional): Whether the output tensor retains the specified
            dimension. Default: ``False`` .
    
    Returns:
        Tensor, indices of the maximum values across a dimension.
    
    Raises:
        TypeError: If `keepdim` is not bool.
        ValueError: If `dim` is out of range.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> from mindspore import ops
        >>> x = Tensor(np.array([[1, 20, 5], [67, 8, 9], [130, 24, 15]]).astype(np.float32))
        >>> output = ops.auto_generate.argmax_ext(x, dim=-1)
        >>> print(output)
        [1 0 0]
    """
    return argmax_impl(input, dim, keepdim)


def bincount(input, weights=None, minlength=0):
    r"""
    Count the occurrences of each value in the input.
    
    If `minlength` is not specified, the length of the output Tensor is the maximum value in the input plus one.
    If `minlength` is specified, the length of the output Tensor is the maximum value between `minlength` or
    the maximum value in the input plus one.
    
    Each value in the output Tensor represents the number of occurrences of that index value in the input.
    If `weights` is specified, the output results are weighted, 
    i.e., :math:`out[n] += weight[i]` instead of :math:`out[n] += 1`.
    
    .. warning::
        This is an experimental API that is subject to change or deletion.
    
    Args:
        input (Tensor): A one-dimensional Tensor.
        weights (Tensor, optional): Weights with the same shape as the input. Default: ``None``.
        minlength (int, optional): The minimum length of output Tensor. Should be non-negative. Default: ``0``.
    
    Returns:
        Tensor, If input is non-empty, the output shape is :math:`(max(max(input)+1, minlength), )`,
        otherwise the shape is :math:`(0, )`.
    
    Raises:
        TypeError: If `input` or `weights` is not a Tensor.
        ValueError: If `input` contains negative values.
        ValueError: If `input` is not one-dimensional or `input` and `weights` do not have the same shape.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> from mindspore import ops, Tensor
        >>> print(ops.auto_generate.bincount_ext(Tensor(np.arange(5))))
        [1 1 1 1 1]
        >>> print(ops.auto_generate.bincount_ext(Tensor(np.array([0, 1, 1, 3, 2, 1, 7]))))
        [1 3 1 1 0 0 0 1]
        >>> w = Tensor(np.array([0.3, 0.5, 0.2, 0.7, 1., -0.6])) # weights
        >>> x = Tensor(np.array([0, 1, 1, 2, 2, 2]))
        >>> print(ops.auto_generate.bincount_ext(x,  weights=w, minlength=5))
        [0.3 0.7 1.1 0.  0. ]
    """
    return bincount_impl(input, weights, minlength)


def fold(input, output_size, kernel_size, dilation=1, padding=0, stride=1):
    r"""
    Combines an array of sliding local blocks into a large containing tensor.
    
    Consider a batched input tensor of shape :math:`(N, C \times \prod(\text{kernel_size}), L)` ,
    where :math:`N` is the batch dimension, :math:`C \times \prod(\text{kernel_size})` is the
    total number of values within each block (a block has :math:`\prod(\text{kernel_size})` spatial
    locations each containing a `C`-channeled vector), and :math:`L` is the total number of such blocks:
    
    .. math::
        L = \prod_d \left\lfloor\frac{\text{output_size}[d] + 2 \times \text{padding}[d] %
            - \text{dilation}[d] \times (\text{kernel_size}[d] - 1) - 1}{\text{stride}[d]} + 1\right\rfloor,
    
    where :math:`d` is over all spatial dimensions.
    
    Therefore, `output_size` is the spatial shape of the large containing tensor of the sliding local blocks.
    
    The `dilation`, `padding` and `stride` arguments specify how the sliding blocks are retrieved.
    
    .. warning::
        Currently, only unbatched(3D) or batched(4D) image-like output tensors are supported.
    
    Args:
        input (Tensor): 2-D or 3-D Tensor.
        output_size (Union[int, tuple[int], list[int]]): The shape of the spatial dimensions of
            the output(i.e., output.shape[2:]).
        kernel_size (Union[int, tuple[int], list[int]]): The size of the kernel, should be two int
            for height and width. If type is int, it means that height equal with width. Must be specified.
        dilation (Union[int, tuple[int], list[int]], optional): The size of the dilation, should be two int
            for height and width. If type is int, it means that height equal with width. Default: ``1`` .
        padding (Union[int, tuple[int], list[int]], optional): The size of the padding, should be two int
            for height and width. If type is int, it means that height equal with width. Default: ``0`` .
        stride (Union[int, tuple[int], list[int]], optional): The size of the stride, should be two int
            for height and width. If type is int, it means that height equal with width. Default: ``1`` .
    
    Returns:
        A Tensor, with same type as `input` .
    
    Shape:
        - Input: :math:`(N, C \times \prod(\text{kernel_size}), L)` or
          :math:`(C \times \prod(\text{kernel_size}), L)`
        - Output: :math:`(N, C, output\_size[0], output\_size[1], ...)` or
          :math:`(C, output\_size[0], output\_size[1], ...)`
    
    Raises:
        TypeError: If `output_size`, `kernel_size`, `stride`, `dilation`, `padding` data type is not int, tuple or list.
        ValueError: If `output_size`, `kernel_size`, `dilation`, `stride` value is not
            greater than zero or elements number invalid.
        ValueError: If `padding` value is less than zero or elements number invalid.
        ValueError: If input.shape[-2] can't be divisible by the product of kernel_size.
        ValueError: If `input.shape[-1]` is not equal to the calculated number of sliding blocks `L`.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.random.rand(16, 64, 25).astype(np.float32))
        >>> output = ops.auto_generate.fold_ext(x, (8, 8), [2, 2], [2, 2], [2, 2], [2, 2])
        >>> print(output.shape)
        (16, 16, 8, 8)
    """
    return fold_impl(input, converted_output_size, converted_kernel_size, converted_dilation, converted_padding, converted_stride)


def elu(input, alpha=1.0):
    r"""
    Exponential Linear Unit activation function.
    
    Applies the exponential linear unit function element-wise.
    The activation function is defined as:
    
    .. math::
    
        \text{ELU}(x)= \left\{
        \begin{array}{align}
            \alpha(e^{x}  - 1) & \text{if } x \le 0\\
            x & \text{if } x \gt 0\\
        \end{array}\right.
    
    Where :math:`x` is the element of input Tensor `input`, :math:`\alpha` is param `alpha`,
    it determines the smoothness of ELU.
    
    ELU function graph:
    
    .. image:: ../images/ELU.png
        :align: center
    
    Args:
        input (Tensor): The input of ELU is a Tensor of any dimension.
        alpha (float, optional): The alpha value of ELU, the data type is float.
            Default: ``1.0`` .
    
    Returns:
        Tensor, has the same shape and data type as `input`.
    
    Raises:
        TypeError: If `alpha` is not a float.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> output = ops.auto_generate.elu_ext(x)
        >>> print(output)
        [[-0.63212055  4.         -0.99966455]
         [ 2.         -0.99326205  9.        ]]
    """
    return elu_impl(input, alpha)


def mse_loss(input, target, reduction='mean'):
    r"""
    Calculates the mean squared error between the predicted value and the label value.
    
    For detailed information, please refer to :class:`mindspore.nn.MSELoss`.
    
    Args:
        input (Tensor): Tensor of any dimension. The data type needs to be consistent with the `target`.
            It should also be broadcastable with the `target`.
        target (Tensor): The input label. Tensor of any dimension. The data type needs to be consistent with the `input`.
            It should also be broadcastable with the `input`.
        reduction (str, optional): Apply specific reduction method to the output: ``'mean'`` , ``'none'`` ,
            ``'sum'`` . Default: ``'mean'`` .
    
            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output.
            - ``'sum'``: the output elements will be summed.
    
    Returns:
        - Tensor. If `reduction` is ``'mean'`` or ``'sum'``, the shape of output is `Tensor Scalar`.
        - If reduction is ``'none'``, the shape of output is the broadcasted shape of **input** and **target** .
    
    Raises:
        ValueError: If `reduction` is not one of ``'mean'`` , ``'sum'`` or ``'none'``.
        ValueError: If `input` and `target` are not broadcastable.
        TypeError: If `input` and `target` are in different data type.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> logits = Tensor(np.array([1, 2, 3]), mindspore.float32)
        >>> labels = Tensor(np.array([[1, 1, 1], [1, 2, 2]]), mindspore.float32)
        >>> output = ops.mse_loss_ext(logits, labels, reduction='none')
        >>> print(output)
        [[0. 1. 4.]
         [0. 0. 1.]]
    """
    return mse_loss_impl(input, target, converted_reduction)


def leaky_relu(input, negative_slope=0.01):
    r"""
    leaky_relu activation function. The element of `input` less than 0 times `negative_slope` .
    
    The activation function is defined as:
    
    .. math::
        \text{leaky_relu}(input) = \begin{cases}input, &\text{if } input \geq 0; \cr
        \text{negative_slope} * input, &\text{otherwise.}\end{cases}
    
    where :math:`negative\_slope` represents the `negative_slope` parameter.
    
    For more details, see `Rectifier Nonlinearities Improve Neural Network Acoustic Models
    <https://ai.stanford.edu/~amaas/papers/relu_hybrid_icml2013_final.pdf>`_.
    
    LeakyReLU Activation Function Graph:
    
    .. image:: ../images/LeakyReLU.png
        :align: center
    
    Args:
        input (Tensor): The input of leaky_relu is a Tensor of any dimension.
        negative_slope (Union[int, float], optional): Slope of the activation function when the element of `input` is less than 0.
          Default: ``0.01`` .
    
    Returns:
        Tensor, has the same type and shape as the `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `negative_slope` is not a float or an int.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([[-1.0, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> print(ops.extend.leaky_relu_ext(input, negative_slope=0.2))
        [[-0.2  4.  -1.6]
         [ 2.  -1.   9. ]]
    """
    return leaky_relu_impl(input, negative_slope)


def l1_loss(input, target, reduction='mean'):
    r"""
    Calculate the mean absolute error between the `input` value and the `target` value.
    
    Assuming that the :math:`x` and :math:`y` are the predicted value and target value,
    both are one-dimensional tensors of length :math:`N`, length :math:`N`, `reduction` is set to ``'none'`` ,
    then calculate the loss of :math:`x` and :math:`y` without dimensionality reduction.
    
    The formula is as follows:
    
    .. math::
        \ell(x, y) = L = \{l_1,\dots,l_N\}^\top, \quad \text{with } l_n = \left| x_n - y_n \right|,
    
    where :math:`N` is the batch size.
    
    If `reduction` is ``'mean'`` or ``'sum'`` , then:
    
    .. math::
        \ell(x, y) =
        \begin{cases}
            \operatorname{mean}(L), & \text{if reduction} = \text{'mean';}\\
            \operatorname{sum}(L),  & \text{if reduction} = \text{'sum'.}
        \end{cases}
    
    Args:
        input (Tensor): Predicted value, Tensor of any dimension.
        target (Tensor): Target value, usually has the same shape as the `input`.
            If `input` and `target` have different shapes, make sure they can broadcast to each other.
        reduction (str, optional): Apply specific reduction method to the output: ``'none'`` , ``'mean'`` ,
            ``'sum'`` . Default: ``'mean'`` .
    
            - ``'none'``: no reduction will be applied.
            - ``'mean'``: compute and return the mean of elements in the output. Notice: At least one of the input and target is float type when the reduction is ``'mean'`` .
            - ``'sum'``: the output elements will be summed.
    
    Returns:
        Tensor or Scalar, if `reduction` is ``'none'`` , return a Tensor with same shape and dtype as `input`.
        Otherwise, a scalar value will be returned.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `target` is not a Tensor.
        ValueError: If `reduction` is not one of ``'none'`` , ``'mean'`` or ``'sum'`` .
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> from mindspore import Tensor, ops
        >>> from mindspore import dtype as mstype
        >>> x = Tensor([[1, 2, 3], [4, 5, 6]], mstype.float32)
        >>> target = Tensor([[6, 5, 4], [3, 2, 1]], mstype.float32)
        >>> output = ops.l1_loss_ext(x, target, reduction="mean")
        >>> print(output)
        3.0
    """
    return l1_loss_impl(input, target, converted_reduction)


def mish(input):
    r"""
    Computes MISH (A Self Regularized Non-Monotonic Neural Activation Function)
    of input tensors element-wise.
    
    The formula is defined as follows:
    
    .. math::
        \text{mish}(input) = input * \tanh(softplus(\text{input}))
    
    See more details in `A Self Regularized Non-Monotonic Neural Activation Function 
    <https://arxiv.org/abs/1908.08681>`_.
    
    Mish Activation Function Graph:
    
    .. image:: ../images/Mish.png
        :align: center
    
    Args:
        input (Tensor): The input of MISH. Supported dtypes: 
    
            - Ascend: float16, float32.
    
    Returns:
        Tensor, has the same type and shape as the `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If dtype of `input` is not float16 or float32.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, ops
        >>> import numpy as np
        >>> x = Tensor(np.array([[-1.1, 4.0, -8.0], [2.0, -5.0, 9.0]]), mindspore.float32)
        >>> output = ops.mish(x)
        >>> print(output)
        [[-3.0764845e-01 3.9974124e+00 -2.6832507e-03]
         [ 1.9439589e+00 -3.3576239e-02 8.9999990e+00]]
    """
    return mish_impl(input)


def cummin(input, dim):
    r"""
    Returns a tuple (values, indices) where `values` is the cumulative minimum value of input Tensor `input`
    along the dimension `dim`, and `indices` is the index location of each minimum value.
    
    .. math::
        \begin{array}{ll} \\
            y_{i} = \min(x_{1}, x_{2}, ... , x_{i})
        \end{array}
    
    .. note::
        GE backend is not supported in Ascend.
    
    Args:
        input (Tensor): The input Tensor, The dimension must be greater than 0.
        dim (int): Operation dimension. The value of `dim` must be in the range `[-input.ndim, input.ndim - 1]`.
    
    Returns:
        tuple [Tensor], tuple of 2 Tensors, containing the cumulative minimum of elements and the index.
        The shape of each output tensor is the same as that of input `input`.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `input` is a Tensor, but the type is complex or bool.
        TypeError: If `dim` is not an int.
        ValueError: If `dim` is out the range of `[-input.ndim, input.ndim - 1]`.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> from mindspore import Tensor, ops
        >>> import mindspore
        >>> a = Tensor([-0.2284, -0.6628,  0.0975,  0.2680, -1.3298, -0.4220], mindspore.float32)
        >>> output = ops.cummin_ext(a, dim=0)
        >>> print(output[0])
        [-0.2284 -0.6628 -0.6628 -0.6628 -1.3298 -1.3298]
        >>> print(output[1])
        [0 1 1 1 4 4]
    """
    return cummin_impl(input, dim)


def atan2(input, other):
    r"""
    Returns arctangent of input/other element-wise.
    
    It returns :math:`\theta\ \in\ [-\pi, \pi]`
    such that :math:`input = r*\sin(\theta), other = r*\cos(\theta)`, where :math:`r = \sqrt{input^2 + other^2}`.
    
    Note:
        - Arg `input` and `other` comply with the implicit type conversion rules to make the data types consistent.
          If they have different data types, the lower precision data type will be converted to relatively the
          highest precision data type.
    
    Args:
        input (Tensor, Number.number): The input tensor or scalar.
        other (Tensor, Number.number): The input tensor or scalar. It has the same shape with `input` or
            its shape is able to broadcast with `input`.
    
    Returns:
        Tensor, the shape is the same as the one after broadcasting.
        The dtype of output is float32 when dtype of `input` is in
        [bool, int8, uint8, int16, int32, int64]. Otherwise output has the same dtype as `input`.
    
    Raises:
        TypeError: If `input` or `other` is not a Tensor or scalar.
        RuntimeError: If the data type of `input` and `other` conversion of Parameter is required
                    when data type conversion of Parameter is not supported.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input = Tensor(np.array([0, 1]), mindspore.float32)
        >>> other = Tensor(np.array([1, 1]), mindspore.float32)
        >>> output = ops.auto_generate.atan2_ext(input, other)
        >>> print(output)
        [0.        0.7853982]
    """
    return atan2_impl(input, other)


def inplace_add(input, other, alpha=1):
    r"""
    None
    """
    return inplace_add_impl(input, other, alpha)


def flatten(input, start_dim=0, end_dim=-1):
    r"""
    Flatten a tensor along dimensions from `start_dim` to `end_dim`.
    
    Args:
        input (Tensor): The input Tensor.
        start_dim (int, optional): The first dimension to flatten. Default: ``0`` .
        end_dim (int, optional): The last dimension to flatten. Default: ``-1`` .
    
    Returns:
        Tensor. If no dimensions are flattened, returns the original `input`, otherwise return the flattened Tensor.
        If `input` is a 0-dimensional Tensor, a 1-dimensional Tensor will be returned.
    
    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `start_dim` or `end_dim` is not int.
        ValueError: If `start_dim` is greater than `end_dim` after canonicalized.
        ValueError: If `start_dim` or `end_dim` is not in range of [-input.dim, input.dim-1].
    
    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> input_x = Tensor(np.ones(shape=[1, 2, 3, 4]), mindspore.float32)
        >>> output = ops.auto_generate.flatten_ext(input_x)
        >>> print(output.shape)
        (24,)
    """
    return flatten_impl(input, start_dim, end_dim)


def sort(input, dim=-1, descending=False, stable=False):
    r"""
    None
    """
    return sort_impl(input, dim, descending, stable)


def log10(input):
    r"""
    Returns the logarithm to the base 10 of a tensor element-wise.
    
    .. math::
        y_i = \log_{10}(x_i)
    
    .. warning::
        - This is an experimental API that is subject to change or deletion.
        - If the input value of operator Log10 is within the range (0, 0.01] or [0.95, 1.05], the output accuracy
          may be affacted.
    
    Args:
        input (Tensor): Input Tensor of any dimension. The value must be greater than 0.
    
    Returns:
        Tensor, has the same shape as the `input`, and the dtype changes according to the `input.dtype`.
        
        - if `input.dtype` is in [float16, float32, float64, bfloat16], the output dtype is the same as the `input.dtype`.
        - if `input.dtype` is integer or boolean type, the output dtype is float32.
    
    Raises:
        TypeError: If `input` is not a Tensor.
    
    Supported Platforms:
        ``Ascend``
    
    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor, ops
        >>> x = Tensor(np.array([3.0, 5.0, 7.0]), mindspore.float32)
        >>> output = ops.auto_generate.log10_ext(x)
        >>> print(output)
        [0.47712136 0.69897    0.845098  ]
    """
    return log10_impl(input)

