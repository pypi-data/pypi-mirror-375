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
"""Add docstrings to Tensor functions"""
from mindspore.common.tensor import Tensor
from mindspore._c_expression import _add_docstr as add_docstr


def attach_docstr(method, docstr):
    try:
        add_docstr(getattr(Tensor, method), docstr)
    except Exception as e:
        raise AttributeError(
            f"Failed to attach docstring to Tensor.{method}.\n"
            f"Please check if there is a duplicate Tensor.{method} in tensor.py."
        )

attach_docstr("cosh", r"""cosh() -> Tensor

For details, please refer to :func:`mindspore.ops.cosh`.""")
attach_docstr("isinf", r"""isinf() -> Tensor

For details, please refer to :func:`mindspore.ops.isinf`.

Supported Platforms:
    ``Ascend`` ``CPU`` ``GPU``""")
attach_docstr("view_as", r"""view_as(other) -> Tensor

View `self` Tensor as the same shape as `other` .

Args:
    other(Tensor): The returned Tensor has the same shape as `other`.

Returns:
    Tensor, has the same shape as `other`.

Raises:
    TypeError: If `other` is not a Tensor.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> from mindspore import Tensor
    >>> from mindspore import dtype as mstype
    >>> a = Tensor([[1, 2, 3], [2, 3, 4]], mstype.float32)
    >>> b = Tensor([1, 1, 1, 1, 1, 1], mstype.float32)
    >>> output = a.view_as(b)
    >>> print(output)
    [1. 2. 3. 2. 3. 4.]
""")
attach_docstr("bitwise_xor", r"""bitwise_xor(other) ->Tensor

Returns bitwise `xor` of two tensors element-wise.

Note:
    `self` and `other` comply with the type conversion rules to make the data types consistent.

Args:
    other (Tensor, Number.number): The shape is the same as the `self` or can be broadcast to the shape of `self`.

Returns:
    Tensor, has the same type as the `self` and has the same shape as after broadcasting.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([0, 0, 1, -1, 1, 1, 1]), mindspore.int16)
    >>> other = Tensor(np.array([0, 1, 1, -1, -1, 2, 3]), mindspore.int16)
    >>> output = input.bitwise_xor(other)
    >>> print(output)
    [ 0  1  0  0 -2  3  2]
""")
attach_docstr("std", r"""std(axis=None, ddof=0, keepdims=False) -> Tensor

For details, please refer to :func:`mindspore.ops.std`.

.. method:: Tensor.std(dim=None, *, correction=1, keepdim=False) -> Tensor
    :noindex:

Calculates the standard deviation over the dimensions specified by `dim`. `dim` can be a single dimension, list of
dimensions, or None to reduce over all dimensions.

The standard deviation (:math:`\sigma`) is calculated as:

.. math::
    \sigma =\sqrt{\frac{1}{N-\delta N}\sum_{j-1}^{N-1}\left(s e l f_{i j}-\overline{x_{i}}\right)^{2}}

where :math:`x` is the sample set of elements, :math:`\bar{x}` is the sample mean, :math:`N` is the number
of samples and :math:`\delta N` is the `correction`.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    dim (None, int, tuple(int), optional): The dimension or dimensions to reduce. Defaults to ``None``.
        If ``None``, all dimensions are reduced.

Keyword Args:
    correction (int, optional): The difference between the sample size and sample degrees of freedom. Defaults
        to Bessel's correction. Defaults to ``1``.
    keepdim (bool, optional): Whether the output tensor has dim retained or not. If ``True`` , keep these
        reduced dimensions and the length is 1. If ``False``, don't keep these dimensions. Defaults to ``False``.

Returns:
    Tensor, the standard deviation.
    Suppose the shape of `self` is :math:`(x_0, x_1, ..., x_R)`:

    - If `dim` is () and `keepdim` is set to ``False`` , returns a 0-D Tensor, indicating the standard deviation of
      all elements in `self`.
    - If `dim` is int, e.g. ``1`` and `keepdim` is set to ``False`` , then the returned Tensor has shape
      :math:`(x_0, x_2, ..., x_R)`.
    - If `dim` is tuple(int) or list(int), e.g. ``(1, 2)`` and `keepdim` is set to ``False`` , then the returned
      Tensor has shape :math:`(x_0, x_3, ..., x_R)`.

Raises:
    TypeError: If `self` is not a Tensor.
    TypeError: If `self` is not in bfloat16, float16, float32.
    TypeError: If `dim` is not one of the followings: None, int, tuple.
    TypeError: If `correction` is not an int.
    TypeError: If `keepdim` is not a bool.
    ValueError: If `dim` is out of range :math:`[-self.ndim, self.ndim)`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import mint, Tensor
    >>> input = Tensor(np.array([[1, 2, 3], [-1, 1, 4]]).astype(np.float32))
    >>> output = input.std(dim=1, correction=1, keepdim=False)
    >>> print(output)
    [1.      2.5166113]
""")
attach_docstr("masked_fill", r"""masked_fill(mask, value) -> Tensor

For details, please refer to :func:`mindspore.ops.masked_fill`.""")
attach_docstr("log", r"""log() -> Tensor

For details, please refer to :func:`mindspore.ops.log`.
""")
attach_docstr("arccosh", r"""arccosh() -> Tensor

Alias for :func:`mindspore.Tensor.acosh`.
""")
attach_docstr("neg", r"""neg() -> Tensor

For details, please refer to :func:`mindspore.ops.neg`.
""")
attach_docstr("new_empty", r"""new_empty(size, *, dtype=None, device=None) -> Tensor

Returns an uninitialized Tensor. Its shape is specified by `size`, its dtype is specified by `dtype` and its
device is specified by `device`.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    size (Union[tuple[int], list[int], int]): The specified shape of output tensor. Only positive integer or
        tuple or list containing positive integers are allowed.

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The specified dtype of the output tensor. If `dtype = None`,
        the tensor will have the same dtype as `self`. Default ``None``.
    device (string, optional): The specified device of the output tensor. In PyNative mode, ``"Ascend"``, ``"npu"``,
        ``"cpu"`` and ``"CPU"`` are supported. In graph mode O0, ``"Ascend"`` and ``"npu"`` are supported. If `device = None`,
        the value set by :func:`mindspore.set_device` will be used. Default ``None``.

Returns:
    Tensor, whose shape, dtype and device are defined by input but with uninitialized data (May be a random value).

Raises:
    TypeError: If `size` is neither an int nor a tuple or list of int.

Supported Platforms:
    ``Ascend`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> x = Tensor([[1, 2, 3], [4, 5, 6]])
    >>> output1 = x.new_empty((2, 3))
    >>> print(output1)
    [[0 0 0]
     [0 0 0]]
    >>> output2 = x.new_empty((2, 3), dtype=mindspore.float64)
    >>> print(output2)
    [[0. 0. 0.]
     [0. 0. 0.]]
""")
attach_docstr("flatten", r"""flatten(start_dim=0, end_dim=-1) -> Tensor

Flatten a tensor along dimensions from `start_dim` to `end_dim`.

Args:
    start_dim (int, optional): The first dimension to flatten. Default: ``0`` .
    end_dim (int, optional): The last dimension to flatten. Default: ``-1`` .

Returns:
    Tensor. If no dimensions are flattened, returns the original `self`, otherwise return the flattened Tensor.
    If `self` is a 0-dimensional Tensor, a 1-dimensional Tensor will be returned.

Raises:
    TypeError: If `start_dim` or `end_dim` is not int.
    ValueError: If `start_dim` is greater than `end_dim` after canonicalized.
    ValueError: If `start_dim` or `end_dim` is not in range of [-self.dim, self.dim-1].

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.ones(shape=[1, 2, 3, 4]), mindspore.float32)
    >>> output = input_x.flatten(0, -1)
    >>> print(output.shape)
    (24,)

.. method:: Tensor.flatten(order='C', *, start_dim=0, end_dim=-1) -> Tensor
    :noindex:

Flatten a tensor along dimensions from `start_dim` to `start_dim`.

Args:
    order (str, optional): Only ``'C'`` and ``'F'`` are supported.
        ``'C'`` means to flatten in row-major (C-style) order.
        ``'F'`` means to flatten in column-major (Fortran-style) order. Default: ``'C'`` .

Keyword Args:
    start_dim (int, optional): The first dimension to flatten. Default: ``0`` .
    end_dim (int, optional): The last dimension to flatten. Default: ``-1`` .

Returns:
    Tensor. If no dimensions are flattened, returns the original `self`, otherwise return the flattened Tensor.
    If `self` is a 0-dimensional Tensor, a 1-dimensional Tensor will be returned.

Raises:
    TypeError: If `order` is not string type.
    ValueError: If `order` is string type, but not ``'C'`` or ``'F'``.
    TypeError: If `start_dim` or `end_dim` is not int.
    ValueError: If `start_dim` is greater than `end_dim` after canonicalized.
    ValueError: If `start_dim` or `end_dim` is not in range of [-self.dim, self.dim-1].

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.ones(shape=[1, 2, 3, 4]), mindspore.float32)
    >>> output = input_x.flatten(order='C')
    >>> print(output.shape)
    (24,)
""")
attach_docstr("median", r"""median(axis=-1, keepdims=False) -> tuple[Tensor]

Computes the median and indices of input tensor.

.. warning::
    - `indices` does not necessarily contain the first occurrence of each median value found in the `input`,
      unless it is unique. The specific implementation of this API is device-specific.
      The results may be different on CPU and GPU.

Args:
    axis (int, optional): Specify the axis for calculation. Default: ``-1`` .
    keepdims (bool, optional): Whether the output tensor need to retain `axis` dimension or not.
        Default: ``False`` .

Returns:
    - y (Tensor) - Returns the median value along the specified dimension.
      And It has the same dtype as the `input`.

    - indices (Tensor) - The index of the median. And the dtype is int64.

Raises:
    TypeError: If `axis` is not an int.
    TypeError: If `keepdims` is not a bool.
    ValueError: If `axis` is not in range of [-x.dim, x.dim-1].

Supported Platforms:
    ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[0.57, 0.11, 0.21],[0.38, 0.50, 0.57], [0.36, 0.16, 0.44]]).astype(np.float32))
    >>> y = x.median(axis=0, keepdims=False)
    >>> print(y)
    (Tensor(shape=[3], dtype=Float32, value= [ 3.79999995e-01,  1.59999996e-01,  4.39999998e-01]),
    Tensor(shape=[3], dtype=Int64, value= [1, 2, 2]))


.. method:: Tensor.median() -> Tensor
    :noindex:

Return the median of the input.

Returns:
    - y (Tensor) - Output median.

Supported Platforms:
    ``Ascend``

.. method:: Tensor.median(dim=-1, keepdim=False) -> tuple[Tensor]
    :noindex:

Output the median on the specified dimension ``dim`` and its corresponding index.
If ``dim`` is None, calculate the median of all elements in the Tensor.

Args:
    dim (int, optional): Specify the axis for calculation. Default: ``None`` .
    keepdim (bool, optional): Whether the output tensor need to retain ``dim`` dimension or not.
        Default: ``False`` .

Returns:
    - y (Tensor) - Output median, with the same data type as ``input`` .

      - If ``dim`` is ``None`` , ``y`` only has one element.
      - If ``keepdim`` is ``True`` , the ``y`` has the same shape as the ``input`` except the shape
        of ``y`` in dimension `dim` is size 1.
      - Otherwise, the ``y`` lacks `dim` dimension than input.

    - indices (Tensor) - The index of the median. Shape is consistent with ``y`` , with a data type of int64.

Raises:
    TypeError: If ``dim`` is not an int.
    TypeError: If ``keepdim`` is not a bool.
    ValueError: If ``dim`` is not in range of [-x.dim, x.dim-1].

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[0.57, 0.11, 0.21],[0.38, 0.50, 0.57], [0.36, 0.16, 0.44]]).astype(np.float32))
    >>> y = x.median(dim=0, keepdim=False)
    >>> print(y)
    (Tensor(shape=[3], dtype=Float32, value= [ 3.79999995e-01,  1.59999996e-01,  4.39999998e-01]),
    Tensor(shape=[3], dtype=Int64, value= [1, 2, 2]))""")
attach_docstr("tril", r"""tril(diagonal=0) -> Tensor

For details, please refer to :func:`mindspore.ops.tril`.
""")
attach_docstr("narrow", r"""narrow(dim, start, length) -> Tensor

Obtains a tensor of a specified length at a specified start position along a specified axis.

Args:
    dim (int): the axis along which to narrow.
    start (Union[int, Tensor]): the starting dimension.
    length (int): the distance to the ending dimension.

Returns:
    output (Tensors) - The narrowed tensor.

Raises:
    ValueError: The value of `dim` is out of range [-self.ndim, self.ndim).
    ValueError: The value of `start` is out of range [-self.shape[dim], self.shape[dim]].
    ValueError: The value of `length` is out of range [0, self.shape[dim] - start].

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> x = Tensor([[1, 2, 3], [4, 5, 6], [7, 8, 9]], mindspore.int32)
    >>> output = x.narrow(0, 0, 2)
    >>> print(output)
    [[ 1 2 3]
     [ 4 5 6]]
    >>> output = x.narrow(1, 1, 2)
    >>> print(output)
    [[ 2 3]
     [ 5 6]
     [ 8 9]]
""")
attach_docstr("expand_as", r"""expand_as(other) -> Tensor

Expand the shape of the input tensor to be the same as the another input tensor. The dim of the
input shape must be smaller than or equal to that of another and the broadcast rules must be met.

Args:
    other (Tensor): The target Tensor. It's shape is the target shape that input tensor need to be expanded.

Returns:
    Tensor, with the given shape of `other` and the same data type as `self`.

Raises:
    TypeError: If `other` is not a tensor.
    ValueError: If the shapes of `other` and `self` are incompatible.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[1, 2, 3], [1, 2, 3]]).astype(np.float32))
    >>> other = Tensor(np.array([[1, 1, 1], [1, 1, 1]]).astype(np.float32))
    >>> output = x.expand_as(other)
    >>> print(output)
    [[1. 2. 3.]
     [1. 2. 3.]]

.. method:: Tensor.expand_as(x) -> Tensor
    :noindex:

Expand the dimension of input tensor to the dimension of target tensor.

Args:
    x (Tensor): The target tensor. The shape of the target tensor must obey
        the broadcasting rule.

Returns:
    Tensor, has the same dimension as target tensor.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> from mindspore import dtype as mstype
    >>> input = Tensor([1, 2, 3], dtype=mstype.float32)
    >>> x = Tensor(np.ones((2, 3)), dtype=mstype.float32)
    >>> output = input.expand_as(x=x)
    >>> print(output)
    [[1. 2. 3.]
     [1. 2. 3.]]
""")
attach_docstr("__sub__", r"""__sub__(other, *, alpha=1) -> Tensor

Alias for :func:`mindspore.Tensor.sub` of `mindspore.Tensor.sub(other, *, alpha=1)`.

.. method:: Tensor.__sub__(y) -> Tensor
    :noindex:

Alias for :func:`mindspore.Tensor.sub` of `mindspore.Tensor.sub(y)`.
""")
attach_docstr("addcdiv", r"""addcdiv(tensor1, tensor2, *, value=1) -> Tensor

For details, please refer to :func:`mindspore.ops.addcdiv`.

Supported Platforms:
    ``Ascend``""")
attach_docstr("atan", r"""atan() -> Tensor

For details, please refer to :func:`mindspore.ops.atan`.""")
attach_docstr("matmul", r"""matmul(tensor2) -> Union[Tensor, numbers.Number]

Returns the matrix product of two tensors.

Note:
    - Numpy arguments `out`, `casting`, `order`, `subok`, `signature`, and `extobj` are not supported.

    - The dtype of `self` and `tensor2` must be same.

    - On Ascend platform, the dims of `self` and `tensor2` must be between 1 and 6.
    - On GPU platform, the supported dtypes of `self` and `tensor2` are ms.float16 and ms.float32.

Args:
    tensor2 (Tensor): Input tensor, scalar not allowed.
        The last dimension of `self` must be the same size as the second last dimension of `tensor2`.
        And the shape of tensor and other could be broadcast.

Returns:
    Tensor or scalar, the matrix product of the inputs. This is a scalar only
    when both `self` and `tensor2` are 1-d vectors.

Raises:
    TypeError: If the dtype of `self` and the dtype of `tensor2` are not the same.
    ValueError: If the last dimension of `self` is not the same size as the
        second-to-last dimension of `tensor2`, or if a scalar value is passed in.
    ValueError: If the shape of `self` and `tensor2` could not broadcast together.
    RuntimeError: On Ascend platforms, the dims of `self` or `tensor2` is less than 1 or greater than 6.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> # case 1 : Reasonable application of broadcast mechanism
    >>> input = Tensor(np.arange(2 * 3 * 4).reshape(2, 3, 4), mindspore.float32)
    >>> other = Tensor(np.arange(4 * 5).reshape(4, 5), mindspore.float32)
    >>> output = input.matmul(other)
    >>> print(output)
    [[[  70.   76.   82.   88.   94.]
      [ 190.  212.  234.  256.  278.]
      [ 310.  348.  386.  424.  462.]]
     [[ 430.  484.  538.  592.  646.]
      [ 550.  620.  690.  760.  830.]
      [ 670.  756.  842.  928. 1014.]]]
    >>> print(output.shape)
    (2, 3, 5)
    >>> # case 2 : the rank of `tensor2` is 1
    >>> input = Tensor(np.ones([1, 2]), mindspore.float32)
    >>> other = Tensor(np.ones([2,]), mindspore.float32)
    >>> output = input.matmul(other)
    >>> print(output)
    [2.]
    >>> print(output.shape)
    (1,)
""")
attach_docstr("topk", r"""topk(k, dim=-1, largest=True, sorted=True) -> tuple(Tensor, Tensor)

Finds the `k` largest or smallest element along the given dimension and returns its value and corresponding index.

.. warning::
    - Due to different memory layout and traversal methods on different platforms,
      the display order of calculation results may be inconsistent when `sorted` is False.

If the `self` is a one-dimensional Tensor, finds the `k` largest or smallest entries in the Tensor,
and outputs its value and index as a Tensor. `values[k]` is the `k` largest item in `self`,
and its index is `indices[k]` .

For a multi-dimensional matrix,
calculates the first or last `k` entries in a given dimension, therefore:

.. math::

    values.shape = indices.shape

If the two compared elements are the same, the one with the smaller index value is returned first.

Args:
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
    - indices (Tensor) - The indices of values within the last dimension of self.

Raises:
    TypeError: If `sorted` is not a bool.
    TypeError: If `k` is not an int.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore as ms
    >>> from mindspore import Tensor
    >>> x = ms.Tensor([[0.5368, 0.2447, 0.4302, 0.9673],
    ...                [0.4388, 0.6525, 0.4685, 0.1868],
    ...                [0.3563, 0.5152, 0.9675, 0.8230]], dtype=ms.float32)
    >>> output = Tensor.topk(x, 2, dim=1)
    >>> print(output)
    (Tensor(shape=[3, 2], dtype=Float32, value=
    [[ 9.67299998e-01,  5.36800027e-01],
     [ 6.52499974e-01,  4.68499988e-01],
     [ 9.67499971e-01,  8.23000014e-01]]), Tensor(shape=[3, 2], dtype=Int32, value=
    [[3, 0],
     [1, 2],
     [2, 3]]))
    >>> output2 = Tensor.topk(x, 2, dim=1, largest=False)
    >>> print(output2)
    (Tensor(shape=[3, 2], dtype=Float32, value=
    [[ 2.44700000e-01,  4.30200011e-01],
     [ 1.86800003e-01,  4.38800007e-01],
     [ 3.56299996e-01,  5.15200019e-01]]), Tensor(shape=[3, 2], dtype=Int32, value=
    [[1, 2],
     [3, 0],
     [0, 1]]))

.. method:: Tensor.topk(k, dim=None, largest=True, sorted=True) -> tuple(Tensor, Tensor)
    :noindex:

For more details, please refer to :func:`mindspore.ops.topk`.
""")
attach_docstr("atan2", r"""atan2(other) -> Tensor

For details, please refer to :func:`mindspore.ops.atan2`.""")
attach_docstr("argsort", r"""argsort(axis=-1, descending=False) -> Tensor

Sorts `self` along the given dimension in specified order and return the sorted indices.

Args:
    axis (int, optional): The axis to sort along. Default: ``-1`` , means the last dimension.
        The Ascend backend only supports sorting the last dimension.
    descending (bool, optional): The sort order. If `descending` is True then the elements
        are sorted in descending order by value. Otherwise sort in ascending order. Default: ``False`` .

Returns:
    Tensor, the indices of sorted `self`. Data type is int32.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[8, 2, 1], [5, 9, 3], [4, 6, 7]]), mindspore.float16)
    >>> sort = Tensor.argsort(x)  # x.argsort()
    >>> print(sort)
    [[2 1 0]
     [2 0 1]
     [0 1 2]]

.. method:: Tensor.argsort(dim=-1, descending=False, stable=False) -> Tensor
    :noindex:

Sorts `self` along the given dimension in specified order and return the sorted indices.
  
.. warning::
    This is an experimental optimizer API that is subject to deletion or change.

Args:
    dim (int, optional): The dim to sort along. Default: ``-1`` , means the last dimension.
        The Ascend backend only supports sorting the last dimension.
    descending (bool, optional): The sort order. If `descending` is ``True`` then the elements
        are sorted in descending order by value. Otherwise sort in ascending order. Default: ``False`` .
    stable (bool, optional): Whether to use stable sorting algorithm. Default: ``False``.

Returns:
    Tensor, the indices of sorted `self`. Data type is int64.

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
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[8, 2, 1], [5, 9, 3], [4, 6, 7]]), mindspore.float16)
    >>> sort = Tensor.argsort(x)  # x.argsort()
    >>> print(sort)
    [[2 1 0]
     [2 0 1]
     [0 1 2]]
""")
attach_docstr("greater", r"""greater(other) -> Tensor

For details, please refer to :func:`mindspore.ops.greater`.""")
attach_docstr("divide", r"""divide(other, *, rounding_mode=None) -> Tensor

Alias for :func:`mindspore.Tensor.div`.
""")
attach_docstr("atanh", r"""atanh() ->Tensor

For details, please refer to :func:`mindspore.ops.atanh`.""")
attach_docstr("expm1", r"""expm1() -> Tensor

For details, please refer to :func:`mindspore.ops.expm1`.
""")
attach_docstr("scatter_", r"""scatter_(dim, index, src) -> Tensor

Update the value in `src` to update `self` according to the specified `index`.

Index the dimension `self` selected by `dim` using `index` , traverse the other
dimensions in sequence, update the value of `src` to `self` , and return `self` .

This operator is the inverse of the in-place version of :func:`mindspore.Tensor.gather` .

This operation provides another three overloads to support parameter `reduce` and scalar value.

Here's an example using a 3-dimension tensor.

.. code-block::

    self[index[i][j][k]][j][k] = src[i][j][k]  # if dim == 0

    self[i][j][index[i][j][k]] = src[i][j][k]  # if dim == 2

.. warning::
    - If multiple indexes point to the same position in `self` , the final value of
      this position in `self` is uncertain.
    - On Ascend, behavior is unpredictable when the value of `index` is not in the
      range `[-self.shape[dim], self.shape[dim])` in forward.
    - This is an experimental API that is subject to change or deletion.

.. note::
    The inverse gradient from `self` to `src` can be calculated only when
    the shape of src is the same as that of `index`.

Args:
    dim (int): Which axis to scatter. Accepted range is `[-r, r)` where `r` is the rank of `self` .
    index (Tensor): The index to access `self` on the target axis specified by `dim` whose dtype must be int32
        or int64. If it is an empty Tensor, no operations is performed and directly returns `self` . Otherwise,
        its rank must be the same as `self` and the value range of each element must be `[-s, s)`
        where `s` is the size of `self` along axis `dim` .
    src (Tensor): The data to doing the update operation with `self` . It should have the same dtype and rank
        as `self` .

Returns:
    Tensor, the modified `self` itself.

Raises:
    TypeError: If type of `self` , `index` or `src` is unsupported.
    RuntimeError: If `dim` is out of the range `[-r, r)` .
    RuntimeError: If rank of `self` is larger than 8.
    RuntimeError: If dtype of tensor `self` , `index` or `src` is unsupported.
    RuntimeError: If dtype of `self` is not equal to the dtype of `src` .
    RuntimeError: If `self` , `index`, or `src` have different ranks and `index` is not an empty tensor.
    RuntimeError: If there is a dimension `d` that makes `index.size(d) > src.size(d)` .
    RuntimeError: If there is a dimension `d` that makes `index.size(d) > self.size(d)` .

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor, int64, float32
    >>> this_tensor = Tensor([[1, 2], [3, 4]], dtype=float32)
    >>> index = Tensor([[1, 0], [1, 0]], dtype=int64)
    >>> src = Tensor([[4, 3], [2, 1]], dtype=float32)
    >>> this_tensor.scatter_(1, index, src)
    >>> print(this_tensor)
    [[3., 4.],
     [1., 2.]]

.. method:: Tensor.scatter_(dim, index, src, *, reduce) -> Tensor
    :noindex:

Update the value in `src` to update `self` according to the specified `index`.

Using the operation specified by `reduce` to index the dimension `self` selected
by `dim` using `index` , traverse the other dimensions in sequence, accumulate or
multiply the value of `src` to `self` , and return `self` .

This operator is the inverse of the in-place version of :func:`mindspore.Tensor.gather` .

Expect that the replacement operation changes to accumulation or multiplication
based on the parameter `reduce`, other operations are the same as the overloaded
function that accept `src` without the parameter `reduce` .

Here's an example using a 3-dimension tensor.

.. code-block::

    self[index[i][j][k]][j][k] += src[i][j][k]  # if dim == 0, reduce == "add"

    self[i][j][index[i][j][k]] *= src[i][j][k]  # if dim == 2, reduce == "multiply"

.. warning::
    - If multiple indexes point to the same position in `self` , the final value of
      this position in `self` is uncertain.
    - On Ascend, behavior is unpredictable when the value of `index` is not in the
      range `[-self.shape[dim], self.shape[dim])` in forward.
    - This is an experimental API that is subject to change or deletion.

.. note::
    This overload function does not support reverse gradient calculation and will return zeros if calculate gradient.

Args:
    dim (int): Which axis to scatter. Accepted range is `[-r, r)` where `r` is the rank of `self` .
    index (Tensor): The index to access `self` on the target axis specified by `dim` whose dtype must be int32
        or int64. If it is an empty Tensor, no operations is performed and directly returns `self` . Otherwise,
        its rank must be the same as `self` and the value range of each element must be `[-s, s)`
        where `s` is the size of `self` along axis `dim` .
    src (Tensor): The data to doing the accumulate or multiply operation with `self` . It should have the
        same dtype and rank as `self` .

Keyword Args:
    reduce (str): Reduce operation, supports ``"add"`` and ``"multiply"`` . When `reduce` is ``"add"`` , `src`
        is accumulated to `input` base on `index` . When `reduce` is ``"multiply"`` , `src` is multiplied
        to `input` base on `index` .

Returns:
    Tensor, the modified `self` itself.

Raises:
    TypeError: If type of `self` , `index` or `src` is unsupported.
    ValueError: If `reduce` is a str but not ``"add"`` or ``"multiply"`` .
    RuntimeError: If `dim` is out of the range `[-r, r)` .
    RuntimeError: If rank of `self` is larger than 8.
    RuntimeError: If dtype of tensor `self` , `index` or `src` is unsupported.
    RuntimeError: If dtype of `self` is not equal to the dtype of `src` .
    RuntimeError: If `self` , `index`, or `src` have different ranks and `index` is not an empty tensor.
    RuntimeError: If there is a dimension `d` that makes `index.size(d) > src.size(d)` .
    RuntimeError: If there is a dimension `d` that makes `index.size(d) > self.size(d)` .

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor, int64, float32
    >>> this_tensor = Tensor([[1, 2], [3, 4]], dtype=float32)
    >>> index = Tensor([[1, 0], [1, 0]], dtype=int64)
    >>> src = Tensor([[4, 3], [2, 1]], dtype=float32)
    >>> this_tensor.scatter_(1, index, src, reduce='add')
    >>> print(this_tensor)
    [[4., 6.],
     [4., 6.]]

.. method:: Tensor.scatter_(dim, index, value) -> Tensor
    :noindex:

Update the value `value` to update `self` according to the specified `index`.

Index the dimension `self` selected by `dim` using `index` , traverse the other
dimensions in sequence, update the value `value` to `self` , and return `self` .

This operator is the inverse of the in-place version of :func:`mindspore.Tensor.gather` .

It can be considered that after the value is broadcasted as a Tensor whose shape
and dtype are consistent with `self` , other operations are the same as the
overloaded function that accept `src` without the parameter `reduce` .

Here's an example using a 3-dimension tensor.

.. code-block::

    self[index[i][j][k]][j][k] = value  # if dim == 0

    self[i][j][index[i][j][k]] = value  # if dim == 2

.. warning::
    - If multiple indexes point to the same position in `self` , the final value of
      this position in `self` is uncertain.
    - On Ascend, behavior is unpredictable when the value of `index` is not in the
      range `[-self.shape[dim], self.shape[dim])` in forward.
    - This is an experimental API that is subject to change or deletion.

Args:
    dim (int): Which axis to scatter. Accepted range is `[-r, r)` where `r` is the rank of `self` .
    index (Tensor): The index to access `self` on the target axis specified by `dim` whose dtype must be int32
        or int64. If it is an empty Tensor, no operations is performed and directly returns `self` . Otherwise,
        its rank must be the same as `self` and the value range of each element must be `[-s, s)`
        where `s` is the size of `self` along axis `dim` .
    value (int, float, bool): The data to doing the update operation with `self` . It can be considered as being
        broadcasted into a Tensor whose shape and dtype are the same as `self` , and then be regarded as `src`
        for calculation.

Returns:
    Tensor, the modified `self` itself.

Raises:
    TypeError: If type of `self` , `index` or `value` is unsupported.
    RuntimeError: If `dim` is out of the range `[-r, r)` .
    RuntimeError: If rank of `self` is larger than 8.
    RuntimeError: If dtype of tensor `self` or `index` is unsupported.
    RuntimeError: If `index` is not an empty tensor and its rank is different from the rank of `self` .
    RuntimeError: If there is a dimension `d` that makes `index.size(d) > self.size(d)` .

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor, int64, float32
    >>> this_tensor = Tensor([[1, 2], [3, 4]], dtype=float32)
    >>> index = Tensor([[0], [1]], dtype=int64)
    >>> this_tensor.scatter_(0, index, 10)
    >>> print(this_tensor)
    [[10., 2.],
     [10., 4.]]

.. method:: Tensor.scatter_(dim, index, value, *, reduce) -> Tensor
    :noindex:

Update the value `value` to update `self` according to the specified `index`.

Using the operation specified by `reduce` to index the dimension `self` selected
by `dim` using `index` , traverse the other dimensions in sequence, accumulate or
multiply the value `value` to `self` , and return `self` .

This operator is the inverse of the in-place version of :func:`mindspore.Tensor.gather` .

Expect that the replacement operation changes to accumulation or multiplication
based on the parameter `reduce`, other operations are the same as the overloaded
function that accept `value` without the parameter `reduce` .

Here's an example using a 3-dimension tensor.

.. code-block::

    self[i][index[i][j][k]][k] += value  # if dim == 1, reduce == "add"

    self[i][j][index[i][j][k]] *= value  # if dim == 2, reduce == "multiply"

.. warning::
    - If multiple indexes point to the same position in `self` , the final value of
      this position in `self` is uncertain.
    - On Ascend, behavior is unpredictable when the value of `index` is not in the
      range `[-self.shape[dim], self.shape[dim])` in forward.
    - This is an experimental API that is subject to change or deletion.

.. note::
    This overload function does not support reverse gradient calculation and will return zeros if calculate gradient.

Args:
    dim (int): Which axis to scatter. Accepted range is `[-r, r)` where `r` is the rank of `self` .
    index (Tensor): The index to access `self` on the target axis specified by `dim` whose dtype must be int32
        or int64. If it is an empty Tensor, no operations is performed and directly returns `self` . Otherwise,
        its rank must be the same as `self` and the value range of each element must be `[-s, s)`
        where `s` is the size of `self` along axis `dim` .
    value (int, float, bool): The data to doing the accumulate or multiply operation with `self` . It can be
        considered as being broadcasted into a Tensor whose shape and dtype are the same as `self` , and then
        be regarded as `src` for calculation.

Keyword Args:
    reduce (str): Reduce operation, supports ``"add"`` and ``"multiply"`` . When `reduce` is ``"add"`` , `value`
        is accumulated to `input` base on `index` . When `reduce` is ``"multiply"`` , `value` is multiplied
        to `input` base on `index` .

Returns:
    Tensor, the modified `self` itself.

Raises:
    TypeError: If type of `self` , `index` or `value` is unsupported.
    ValueError: If `reduce` is a str but not ``"add"`` or ``"multiply"`` .
    RuntimeError: If `dim` is out of the range `[-r, r)` .
    RuntimeError: If rank of `self` is larger than 8.
    RuntimeError: If dtype of tensor `self` or `index` is unsupported.
    RuntimeError: If `index` is not an empty tensor and its rank is different from the rank of `self` .
    RuntimeError: If there is a dimension `d` that makes `index.size(d) > self.size(d)` .

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor, int64, float32
    >>> this_tensor = Tensor([[1, 2], [3, 4]], dtype=float32)
    >>> index = Tensor([[0], [1]], dtype=int64)
    >>> this_tensor.scatter_(0, index, 3, reduce="multiply")
    >>> print(this_tensor)
    [[3., 2.],
     [9., 4.]]
""")
attach_docstr("index_add", r"""index_add(indices, y, axis, use_lock=True, check_index_bound=True) -> Tensor

Adds tensor `y` to specified axis and indices of tensor `self`. The axis should be in [-len(self.dim),  len(self.dim) - 1], and indices should be in [0, the size of `self` - 1] at the axis dimension.

Args:
    indices (Tensor): Add the value of `self` and `y` along the dimension of the `axis` according to the specified index value, with data type int32. The `indices` must be 1D with the same size as the size of `y` in the `axis` dimension. The values of `indices` should be in [0, b), where the b is the size of `self` in the `axis` dimension.
    y (Tensor): The input tensor with the value to add.
    axis (int): The dimension along which to index.
    use_lock (bool, optional): Whether to enable a lock to protect the updating process of variable tensors. If ``True`` , when updating the value of `self`, this process will be protected by a lock by using atomic operation. If ``False`` , the result may be unpredictable. Default: ``True`` .
    check_index_bound (bool, optional): If ``True`` , check indices boundary. If ``False`` , don't check indices boundary. Default: ``True`` .

Returns:
    Tensor, has the same shape and dtype as `self`.

Raises:
    TypeError: If neither `indices` nor `y` is a Tensor.
    ValueError: If axis is out of the range of `self` shape.
    ValueError: If `self` rank is not the same as `y` rank.
    ValueError: If shape of `indices` is not 1D or size of `indices` is not equal to dimension of y[axis].
    ValueError: If `y`'s shape is not the same as `self` except the `axis` th dimension.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), mindspore.float32)
    >>> indices = Tensor(np.array([0, 2]), mindspore.int32)
    >>> y = Tensor(np.array([[0.5, 1.0], [1.0, 1.5], [2.0, 2.5]]), mindspore.float32)
    >>> output = x.index_add(indices, y, axis = 1)
    >>> print(output)
    [[ 1.5  2.   4. ]
     [ 5.   5.   7.5]
     [ 9.   8.  11.5]]

.. method:: Tensor.index_add(dim, index, source, *, alpha=1) -> Tensor
    :noindex:

For details, please refer to :func:`mindspore.ops.index_add`.
The corresponding relationships between the parameters of `Tensor.index_add` and :func:`mindspore.ops.index_add`
are as follows: `dim` -> `axis`, `index` -> `indices`, `source * alpha` -> `y`.
""")
attach_docstr("logical_or", r"""logical_or(other) -> Tensor

For details, please refer to :func:`mindspore.ops.logical_or`.
""")
attach_docstr("sum", r"""sum(dim=None, keepdim=False, *, dtype=None) -> Tensor

Calculate sum of Tensor elements over a given dim.

Note:
    The `dim` with tensor type is only used for compatibility with older versions and is not recommended.

Args:
    dim (Union[None, int, tuple(int), list(int), Tensor], optional): Dimensions along which a sum is performed.
        If ``None`` , sum all the elements of the self tensor.
        If the `dim` is a tuple or list of ints, a sum is performed on all the dimensions specified in the tuple.
        Must be in the range :math:`[-self.ndim, self.ndim)` . Default: ``None`` .
    keepdim (bool, optional): Whether the output tensor has `dim` retained or not.
        If ``True`` , keep these reduced dimensions and the length is 1.
        If ``False`` , don't keep these dimensions. Default: ``False`` .

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The desired data type of returned Tensor. Default: ``None`` .

Returns:
    A Tensor, sum of elements over a given `dim` in `self`.

Raises:
    TypeError: If `dim` is not an int, tulpe(int), list(int), Tensor or None.
    ValueError: If `dim` is not in the range :math:`[-self.ndim, self.ndim)` .
    TypeError: If `keepdim` is not a bool.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> from mindspore import dtype as mstype
    >>> x = Tensor(np.array([[[1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]],
    ...                      [[4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [6, 6, 6, 6, 6, 6]],
    ...                      [[7, 7, 7, 7, 7, 7], [8, 8, 8, 8, 8, 8], [9, 9, 9, 9, 9, 9]]]), mstype.float32)
    >>> out = Tensor.sum(x)
    >>> print(out)
    270.0
    >>> out = Tensor.sum(x, dim=2)
    >>> print(out)
    [[ 6. 12. 18.]
    [24. 30. 36.]
    [42. 48. 54.]]
    >>> out = Tensor.sum(x, dim=2, keepdim=True)
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


.. method:: Tensor.sum(axis=None, dtype=None, keepdims=False, initial=None) -> Tensor
    :noindex:

Return sum of tensor elements over a given axis.

Note:
    Numpy arguments `out`, `where`, `casting`, `order`, `subok`, `signature`, and `extobj` are not supported.
    The `axis` with tensor type is only used for compatibility with older versions and is not recommended.

Args:
    axis (Union[None, int, tuple(int), list(int), Tensor], optional): Axis or axes along which a sum is performed.
        Default: ``None`` .
        If ``None`` , sum all the elements of the self tensor.
        If the `axis` is negative, it counts from the last to the first `axis`.
        If the `axis` is a tuple or list of ints, a sum is performed on all the axes specified in the tuple
        or list instead of a single `axis` or all the axes as before.
    dtype (:class:`mindspore.dtype`, optional): Default: ``None`` . Overrides the dtype of the
        output Tensor.
    keepdims (bool, optional): If this is set to ``True`` , the axes which are reduced are left in the result as
        dimensions with size one. With this option, the result will broadcast correctly against the self
        array. If the default value is passed, then `keepdims` will not be passed through to the sum method
        of sub-classes of ndarray, however any non-default value will be. If the sub-class method does not
        implement `keepdims` any exceptions will be raised. Default: ``False`` .
    initial (scalar, optional): Starting value for the sum. Default: ``None`` .

Returns:
    Tensor. A tensor with the same shape as self, with the specified `axis` removed.
    If the self tensor is a 0-d array, or if the `axis` is ``None`` , a scalar is returned.

Raises:
    TypeError: If self is not array_like, or `axis` is not int, tuple of ints, list of ints or Tensor,
        or `keepdims` is not integer, or `initial` is not scalar.
    ValueError: If any `axis` is out of range or duplicate axes exist.

See also:
    - :func:`mindspore.Tensor.cumsum`: Return the cumulative sum of the elements along a given `axis`.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.array([-1, 0, 1]).astype(np.float32))
    >>> print(input_x.sum())
    0.0
    >>> input_x = Tensor(np.arange(10).reshape(2, 5).astype(np.float32))
    >>> print(input_x.sum(axis=1))
    [10. 35.]
""")
attach_docstr("eq", r"""eq(other) -> Tensor

For details, please refer to :func:`mindspore.ops.eq`.""")
attach_docstr("unique", r"""unique(sorted=True, return_inverse=False, return_counts=False, dim=None) -> tuple(Tensor)

Returns the unique elements of `self`.

when `return_inverse=True`, also return a tensor containing the index of each value of `self`
corresponding to the output unique tensor.
when `return_counts=True`, also return a tensor containing the number of occurrences for each
unique value or tensor.

Args:
    sorted(bool, optional): Whether to sort the unique elements in ascending order before returning as output.
        Default: ``True`` .
    return_inverse(bool, optional): Whether to also return the indices for where elements in `self` ended up in
        the returned unique list. Default: ``False`` .
    return_counts(bool, optional): Whether to also return the counts for each unique element. Default: ``False`` .
    dim(int, optional): the dimension to operate upon. If ``None``, the unique of the flattened `self` is returned.
        Otherwise, each of the tensors indexed by the given dimension is treated as one of the elements to apply the
        unique operation upon. Default: ``None`` .

Returns:
    A tensor or a tuple of tensors containing some of tensor objects (`output`, `inverse_indices`, `counts`).

    - **output** (Tensor) - The output tensor including the unique elements of `self`, it has same dtype as `self`.
    - **inverse_indices** (Tensor, optional) - Return when ``return_inverse`` is True. It represents the indices for where
      elements in `self` map to in the output. When ``dim`` is ``None``, it has same shape as `self`,
      otherwise, the shape is self.shape[dim].
    - **counts** (Tensor, optional) - Return when ``return_counts`` is True. It represents the number of occurrences for each
      unique value or tensor. When ``dim`` is ``None``, it has same shape as output, otherwise, the shape is
      output.shape(dim).

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([1, 2, 5, 2]), mindspore.int32)
    >>> output = x.unique(return_inverse=True)
    >>> print(output)
    (Tensor(shape=[3], dtype=Int32, value= [1, 2, 5]), Tensor(shape=[4], dtype=Int64, value= [0, 1, 2, 1]))
    >>> y = output[0]
    >>> print(y)
    [1 2 5]
    >>> idx = output[1]
    >>> print(idx)
    [0 1 2 1]
""")
attach_docstr("__add__", r"""__add__(other) -> Tensor

Alias for :func:`mindspore.Tensor.add`.

.. method:: Tensor.__add__(other, *, alpha=1) -> Tensor
    :noindex:

Alias for overload function of :func:`mindspore.Tensor.add`.
""")
attach_docstr("var", r"""var(axis=None, ddof=0, keepdims=False) -> Tensor

Compute the variance along the specified axis.

The variance is the average of the squared deviations from the mean, i.e.,
:math:`var = mean(abs(x - x.mean())**2)`.

Return the variance, which is computed for the flattened array by default,
otherwise over the specified axis.

Note:
    Numpy arguments `dtype`, `out` and `where` are not supported.

Args:
    axis (Union[None, int, tuple(int)], optional): Axis or axes along which the variance is computed.
        The default is to compute the variance of the flattened array. Default: ``None`` .
    ddof (int, optional): Means Delta Degrees of Freedom. Default: ``0`` .
        The divisor used in calculations is :math:`N - ddof`, where :math:`N` represents the number of elements.
    keepdims (bool, optional): Whether the output Tensor has dim retained or not. If ``True`` , keep these reduced
        dimensions and the length is 1. If ``False`` , don't keep these dimensions. Default: ``False`` .

Returns:
    Variance tensor.

Raises:
    TypeError: If `axis` is not one of the followings: None, int, tuple.
    TypeError: If `ddof` is not an int.
    TypeError: If `keepdims` is not a bool.
    ValueError: If `axis` is out of range :math:`[-self.ndim, self.ndim)`.

See also:
    - :func:`mindspore.Tensor.mean`: Reduce a dimension of a tensor by averaging all elements in the dimension.
    - :func:`mindspore.Tensor.std`: Compute the standard deviation along the specified axis.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.array([1., 2., 3., 4.], np.float32))
    >>> output = input_x.var()
    >>> print(output)
    1.25

.. method:: Tensor.var(dim=None, *, correction=1, keepdim=False) -> Tensor
    :noindex:

Calculates the variance over the dimensions specified by `dim`. `dim` can be a single dimension, list of
dimensions, or None to reduce over all dimensions.

The variance (:math:`\delta ^2`) is calculated as:

.. math::
    \delta ^2 = \frac{1}{\max(0, N - \delta N)}\sum^{N - 1}_{i = 0}(x_i - \bar{x})^2

where :math:`x` is the sample set of elements, :math:`\bar{x}` is the sample mean, :math:`N` is the number
of samples and :math:`\delta N` is the `correction`.

Args:
    dim (None, int, tuple(int), optional): The dimension or dimensions to reduce. Defaults to ``None``.
        If ``None``, all dimensions are reduced.

Keyword Args:
    correction (int, optional): The difference between the sample size and sample degrees of freedom. Defaults
        to Bessel's correction. Defaults to ``1``.
    keepdim (bool, optional): Whether the output tensor has dim retained or not. If ``True`` , keep these
        reduced dimensions and the length is 1. If ``False``, don't keep these dimensions. Defaults to ``False``.

Returns:
    Tensor, the variance.
    Suppose the shape of `self` is :math:`(x_0, x_1, ..., x_R)`:

    - If `dim` is () and `keepdim` is set to ``False`` , returns a 0-D Tensor, indicating the variance of all
      elements in `self`.
    - If `dim` is int, e.g. ``1`` and `keepdim` is set to ``False`` , then the returned Tensor has shape
      :math:`(x_0, x_2, ..., x_R)`.
    - If `dim` is tuple(int) or list(int), e.g. ``(1, 2)`` and `keepdim` is set to ``False`` , then the returned
      Tensor has shape :math:`(x_0, x_3, ..., x_R)`.

Raises:
    TypeError: If `dim` is not one of the followings: None, int, list, tuple.
    TypeError: If `correction` is not an int.
    TypeError: If `keepdim` is not a bool.
    ValueError: If `dim` is out of range :math:`[-self.ndim, self.ndim)`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> input_x = Tensor([[8, 2, 1], [5, 9, 3], [4, 6, 7]], mindspore.float32)
    >>> output = input_x.var(dim=0, correction=1, keepdim=True)
    >>> print(output)
    [[ 4.333333, 12.333333, 9.333333]]""")
attach_docstr("__abs__", r"""__abs__() -> Tensor

Alias for :func:`Tensor.abs`.
""")
attach_docstr("max", r"""max() -> Tensor

Returns the maximum value of the self tensor.

Returns:
    Scalar Tensor with the same dtype as `input`, the maximum value of the input.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
    >>> output = x.max()
    >>> print(output)
    [0.7]

.. method:: Tensor.max(dim, keepdim=False) -> tuple(Tensor)
    :noindex:

Calculates the maximum value along with the given dim for the input tensor, and returns the maximum values and
indices.

Args:
    dim (int): The dimension to reduce.
    keepdim (bool, optional): Whether to keep dimension, if ``True`` the output will keep the same dimension as the
        `self` , the output will reduce dimension if ``False``. Default: ``False``.

Returns:
    tuple (Tensor), tuple of 2 tensors, containing the maximum value of the self tensor along the given
    dimension `dim` and the corresponding index.

    - **values** (Tensor) - The maximum value of self tensor, with the same shape as `index`, and same dtype as `self`.
    - **index** (Tensor) - The index for the maximum value of the self tensor, with dtype int64. If `keepdim` is
      ``True`` , the shape of output tensors is :math:`(self_1, self_2, ..., self_{dim-1}, 1, self_{dim+1}, ..., self_N)`.
      Otherwise, the shape is :math:`(self_1, self_2, ..., self_{dim-1}, self_{dim+1}, ..., self_N)` .

Raises:
    TypeError: If `keepdim` is not a bool.
    TypeError: If `dim` is not an int.
    TypeError: If self tensor data type is Complex.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
    >>> output, index = x.max(0, keepdim=True)
    >>> print(output, index)
    [0.7] [3]

.. method:: Tensor.max(axis=None, keepdims=False, *, initial=None, where=True, return_indices=False) -> tuple(Tensor)
    :noindex:

Return the maximum of a tensor or maximum along an axis.

Note:
    When `axis` is ``None``, `keepdims` and subsequent parameters have no effect.
    At the same time, the index is fixed to return 0.

Args:
    axis (Union[None, int, list, tuple of ints], optional): Axis or axes along which to operate. By default,
        flattened input is used. If this is a tuple of ints, the maximum is selected over multiple axes,
        instead of a single axis or all the axes as before. Default: ``None`` .
    keepdims (bool, optional):
        If this is set to ``True`` , the axes which are reduced are left in the result as dimensions with size one. 
        With this option, the result will broadcast correctly against the input array. Default: ``False`` .

Keyword Args:
    initial (scalar, optional): The minimum value of an output element. Must be present to allow computation
        on empty slice. Default: ``None`` .
    where (bool Tensor, optional): A boolean tensor which is broadcasted to match the dimensions of array,
        and selects elements to include in the reduction. If non-default value is passed, initial must also
        be provided. Default: ``True`` .
    return_indices (bool, optional): Whether to return the index of the maximum value. Default: ``False`` . 
        If `axis` is a list or tuple of ints, it must be ``False`` .

Returns:
    Tensor or scalar, maximum of self tensor. If `axis` is ``None`` , the result is a scalar value. 
    If `axis` is given, the result is a tensor of dimension ``self.ndim - 1``.

Raises:
    TypeError: If arguments have types not specified above.

See also:
    - :func:`mindspore.Tensor.argmin`: Return the indices of the minimum values along an axis.
    - :func:`mindspore.Tensor.argmax`: Return the indices of the maximum values along an axis.
    - :func:`mindspore.Tensor.min`: Return the minimum of a tensor or minimum along an axis.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> a = Tensor(np.arange(4).reshape((2, 2)).astype('float32'))
    >>> output = a.max()
    >>> print(output)
    3.0
    >>> value, indices = a.max(axis=0, return_indices=True)
    >>> print(value)
    [2. 3.]
    >>> print(indices)
    [1 1]
""")
attach_docstr("bitwise_and", r"""bitwise_and(other) ->Tensor

Returns bitwise `and` of two tensors element-wise.

Note:
    `self` and `other` comply with the type conversion rules to make the data types consistent.

Args:
    other (Tensor, Number.number): The shape is the same as the `self` or can be broadcast to the shape of `self`.

Returns:
    Tensor, has the same type as the `self` and has the same shape as after broadcasting.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([0, 0, 1, -1, 1, 1, 1]), mindspore.int16)
    >>> other = Tensor(np.array([0, 1, 1, -1, -1, 2, 3]), mindspore.int16)
    >>> output = input.bitwise_and(other)
    >>> print(output)
    [ 0  0  1 -1  1  0  1]
""")
attach_docstr("exp", r"""exp() -> Tensor

For details, please refer to :func:`mindspore.ops.exp`.
""")
attach_docstr("arcsinh", r"""arcsinh() -> Tensor

Alias for :func:`mindspore.Tensor.asinh`.
""")
attach_docstr("repeat_interleave", r"""repeat_interleave(repeats, dim=None, *, output_size=None) -> Tensor

Repeat elements of a tensor along a dim, like :func:`mindspore.numpy.repeat`.

.. warning::
    Only support on Atlas A2 training series.

.. note::
    The self tensor to repeat values for. Must be of type: float16, float32, 
    int8, uint8, int16, int32, or int64.

Args:
    repeats (Union[int, tuple, list, Tensor]): The number of times to repeat, must be positive.
    dim (int, optional): The dim along which to repeat, Default: ``None``. if dim is None,
        the self Tensor will be flattened and the output will alse be flattened.

Keyword Args:
    output_size (int, optional): Total output size for the given axis (e.g. sum of repeats),
        Default: ``None``.

Returns:
    One tensor with values repeated along the specified dim. If self has shape
    :math:`(s1, s2, ..., sn)` and dim is i, the output will have shape :math:`(s1, s2, ...,
    si * repeats, ..., sn)`. The output type will be the same as the type of `self`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input1 = Tensor(np.array([[0, 1, 2], [3, 4, 5]]), mindspore.int32)
    >>> output1 = input1.repeat_interleave(repeats=2, dim=0, output_size=None)
    >>> input2 = Tensor(np.array([[1, 2], [3, 4]]), mindspore.int32)
    >>> output2 = input2.repeat_interleave(Tensor(np.array([1, 2])), dim=0, output_size=None)
    >>> print(output1)
    >>> print(output2)
    [[0 1 2]
     [0 1 2]
     [3 4 5]
     [3 4 5]]
    [[1 2]
     [3 4]
     [3 4]]

.. method:: Tensor.repeat_interleave(repeats, dim=None) -> Tensor
    :noindex:

Repeat elements of a tensor along an dim, like :func:`mindspore.numpy.repeat`.

.. note::
    The tensor to repeat values for. Must be of type: float16,
    float32, int8, uint8, int16, int32, or int64.

Args:
    repeats (Union[int, tuple, list, Tensor]): The number of times to repeat, must be positive.
    dim (int, optional): The dim along which to repeat, Default: ``None``. if dim is None,
        the self Tensor will be flattened and the output will alse be flattened.

Returns:
    One tensor with values repeated along the specified dim. If self has shape
    :math:`(s1, s2, ..., sn)` and dim is i, the output will have shape :math:`(s1, s2, ...,
    si * repeats, ..., sn)`. The output type will be the same as the type of `self`.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input1 = Tensor(np.array([[0, 1, 2], [3, 4, 5]]), mindspore.int32)
    >>> output1 = input1.repeat_interleave(repeats=2, dim=0)
    >>> input2 = Tensor(np.array([[1, 2], [3, 4]]), mindspore.int32)
    >>> output2 = input2.repeat_interleave(Tensor(np.array([1, 2])), dim=0)
    >>> print(output1)
    >>> print(output2)
    [[0 1 2]
     [0 1 2]
     [3 4 5]
     [3 4 5]]
    [[1 2]
     [3 4]
     [3 4]]
""")
attach_docstr("gt", r"""gt(other) -> Tensor

For details, please refer to :func:'mindspore.Tensor.greater'.""")
attach_docstr("asinh", r"""asinh() -> Tensor

For details, please refer to :func:`mindspore.ops.asinh`.
""")
attach_docstr("masked_select", r"""masked_select(mask) -> Tensor

For details, please refer to :func:`mindspore.ops.masked_select`.""")
attach_docstr("mm", r"""mm(mat2) -> Tensor

Returns the matrix product of two arrays.
If `self` is a :math:`(n \times m)` Tensor, `mat2` is a
:math:`(m \times p)` Tensor, `out` will be a :math:`(n \times p)` Tensor.

Note:
    This function cannot support broadcasting.
    Refer to :func:`mindspore.ops.matmul` instead if you need a broadcastable function.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    mat2 (Tensor): The second matrix of matrix multiplication.
        The last dimension of `self` must be the same size as the first dimension of `mat2`.

Returns:
    Tensor, the matrix product of the inputs.

Raises:
    TypeError: If `self` or `mat2` is not a Tensor.
    RuntimeError: If the last dimension of `self` is not the same size as the
        second-to-last dimension of `mat2`.
    RuntimeError: If dtype of `self` or `mat2` is not float16, float32 or bfloat16.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore as ms
    >>> import numpy as np
    >>> x1 = ms.Tensor(np.random.rand(2, 3), ms.float32)
    >>> x2 = ms.Tensor(np.random.rand(3, 4), ms.float32)
    >>> out = x1.mm(x2)
    >>> print(out.shape)
    (2, 4)
""")
attach_docstr("arccos", r"""arccos() -> Tensor

Alias for :func:`mindspore.Tensor.acos`.
""")
attach_docstr("isclose", r"""isclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor

Returns a tensor of Boolean values indicating whether each element of `input`
is "close" to the corresponding element of `other`. Closeness is defined as:

.. math::
    |input-other| <= atol + rtol * |other|

Args:
    other (Tensor): Second tensor to compare.
    rtol (float, optional): Relative tolerance. Default: ``1e-05`` .
    atol (float, optional): Absolute tolerance. Default: ``1e-08`` .
    equal_nan (bool, optional): If ``True`` , then two NaNs will be considered equal. Default: ``True`` .

Returns:
    Tensor, with the same shape as `input` and `other` after broadcasting, its dtype is bool.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([1.3, 2.1, 3.2, 4.1, 5.1]), mindspore.float16)
    >>> other = Tensor(np.array([1.3, 3.3, 2.3, 3.1, 5.1]), mindspore.float16)
    >>> output = Tensor.isclose(input, other)
    >>> print(output)
    [ True False False False  True]

.. method:: Tensor.isclose(x2, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor
    :noindex:

Returns a new Tensor with boolean elements representing if each element of `input`
is "close" to the corresponding element of `x2`. Closeness is defined as:

.. math::
    |input-x2| <= atol + rtol * |x2|

Args:
    x2 (Tensor): Second tensor to compare. Dtype must be same as `input`.
    rtol (Union[float, int, bool], optional): Relative tolerance. Default: ``1e-05`` .
    atol (Union[float, int, bool], optional): Absolute tolerance. Default: ``1e-08`` .
    equal_nan (bool, optional): If ``True`` , then two NaNs will be considered equal. Default: ``False``.

Returns:
    A bool Tensor, with the shape as broadcasted result of the input `input` and `x2`.

Raises:
    TypeError: `x2` is not Tensor.
    TypeError: `input` or `x2` dtype is not support. Support dtype: float16, float32, float64, int8, int16, int32,
        int64 and uint8. On Ascend, more dtypes are support: bool and bfloat16.
    TypeError: `atol` or `rtol` is not float, int or bool.
    TypeError: `equal_nan` is not bool.
    TypeError: `input` and `x2` have different dtypes.
    ValueError: `input` and `x2` cannot broadcast.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([1.3, 2.1, 3.2, 4.1, 5.1]), mindspore.float16)
    >>> x2 = Tensor(np.array([1.3, 3.3, 2.3, 3.1, 5.1]), mindspore.float16)
    >>> output = Tensor.isclose(input, x2)
    >>> print(output)
    [ True False False False  True]
""")
attach_docstr("tile", r"""tile(dims) -> Tensor

Replicates an tensor with given dims times.

Note:
    On Ascend, the number of `dims` should not exceed 8, and currently does not support scenarios
    where more than 4 dimensions are repeated simultaneously.

Args:
    dims (tuple[int]): The parameter that specifies the number of replications,
        the parameter type is tuple, and the data type is int, i.e., :math:`(y_1, y_2, ..., y_S)`.
        Only constant value is allowed.

Returns:
    Tensor, has the same data type as the `self`. Suppose the length of `dims` is `d`,
    the dimension of `self` is `self.dim`, and the shape of `self` is :math:`(x_1, x_2, ..., x_S)`.

    - If `self.dim = d`, then the shape of their corresponding positions can be multiplied, and
      the shape of Outputs is :math:`(x_1*y_1, x_2*y_2, ..., x_S*y_S)`.
    - If `self.dim < d`, prepend 1 to the shape of `self` until their lengths are consistent.
      Such as set the shape of `self` as :math:`(1, ..., x_1, x_2, ..., x_S)`,
      then the shape of their corresponding positions can be multiplied, and the shape of Outputs is
      :math:`(1*y_1, ..., x_R*y_R, x_S*y_S)`.
    - If `self.dim > d`, prepend 1 to `dims` until their lengths are consistent. Such as set the
      `dims` as :math:`(1, ..., y_1, y_2, ..., y_S)`, then the shape of their corresponding positions
      can be multiplied, and the shape of Outputs is :math:`(x_1*1, ..., x_R*y_R, x_S*y_S)`.

Raises:
    TypeError: If `dims` is not a tuple or not all elements are int.
    ValueError: If not all elements of `dims` are greater than or equal to 0.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([[1, 2], [3, 4]]), mindspore.float32)
    >>> dims = (2, 3)
    >>> output = input.tile(dims)
    >>> print(output)
    [[1.  2.  1.  2.  1.  2.]
     [3.  4.  3.  4.  3.  4.]
     [1.  2.  1.  2.  1.  2.]
     [3.  4.  3.  4.  3.  4.]]
    >>> dims = (2, 3, 2)
    >>> output = input.tile(dims)
    >>> print(output)
    [[[1. 2. 1. 2.]
      [3. 4. 3. 4.]
      [1. 2. 1. 2.]
      [3. 4. 3. 4.]
      [1. 2. 1. 2.]
      [3. 4. 3. 4.]]
     [[1. 2. 1. 2.]
      [3. 4. 3. 4.]
      [1. 2. 1. 2.]
      [3. 4. 3. 4.]
      [1. 2. 1. 2.]
      [3. 4. 3. 4.]]]


.. method:: Tensor.tile(reps) -> Tensor
    :noindex:

For more details, please refer to :func:`mindspore.ops.tile`. The parameter `reps` in the current interface and the parameter `dims` in the detail reference interface are actually the same parameter.
""")
attach_docstr("greater_equal", r"""greater_equal(other) -> Tensor

For details, please refer to :func:`mindspore.ops.greater_equal`.
""")
attach_docstr("select", r"""select(dim, index) -> Tensor

Slices the `self` tensor along the selected dimension at the given index.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    dim (int): the dimension to slice.
    index (int): the index to select with.

Returns:
    Tensor.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> input = Tensor([[2, 3, 4, 5], [3, 2, 4, 5]])
    >>> y = Tensor.select(input, 0, 0)
    >>> print(y)
    [2 3 4 5]

.. method:: Tensor.select(condition, y) -> Tensor
    :noindex:

The conditional tensor determines whether the corresponding element in the output must be
selected from `self` (if True) or `y` (if False) based on the value of each
element.

It can be defined as:

.. math::
    out_i = \begin{cases}
    self_i, & \text{if } condition_i \\
    y_i, & \text{otherwise}
    \end{cases}

Args:
    condition (Tensor[bool]): The condition tensor, decides which element is chosen.
        The shape is :math:`(x_1, x_2, ..., x_N, ..., x_R)`.
    y (Union[Tensor, int, float]): The second Tensor to be selected.
        If `y` is a Tensor, its shape should be or be braodcast to :math:`(x_1, x_2, ..., x_N, ..., x_R)`.
        If `y` is int or float, it will be casted to int32 or float32, and broadcast to the same shape as `self`.
        There must be at least one Tensor between `self` and `y`.

Returns:
    Tensor, has the same shape as `condition`.

Raises:
    TypeError: If y is not a Tensor, int or float.
    ValueError: The shape of inputs cannot be broadcast.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> # Both input are Tensor
    >>> cond = Tensor([True, False])
    >>> x = Tensor([2,3], mindspore.float32)
    >>> y = Tensor([1,2], mindspore.float32)
    >>> output = Tensor.select(x, cond, y)
    >>> print(output)
    [2. 2.]
""")
attach_docstr("fill_diagonal_", r"""fill_diagonal_(fill_value, warp=False) -> Tensor

Fills the main diagonal of a Tensor in-place with a specified value and returns the result.
The `self` has at least 2 dimensions, and all dimensions of `self` must be equal in length
when the dimension of `self` is greater than 2.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    fill_value (number): The value to fill the diagonal of `self`.
    wrap (bool, optional): Controls whether the diagonal elements continue onto the
        remaining rows in case of a tall matrix(A matrix has more rows than columns). Default: ``False`` .

Returns:
    Tensor, has the same shape and data type as `self`.

Raises:
    ValueError: If the dimension of `self` is not greater than 1.
    ValueError: If the size of each dimension is not equal, when the dimension is greater than 2.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]).astype(np.float32))
    >>> fill_value = 9.9
    >>> x.fill_diagonal_(fill_value)
    >>> print(x)
    [[9.9 2.  3. ]
     [4.  9.9 6. ]
     [7.  8.  9.9]]
""")
attach_docstr("fill_", r"""fill_(value) -> Tensor

Fills `self` tensor with the specified `value` .

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    value (Union[Tensor, number.Number, bool]): Value to fill the `self` .

Returns:
    Tensor.

Raises:
    RunTimeError: The data type of `self` or `value` is not supported.
    RunTimeError: When the `value` is Tensor, it should be 0-D Tensor or 1-D Tensor with shape=[1].

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> from mindspore import ops
    >>> x = ops.zeros((3, 3))
    >>> print(x)
    [[0. 0. 0.]
     [0. 0. 0.]
     [0. 0. 0.]]
    >>> output = x.fill_(1.0)
    >>> print(output)
    [[1. 1. 1.]
     [1. 1. 1.]
     [1. 1. 1.]]
    >>> print(x)
    [[1. 1. 1.]
     [1. 1. 1.]
     [1. 1. 1.]]""")
attach_docstr("prod", r"""prod(dim=None, keepdim=False, dtype=None) -> Tensor

Reduces a dimension of a tensor by multiplying all elements in the dimension, by default. And also can
reduce a dimension of `self` along the `dim`. Determine whether the dimensions of the output and self are the
same by controlling `keepdim`.

Args:
    dim (Union[int, tuple(int), list(int), Tensor], optional): The dimensions to reduce. Default: ``None`` , reduce all dimensions.
        Only constant value is allowed. Assume the rank of `self` is r, and the value range is [-r,r).
    keepdim (bool, optional): If ``True`` , keep these reduced dimensions and the length is 1.
        If ``False`` , don't keep these dimensions. Default: ``False`` .
    dtype (:class:`mindspore.dtype`, optional): The desired data type of returned Tensor. Default: ``None`` .

Returns:
    Tensor.

    - If `dim` is ``None`` , and `keepdim` is ``False`` ,
      the output is a 0-D tensor representing the product of all elements in the self tensor.
    - If `dim` is int, set as 1, and `keepdim` is ``False`` ,
      the shape of output is :math:`(self_0, self_2, ..., self_R)`.
    - If `dim` is tuple(int) or list(int), set as (1, 2), and `keepdim` is ``False`` ,
      the shape of output is :math:`(self_0, self_3, ..., self_R)`.
    - If `dim` is 1-D Tensor, set as [1, 2], and `keepdim` is ``False`` ,
      the shape of output is :math:`(self_0, self_3, ..., self_R)`.

Raises:
    TypeError: If `dim` is not one of the following: int, Tuple, list or Tensor.
    TypeError: If `keepdim` is not a bool.
    ValueError: If `dim` is out of range.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.random.randn(3, 4, 5, 6).astype(np.float32))
    >>> output = Tensor.prod(x, 1, True)
    >>> result = output.shape
    >>> print(result)
    (3, 1, 5, 6)
    >>> # case 1: Reduces a dimension by multiplying all elements in the dimension.
    >>> x = Tensor(np.array([[[1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3]],
    ...                      [[4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [6, 6, 6, 6, 6, 6]],
    ...                      [[7, 7, 7, 7, 7, 7], [8, 8, 8, 8, 8, 8], [9, 9, 9, 9, 9, 9]]]), mindspore.float32)
    >>> output = Tensor.prod(x)
    >>> print(output)
    2.2833798e+33
    >>> print(output.shape)
    ()
    >>> # case 2: Reduces a dimension along axis 0.
    >>> output = Tensor.prod(x, 0, True)
    >>> print(output)
    [[[ 28.  28.  28.  28.  28.  28.]
      [ 80.  80.  80.  80.  80.  80.]
      [162. 162. 162. 162. 162. 162.]]]
    >>> # case 3: Reduces a dimension along axis 1.
    >>> output = Tensor.prod(x, 1, True)
    >>> print(output)
    [[[  6.   6.   6.   6.   6.   6.]]
     [[120. 120. 120. 120. 120. 120.]]
     [[504. 504. 504. 504. 504. 504.]]]
    >>> # case 4: Reduces a dimension along axis 2.
    >>> output = Tensor.prod(x, 2, True)
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


.. method:: Tensor.prod(axis=None, keep_dims=False, dtype=None)-> Tensor
    :noindex:

For more details, please refer to :func:`mindspore.ops.prod`.
""")
attach_docstr("maximum", r"""maximum(other) -> Tensor

For details, please refer to :func:`mindspore.ops.maximum`.""")
attach_docstr("masked_fill_", r"""masked_fill_(mask, value) -> Tensor

In-place version of :func:`mindspore.Tensor.masked_fill`.

.. warning::
    This is an experimental API that is subject to change or deletion.
""")
attach_docstr("arctan2", r"""arctan2(other) -> Tensor

Alias for :func:`Tensor.atan2`.
""")
attach_docstr("logaddexp2", r"""logaddexp2(other) -> Tensor

For details, please refer to :func:`mindspore.ops.logaddexp2`.
""")
attach_docstr("clamp", r"""clamp(min=None, max=None) -> Tensor

For details, please refer to :func:`mindspore.ops.clamp`.""")
attach_docstr("any", r"""any(axis=None, keep_dims=False) -> Tensor

Tests if any element in tensor evaluates to `True` along the given axes.

Args:
    axis (Union[int, tuple(int), list(int), Tensor], optional): The dimensions to reduce. If ``None`` ,
          all dimensions are reduced. Default ``None`` .
    keep_dims (bool, optional): Whether the output tensor has dim retained or not. Default ``False`` .

Returns:
    Tensor

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[True, False], [True, True]])
    >>>
    >>> # case 1:  By default, mindspore.Tensor.any tests along all the axes.
    >>> x.any()
    Tensor(shape=[], dtype=Bool, value= True)
    >>>
    >>> # case 2: Reduces a dimension along axis 1, with keep_dims False.
    >>> x.any(axis=1)
    Tensor(shape=[2], dtype=Bool, value= [ True,  True])
    >>>
    >>> # case 3: Reduces a dimension along axis (0, 1), with keep_dims False.
    >>> x.any(axis=(0,1))
    Tensor(shape=[], dtype=Bool, value= True)
    >>>
    >>> # case 4: Reduces a dimension along axis [0, 1], with keep_dims True.
    >>> x.any(axis=[0,1], keep_dims=True)
    Tensor(shape=[1, 1], dtype=Bool, value=
    [[ True]])

.. method:: Tensor.any(dim=None, keepdim=False) -> Tensor
    :noindex:

For details, please refer to :func:`mindspore.mint.any`.
""")
attach_docstr("mul_", r"""mul_(other) -> Tensor

Multiplies two tensors element-wise.

.. math::

    out_{i} = tensor_{i} * other_{i}

.. warning::
    This is an experimental API that is subject to change or deletion.

Note:
    - When `self` and `other` have different shapes,
      `other` be able to broadcast to a `self`.
    - `self` and `other` can not be bool type at the same time,
      [True, Tensor(True), Tensor(np.array([True]))] are all considered bool type.

Args:
    other (Union[Tensor, number.Number, bool]): `other` is a number.Number or
        a bool or a tensor whose data type is number.Number and bool.

Returns:
    Tensor, the shape is the same as `self` , and the data type is the same as `self` .

Raises:
    TypeError: If `other` is not one of the following: Tensor, number.Number, bool.
    RuntimeError: If `other` cannot be broadcast to `self`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([1.0, 2.0, 3.0]), mindspore.float32)
    >>> y = Tensor(np.array([4.0, 5.0, 6.0]), mindspore.float32)
    >>> output = x.mul_(y)
    >>> print(output)
    [ 4. 10. 18.]
    >>> print(x)
    [ 4. 10. 18.]
""")
attach_docstr("logical_and", r"""logical_and(other) -> Tensor

For details, please refer to :func:`mindspore.ops.logical_and`.
""")
attach_docstr("bitwise_or", r"""bitwise_or(other) ->Tensor

Returns bitwise `or` of two tensors element-wise.

Note:
    `self` and `other` comply with the type conversion rules to make the data types consistent.

Args:
    other (Tensor, Number.number): The shape is the same as the `self` or can be broadcast to the shape of `self`.

Returns:
    Tensor, has the same type as the `self` and has the same shape as after broadcasting.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([0, 0, 1, -1, 1, 1, 1]), mindspore.int16)
    >>> other = Tensor(np.array([0, 1, 1, -1, -1, 2, 3]), mindspore.int16)
    >>> output = input.bitwise_or(other)
    >>> print(output)
    [ 0  1  1 -1 -1  3  3]
""")
attach_docstr("roll", r"""roll(shifts, dims) -> Tensor

For details, please refer to :func:`mindspore.ops.roll`.
""")
attach_docstr("tanh", r"""tanh() -> Tensor

For details, please refer to :func:`mindspore.ops.tanh`.
""")
attach_docstr("chunk", r"""chunk(chunks, dim=0) -> tuple[Tensor]

Cut the self Tensor into `chunks` sub-tensors along the specified dimension.

Note:
    The number of sub-tensors returned by this function may be less than the number
    of sub-tensors specified by `chunks`.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    chunks (int): Number of sub-tensors to cut.
    dim (int, optional): Specify the dimensions that you want to split. Default: ``0`` .

Returns:
    A tuple of sub-tensors.

Raises:
    TypeError: The sum of `chunks` is not int.
    TypeError: If argument `dim` is not int.
    ValueError: If argument `dim` is out of range of :math:`[-self.ndim, self.ndim)` .
    ValueError: If argument `chunks` is not positive number.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.arange(9).astype("float32"))
    >>> output = input_x.chunk(3, dim=0)
    >>> print(output)
    (Tensor(shape=[3], dtype=Float32, value= [ 0.00000000e+00,  1.00000000e+00,  2.00000000e+00]),
        Tensor(shape=[3], dtype=Float32, value= [ 3.00000000e+00,  4.00000000e+00,  5.00000000e+00]),
        Tensor(shape=[3], dtype=Float32, value= [ 6.00000000e+00,  7.00000000e+00,  8.00000000e+00]))

.. method:: Tensor.chunk(chunks, axis=0) -> tuple[Tensor]
    :noindex:

Cut the self Tensor into `chunks` sub-tensors along the specified axis.

Note:
    This function may return less than the specified number of chunks!

Args:
    chunks (int): Number of sub-tensors to cut.
    axis (int, optional): Specify the dimensions that you want to split. Default: ``0`` .

Returns:
    A tuple of sub-tensors.

Raises:
    TypeError: The sum of `chunks` is not int.
    TypeError: If argument `axis` is not int.
    ValueError: If argument `axis` is out of range of :math:`[-self.ndim, self.ndim)` .
    ValueError: If argument `chunks` is not positive number.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.arange(9).astype("float32"))
    >>> output = input_x.chunk(3, axis=0)
    >>> print(output)
    (Tensor(shape=[3], dtype=Float32, value= [ 0.00000000e+00,  1.00000000e+00,  2.00000000e+00]),
        Tensor(shape=[3], dtype=Float32, value= [ 3.00000000e+00,  4.00000000e+00,  5.00000000e+00]),
        Tensor(shape=[3], dtype=Float32, value= [ 6.00000000e+00,  7.00000000e+00,  8.00000000e+00]))""")
attach_docstr("sort", r"""sort(dim=-1, descending=False) -> (Tensor, Tensor)

Sorts the elements of the self tensor along the given dimension in the specified order.

.. warning::
    Currently, the data types of float16, uint8, int8, int16, int32, int64 are well supported.
    If use float32, it may cause loss of accuracy.

Args:
    dim (int, optional): The dimension to sort along. Default: ``-1``, means the last dimension.
    descending (bool, optional): Controls the sort order. If `descending` is True, the elements
        are sorted in descending order, or else sorted in ascending order. Default: ``False`` .

Returns:
    - y1, a tensor whose values are the sorted values, with the same shape and data type as self.
    - y2, a tensor that consists of the indices of the elements in the original self tensor.
      Data type is int64.

Raises:
    TypeError: If `dim` is not an int.
    TypeError: If `descending` is not a bool.
    TypeError: If `self` not in float16, float32, uint8, int8, int16, int32, int64, bfloat16
    TypeError: If `stable` is not a bool.
    ValueError: If `dim` is not in range of [-len(self.shape), len(self.shape)).

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[8, 2, 1], [5, 9, 3], [4, 6, 7]]), mindspore.float16)
    >>> output = x.sort(dim=-1)
    >>> # The output below is based on the Ascend platform.
    >>> print(output)
    (Tensor(shape=[3, 3], dtype=Float16, value=
    [[ 1.0000e+00,  2.0000e+00,  8.0000e+00],
    [ 3.0000e+00,  5.0000e+00,  9.0000e+00],
    [ 4.0000e+00,  6.0000e+00,  7.0000e+00]]), Tensor(shape=[3, 3], dtype=Int64, value=
    [[2, 1, 0],
    [2, 0, 1],
    [0, 1, 2]]))

.. method:: Tensor.sort(axis=-1, descending=False) -> (Tensor, Tensor)
    :noindex:

Sorts the elements of the input tensor along the given dimension in the specified order.

Args:
    axis (int, optional): The dimension to sort along. Default: ``-1``, means the last dimension.
        The Ascend backend only supports sorting the last dimension.
    descending (bool, optional): Controls the sort order. If `descending` is True, the elements
        are sorted in descending order, or else sorted in ascending order. Default: ``False`` .

.. warning::
    Currently, the data types of float16, uint8, int8, int16, int32, int64 are well supported.
    If use float32, it may cause loss of accuracy.

Returns:
    - y1, a tensor whose values are the sorted values, with the same shape and data type as self.
    - y2, a tensor that consists of the indices of the elements in the original self tensor.
      Data type is int32.

Raises:
    TypeError: If `axis` is not an int.
    TypeError: If `descending` is not a bool.
    TypeError: If dtype of `self` is neither float16, float32, uint8, int8, int16, int32, int64.
    ValueError: If `axis` is not in range of [-len(self.shape), len(self.shape)).

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[8, 2, 1], [5, 9, 3], [4, 6, 7]]), mindspore.float16)
    >>> output = x.sort(axis=-1)
    >>> # The output below is based on the Ascend platform.
    >>> print(output)
    (Tensor(shape=[3, 3], dtype=Float16, value=
    [[ 1.0000e+00,  2.0000e+00,  8.0000e+00],
    [ 3.0000e+00,  5.0000e+00,  9.0000e+00],
    [ 4.0000e+00,  6.0000e+00,  7.0000e+00]]), Tensor(shape=[3, 3], dtype=Int32, value=
    [[2, 1, 0],
    [2, 0, 1],
    [0, 1, 2]]))
""")
attach_docstr("mul", r"""mul(other) -> Tensor

For details, please refer to :func:`mindspore.ops.mul`.
""")
attach_docstr("index_select", r"""index_select(axis, index) -> Tensor

Generates a new Tensor that accesses the values of `self` along the specified `axis` dimension
using the indices specified in `index`. The new Tensor has the same number of dimensions as `self`,
with the size of the `axis` dimension being equal to the length of `index`, and the size of all other
dimensions will be unchanged from the original `self` Tensor.

.. note::
    The value of index must be in the range of `[0, self.shape[axis])`, the result is undefined out of range.

Args:
    axis (int): The dimension to be indexed.
    index (Tensor): A 1-D Tensor with the indices to access in `self` along the specified axis.

Returns:
    Tensor, has the same dtype as `self` Tensor.

Raises:
    TypeError: If `index` is not a Tensor.
    TypeError: If `axis` is not int number.
    ValueError: If the value of `axis` is out the range of `[-self.ndim, self.ndim - 1]`.
    ValueError: If the dimension of `index` is not equal to 1.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> input = Tensor(np.arange(16).astype(np.float32).reshape(2, 2, 4))
    >>> print(input)
    [[[ 0.  1.  2.  3.]
      [ 4.  5.  6.  7.]]
     [[ 8.  9. 10. 11.]
      [12. 13. 14. 15.]]]
    >>> index = Tensor([0,], mindspore.int32)
    >>> y = input.index_select(1, index)
    >>> print(y)
    [[[ 0.  1.  2.  3.]]
     [[ 8.  9. 10. 11.]]]

.. method:: Tensor.index_select(dim, index) -> Tensor
    :noindex:

Generates a new Tensor that accesses the values of `self` along the specified `dim` dimension
using the indices specified in `index`. The new Tensor has the same number of dimensions as `self`,
with the size of the `dim` dimension being equal to the length of `index`, and the size of all other
dimensions will be unchanged from the original `self` Tensor.

.. note::
    The value of index must be in the range of `[0, self.shape[dim])`, the result is undefined out of range.

Args:
    dim (int): The dimension to be indexed.
    index (Tensor): A 1-D Tensor with the indices to access in `self` along the specified dim.

Returns:
    Tensor, has the same dtype as `self` Tensor.

Raises:
    TypeError: If `index` is not a Tensor.
    TypeError: If `dim` is not int number.
    ValueError: If the value of `dim` is out the range of `[-self.ndim, self.ndim - 1]`.
    ValueError: If the dimension of `index` is not equal to 1.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> input = Tensor(np.arange(16).astype(np.float32).reshape(2, 2, 4))
    >>> print(input)
    [[[ 0.  1.  2.  3.]
      [ 4.  5.  6.  7.]]
     [[ 8.  9. 10. 11.]
      [12. 13. 14. 15.]]]
    >>> index = Tensor([0,], mindspore.int32)
    >>> y = input.index_select(1, index)
    >>> print(y)
    [[[ 0.  1.  2.  3.]]
     [[ 8.  9. 10. 11.]]]""")
attach_docstr("nan_to_num", r"""nan_to_num(nan=None, posinf=None, neginf=None) -> Tensor

For details, please refer to :func:`mindspore.ops.nan_to_num`.

Supported Platforms:
    ``Ascend`` ``CPU``
""")
attach_docstr("where", r"""where(condition, y) -> Tensor

For details, please refer to :func:`mindspore.ops.where`.
""")
attach_docstr("repeat", r"""repeat(*repeats)

Copy the elements in each dimension of a Tensor based on the specified number of repetition times.

This function copies the tensor's data.

The shape of the output tensor can be described as follows, where :math:`n` is the number of
elements in `repeats`.

.. math::

    shape_{i} = \begin{cases}
    repeats_{i} * input.shape_{i} & \text{if } 0 \le i < input.{rank} \\
    repeats_{i} & \text{if } input.{rank} \le i < n \\
    \end{cases}

.. warning::
    This is an experimental API that is subject to change or deletion.

.. note::
    If need to specify the number of repetition times for each element of a single dimension, please
    refer to :func:`mindspore.Tensor.repeat_interleave`.

Args:
    *repeats (int): Number of repetitions of `self` in each dimension. The value must be a
        non-negative number. ``1`` indicates that the dimension remains unchanged. The number
        of elements in `repeats` must be greater than or equals to the number of dimensions
        in `self` . When the number of dimensions of `self` is less than the number of elements
        of `repeats` , `self` is broadcasted to the number of dimensions with the same number of
        elements of `repeats` (as shown in the example).

Returns:
    Tensor, the new Tensor after the element is copied from the specified number of repetitions.

Raises:
    RuntimeError: If the number of elements of `repeats` is less than the number of dimensions
        of `self` . Or `repeats` has negative element.
    RuntimeError: If the number of elements of `repeats` or the number of dimensions of `self` is larger than 8.
    TypeError: If type of `repeats` is unsupported.

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor
    >>> a = Tensor([[0, 1, 2], [3, 4, 5]])
    >>> print(a.repeat(3, 2))
    [[0 1 2 0 1 2]
     [3 4 5 3 4 5]
     [0 1 2 0 1 2]
     [3 4 5 3 4 5]
     [0 1 2 0 1 2]
     [3 4 5 3 4 5]]
    >>> print(a.repeat(2, 1, 3))  # a is treated as a shape [1, 2, 3]
    [[[0 1 2 0 1 2 0 1 2]
      [3 4 5 3 4 5 3 4 5]]
     [[0 1 2 0 1 2 0 1 2]
      [3 4 5 3 4 5 3 4 5]]]

.. method:: Tensor.repeat(repeats) -> Tensor
    :noindex:

Copy the elements in each dimension of a Tensor based on the specified number of repetition times.

This function copies the tensor's data.

Expect that a  variable-length int parameter is changed to a parameter which type is list or tuple,
other operations are the same as the overload with `*repeats` parameter.

The shape of the output tensor can be described as follows, where :math:`n` is the number of
elements in `repeats`.

.. math::

    shape_{i} = \begin{cases}
    repeats_{i} * input.shape_{i} & \text{if } 0 \le i < input.{rank} \\
    repeats_{i} & \text{if } input.{rank} \le i < n \\
    \end{cases}

.. warning::
    This is an experimental API that is subject to change or deletion.

.. note::
    If need to specify the number of repetition times for each element of a single dimension, please
    refer to :func:`mindspore.Tensor.repeat_interleave`.

Args:
    repeats (Union[tuple[int], list[int]]): Number of repetitions of `self` in each dimension. The value
        must be a non-negative number. ``1`` indicates that the dimension remains unchanged. The number
        of elements in `repeats` must be greater than or equals to the number of dimensions in `self` .
        When the number of dimensions of `self` is less than the number of elements of `repeats` , `self`
        is broadcasted to the number of dimensions with the same number of elements of `repeats` (as shown
        in the example).

Returns:
    Tensor, the new Tensor after the element is copied from the specified number of repetitions.

Raises:
    RuntimeError: If the number of elements of `repeats` is less than the number of dimensions
        of `self` . Or `repeats` has negative element.
    RuntimeError: If the number of elements of `repeats` or the number of dimensions of `self` is larger than 8.
    TypeError: If type of `repeats` is unsupported.

See also:
    - :func:`mindspore.Tensor.reshape`: Give a new shape to a tensor without changing its data.
    - :func:`mindspore.Tensor.resize`: Changes shape and size of tensor in-place.
    - :func:`mindspore.Tensor.repeat_interleave`: Repeats each element on the specified axis of a Tensor based
      on the specified number of times.
    - :func:`mindspore.Tensor.tile`: Repeats a Tensor on each dimension for a specified number of times. And
      there is no requirement on the number of parameters `repeats` .

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor
    >>> a = Tensor([[0, 1, 2], [3, 4, 5]])
    >>> print(a.repeat([3, 2]))
    [[0 1 2 0 1 2]
     [3 4 5 3 4 5]
     [0 1 2 0 1 2]
     [3 4 5 3 4 5]
     [0 1 2 0 1 2]
     [3 4 5 3 4 5]]
    >>> print(a.repeat(repeats=(2, 1, 3)))  # a is treated as a shape [1, 2, 3]
    [[[0 1 2 0 1 2 0 1 2]
      [3 4 5 3 4 5 3 4 5]]
     [[0 1 2 0 1 2 0 1 2]
      [3 4 5 3 4 5 3 4 5]]]
""")
attach_docstr("square", r"""square() -> Tensor

For details, please refer to :func:`mindspore.ops.square`.""")
attach_docstr("addmv", r"""addmv(mat, vec, *, beta=1, alpha=1) -> Tensor

For details, please refer to :func:`mindspore.ops.addmv`.

Supported Platforms:
    ``Ascend``""")
attach_docstr("less_equal", r"""less_equal(other) -> Tensor

For details, please refer to :func:`mindspore.ops.less_equal`.""")
attach_docstr("xlogy", r"""xlogy(other) -> Tensor

For details, please refer to :func:`mindspore.ops.xlogy`.
""")
attach_docstr("less", r"""less(other) -> Tensor

For details, please refer to :func:`mindspore.ops.less`.""")
attach_docstr("histc", r"""histc(bins=100, min=0, max=0) -> Tensor

For details, please refer to :func:`mindspore.ops.histc`.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``""")
attach_docstr("scatter_add", r"""scatter_add(dim, index, src) -> Tensor

Add all elements in `src` to the index specified by `index` to `self` along dimension specified by `dim`.
It takes three inputs `self`, `src` and `index` of the same rank r >= 1.

For a 3-D tensor, the operation updates input as follows:

.. code-block::

    self[index[i][j][k]][j][k] += src[i][j][k]  # if dim == 0

    self[i][index[i][j][k]][k] += src[i][j][k]  # if dim == 1

    self[i][j][index[i][j][k]] += src[i][j][k]  # if dim == 2

.. note::
    The rank of this tensor `self` must be at least 1.

Args:
    dim (int): Which dim to scatter. Accepted range is [-r, r) where r = rank(`self`).
    index (Tensor): The index of `self` to do scatter operation whose data type must be int32 or
        int64. Same rank as `self`. Except for the dimension specified by `dim`,
        the size of each dimension of `index` must be less than or equal to the size of
        the corresponding dimension of `self`.
    src (Tensor): The tensor doing the scatter operation with `self`, has the same type as `self` and
        the size of each dimension must be greater than or equal to that of `index`.

Returns:
    Tensor, has the same shape and type as `self`.

Raises:
    TypeError: If `index` is neither int32 nor int64.
    ValueError: If anyone of the rank among `self`, `index` and `src` is less than 1.
    ValueError: If the rank of `self`, `index` and `src` is not the same.
    ValueError: The size of any dimension of `index` except the dimension specified by `dim` is
        greater than the size of the corresponding dimension of `self`.
    ValueError: If the size of any dimension of `src` is less than that of `index`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> import mindspore as ms
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([[1, 2, 3, 4, 5]]), dtype=ms.float32)
    >>> src = Tensor(np.array([[8, 8]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[2, 4]]), dtype=ms.int64)
    >>> out = input.scatter_add(dim=1, index=index, src=src)
    >>> print(out)
    [[1. 2. 11. 4. 13.]]
    >>> input = Tensor(np.zeros((5, 5)), dtype=ms.float32)
    >>> src = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[0, 0, 0], [2, 2, 2], [4, 4, 4]]), dtype=ms.int64)
    >>> out = input.scatter_add(dim=0, index=index, src=src)
    >>> print(out)
    [[1. 2. 3. 0. 0.]
     [0. 0. 0. 0. 0.]
     [4. 5. 6. 0. 0.]
     [0. 0. 0. 0. 0.]
     [7. 8. 9. 0. 0.]]
    >>> input = Tensor(np.zeros((5, 5)), dtype=ms.float32)
    >>> src = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[0, 2, 4], [0, 2, 4], [0, 2, 4]]), dtype=ms.int64)
    >>> out = input.scatter_add(dim=1, index=index, src=src)
    >>> print(out)
    [[1. 0. 2. 0. 3.]
     [4. 0. 5. 0. 6.]
     [7. 0. 8. 0. 9.]
     [0. 0. 0. 0. 0.]
     [0. 0. 0. 0. 0.]]

.. method:: Tensor.scatter_add(indices, updates) -> Tensor
    :noindex:

Creates a new tensor by adding the values from the positions in `self` indicated by
`indices`, with values from `updates`. When multiple values are given for the same
index, the updated result will be the sum of all values. This operation is almost
equivalent to using ScatterNdAdd, except that the updates are applied on output `Tensor`
instead of input `Parameter`.

The last axis of `indices` is the depth of each index vectors. For each index vector,
there must be a corresponding value in `updates`. The shape of `updates` should be
equal to the shape of `self[indices]`. For more details, see Examples.

.. math::
    output\left [indices  \right ] = input\_x + update

.. note::
    The dimension of this tensor `self` must be no less than indices.shape[-1].

    If some values of the `indices` are out of bound:

    - On GPU, if some values of the `indices` are out of bound, instead of raising an index error,
      the corresponding `updates` will not be updated to self tensor.
    - On CPU, if some values of the `indices` are out of bound, raising an index error.
    - On Ascend, out of bound checking is not supported, if some values of the `indices` are out of bound,
      unknown errors may be caused.

Args:
    indices (Tensor): The index of input tensor whose data type is int32 or int64.
        The rank must be at least 2.
    updates (Tensor): The tensor to update the input tensor, has the same type as input,
        and updates. And the shape should be
        equal to :math:`indices.shape[:-1] + input\_x.shape[indices.shape[-1]:]`.

Returns:
    Tensor, has the same shape and type as `self`.

Raises:
    TypeError: If dtype of `indices` is neither int32 nor int64.
    ValueError: If length of shape of `self` is less than the last dimension of shape of `indices`.
    RuntimeError: If a value of `indices` is not in `self` on CPU backend.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = Tensor(np.array([[-0.1, 0.3, 3.6], [0.4, 0.5, -3.2]]), mindspore.float32)
    >>> indices = Tensor(np.array([[0, 0], [0, 0]]), mindspore.int32)
    >>> updates = Tensor(np.array([1.0, 2.2]), mindspore.float32)
    >>> output = input_x.scatter_add(indices, updates)
    >>> print(output)
    [[ 3.1  0.3  3.6]
     [ 0.4  0.5 -3.2]]
""")
attach_docstr("div_", r"""div_(other, *, rounding_mode=None) -> Tensor

In-place version of :func:`mindspore.Tensor.div`.""")
attach_docstr("lerp", r"""lerp(end, weight) -> Tensor

For more details, please refer to :func:`mindspore.ops.lerp`.""")
attach_docstr("_to", r"""_to(dtype) -> Tensor

    Returns a tensor with the new specified data type.

    Note:
        When converting complex numbers to boolean type, the imaginary part of the complex number is not
        taken into account. As long as the real part is non-zero, it returns True; otherwise, it returns False.

    Args:
        dtype (dtype.Number): The valid data type of the output tensor. Only constant value is allowed.

    Returns:
        Tensor, the data type of the tensor is `dtype`.

    Raises:
        TypeError: If `dtype` is not a Number.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> import numpy as np
        >>> from mindspore import Tensor
        >>> input_np = np.random.randn(2, 3, 4, 5).astype(np.float32)
        >>> input = Tensor(input_np)
        >>> dtype = mindspore.int32
        >>> output = input._to(dtype)
        >>> print(output.dtype)
        Int32
        >>> print(output.shape)
        (2, 3, 4, 5)
""")
attach_docstr("rsqrt", r"""rsqrt() -> Tensor

For details, please refer to :func:`mindspore.ops.rsqrt`.
""")
attach_docstr("t", r"""Transpose `self` .

For details, please refer to :func:`mindspore.ops.t`.

Supported Platforms:
    ``Ascend``
""")
attach_docstr("hardshrink", r"""hardshrink(lambd=0.5) -> Tensor

For details, please refer to :func:`mindspore.ops.hardshrink`.""")
attach_docstr("scatter", r"""scatter(dim, index, src) -> Tensor

Update the value in `src` to `self` according to the specified index.
For a 3-D tensor, the output will be:

.. code-block::

    output[index[i][j][k]][j][k] = src[i][j][k]  # if dim == 0

    output[i][index[i][j][k]][k] = src[i][j][k]  # if dim == 1

    output[i][j][index[i][j][k]] = src[i][j][k]  # if dim == 2

.. note::
    The backward is supported only for the case `src.shape == index.shape` when `src` is a tensor.
    The rank of the input tensor `self` must be at least 1.

Args:
    dim (int): Which axis to scatter. Accepted range is [-r, r) where r = rank(self).
    index (Tensor): The index to do update operation whose data must be positive number with type of int32
        or int64. Same rank as `self` . And accepted range is [-s, s) where s is the size along axis.
    src (Tensor, float): The data doing the update operation with `self`. Can be a tensor with the same data type
        as `self` or a float number to scatter.

Returns:
    Tensor, has the same shape and type as `self` .

Raises:
    TypeError: If `index` is neither int32 nor int64.
    ValueError: If rank of any of `self` , `index` and `src` is less than 1.
    ValueError: If the rank of `src` is not equal to the rank of `self` .
    TypeError: If the data types of `self` and `src` have different dtypes.
    RuntimeError: If `index` has negative elements.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> import mindspore as ms
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([[1, 2, 3, 4, 5]]), dtype=ms.float32)
    >>> src = Tensor(np.array([[8, 8]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[2, 4]]), dtype=ms.int64)
    >>> out = input.scatter(dim=1, index=index, src=src)
    >>> print(out)
    [[1. 2. 8. 4. 8.]]
    >>> input = Tensor(np.zeros((5, 5)), dtype=ms.float32)
    >>> src = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[0, 0, 0], [2, 2, 2], [4, 4, 4]]), dtype=ms.int64)
    >>> out = input.scatter(dim=0, index=index, src=src)
    >>> print(out)
    [[1. 2. 3. 0. 0.]
     [0. 0. 0. 0. 0.]
     [4. 5. 6. 0. 0.]
     [0. 0. 0. 0. 0.]
     [7. 8. 9. 0. 0.]]
    >>> input = Tensor(np.zeros((5, 5)), dtype=ms.float32)
    >>> src = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[0, 2, 4], [0, 2, 4], [0, 2, 4]]), dtype=ms.int64)
    >>> out = input.scatter(dim=1, index=index, src=src)
    >>> print(out)
    [[1. 0. 2. 0. 3.]
     [4. 0. 5. 0. 6.]
     [7. 0. 8. 0. 9.]
     [0. 0. 0. 0. 0.]
     [0. 0. 0. 0. 0.]] 

.. method:: Tensor.scatter(axis, index, src) -> Tensor
    :noindex:

Update the value in `src` to `self` according to the specified index.
Refer to :func:`mindspore.ops.tensor_scatter_elements` for more details.

.. note::
    The backward is supported only for the case `src.shape == index.shape`.
    The rank of the input tensor `self` must be at least 1.

Args:
    axis (int): Which axis to scatter. Accepted range is [-r, r) where r = rank(self).
    index (Tensor): The index to do update operation whose data must be positive number with type of int32
        or int64. Same rank as `self` . And accepted range is [-s, s) where s is the size along axis.
    src (Tensor, float): The data doing the update operation with `self`. Can be a tensor with the same data type
        as `self` or a float number to scatter.

Returns:
    Tensor, has the same shape and type as `self` .

Raises:
    TypeError: If `index` is neither int32 nor int64.
    ValueError: If rank of any of `self` , `index` and `src` is less than 1.
    ValueError: If the rank of `src` is not equal to the rank of `self` .
    TypeError: If the data types of `self` and `src` have different dtypes.
    RuntimeError: If `index` has negative elements.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> import mindspore as ms
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([[1, 2, 3, 4, 5]]), dtype=ms.float32)
    >>> src = Tensor(np.array([[8, 8]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[2, 4]]), dtype=ms.int64)
    >>> out = input.scatter(axis=1, index=index, src=src)
    >>> print(out)
    [[1. 2. 8. 4. 8.]]
    >>> input = Tensor(np.zeros((5, 5)), dtype=ms.float32)
    >>> src = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[0, 0, 0], [2, 2, 2], [4, 4, 4]]), dtype=ms.int64)
    >>> out = input.scatter(axis=0, index=index, src=src)
    >>> print(out)
    [[1. 2. 3. 0. 0.]
     [0. 0. 0. 0. 0.]
     [4. 5. 6. 0. 0.]
     [0. 0. 0. 0. 0.]
     [7. 8. 9. 0. 0.]]
    >>> input = Tensor(np.zeros((5, 5)), dtype=ms.float32)
    >>> src = Tensor(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), dtype=ms.float32)
    >>> index = Tensor(np.array([[0, 2, 4], [0, 2, 4], [0, 2, 4]]), dtype=ms.int64)
    >>> out = input.scatter(axis=1, index=index, src=src)
    >>> print(out)
    [[1. 0. 2. 0. 3.]
     [4. 0. 5. 0. 6.]
     [7. 0. 8. 0. 9.]
     [0. 0. 0. 0. 0.]
     [0. 0. 0. 0. 0.]]
""")
attach_docstr("bincount", r"""bincount(weights=None, minlength=0) -> Tensor

For details, please refer to :func:`mindspore.ops.bincount`.""")
attach_docstr("log1p", r"""log1p() -> Tensor

For details, please refer to :func:`mindspore.ops.log1p`.
""")
attach_docstr("sin", r"""sin() -> Tensor

For details, please refer to :func:`mindspore.ops.sin`.""")
attach_docstr("dot", r"""dot(other) -> Tensor

Computes the dot product of two 1D tensor.

Args:
    other (Tensor): The input in the dot product, must be 1D.

Returns:
    Tensor, the shape is [] and the data type is same as `self`.

Raises:
    TypeError: If `other` is not tensor.
    RuntimeError: If dtypes of `self` and `other` are not same.
    RuntimeError: If shapes of `self` and `other` are not same.
    RuntimeError: If shapes of `self` and `other` are not 1D.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> input = Tensor([2.0, 3.0], mindspore.float32)
    >>> other = Tensor([2.0, 1.0], mindspore.float32)
    >>> output = Tensor.dot(input, other)  # input.dot(other)
    >>> print(output)
    [7.        ]
    >>> print(output.dtype)
    Float32
""")
attach_docstr("frac", r"""frac() -> Tensor

For details, please refer to :func:`mindspore.ops.frac`.
""")
attach_docstr("sinh", r"""sinh() -> Tensor

For details, please refer to :func:`mindspore.ops.sinh`.""")
attach_docstr("absolute", r"""absolute() -> Tensor

Alias for :func:`Tensor.abs`.
""")
attach_docstr("new_zeros", r"""new_zeros(size, dtype=None) -> Tensor

Return a tensor of `size` filled with zeros.

Args:
    size (Union[int, tuple(int), list(int)]): An int, list or tuple of integers defining the output shape.
    dtype (:class:`mindspore.dtype`, optional): The desired dtype of the output tensor. If None, the returned
        tensor has the same dtype as `self`. Default: ``None``.

Returns:
    Tensor, the shape and dtype is defined above and filled with zeros.

Raises:
    TypeError: If `size` is neither an int nor a tuple/list of int.
    TypeError: If `dtype` is not a MindSpore dtype.
    ValueError: If `size` contains negative values.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> x = Tensor((), mindspore.int32)
    >>> x.new_zeros((2, 3))
    Tensor(shape=[2, 3], dtype=Int32, value=
    [[0, 0, 0],
     [0, 0, 0]])
""")
attach_docstr("kthvalue", r"""kthvalue(k, dim=-1, keepdim=False) -> Tensor

Calculates the kth smallest value along given dim specified by `dim` of the `self`
tensor, and returns a tuple of (`values`, `indices`) where `values` contains the k-th smallest element
and `indices` provides the index of each corresponding element.

Args:
    k (int): Specifies the k-th smallest element to retrieve.
    dim (int, optional): The dimension along which to find the k-th smallest value. Default: ``-1`` .
    keepdim (bool, optional): Whether to reduce dimension, if ``True`` , the output will keep same dimension with the
        `self`, the output will reduce dimension if ``False`` . Default: ``False`` .

Returns:
    A tuple consisting of `values` and `indices`.

    - **values** (Tensor) - The k-th smallest value of self tensor, with the same dtype as `self`.
    - **indices** (Tensor) - The indices for the k-th smallest value of the self tensor, it has the same shape as `values` with dtype of int64.
        
Raises:
    TypeError: If `k` or `dim` is not an int.
    TypeError: If `keepdim` is not a bool.
    TypeError: If dtype of `self` is not supported.
    ValueError: If `self` is an empty Tensor.
    RuntimeError: If `k` is not in the proper range.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor, ops
    >>> input_x = Tensor(np.array([[1.01, 2.02, 3.03], [1.04, 2.05, 3.06]]), mindspore.float32)
    >>> out = input_x.kthvalue(2, 1, False)
    >>> print(out)
    (Tensor(shape=[2], dtype=Float32, value= [ 2.01999998e+00,  2.04999995e+00]), Tensor(shape=[2], dtype=Int64, value= [1, 1]))
    >>> out1 = input_x.kthvalue(2, 1, True)
    >>> print(out1)
    (Tensor(shape=[2, 1], dtype=Float32, value=
    [[ 2.01999998e+00],
     [ 2.04999995e+00]]), Tensor(shape=[2, 1], dtype=Int64, value=
    [[1],
     [1]]))
""")
attach_docstr("logical_not", r"""logical_not() -> Tensor

For details, please refer to :func:`mindspore.ops.logical_not`.
""")
attach_docstr("put_", r"""put_(index, source, accumulate=False) -> Tensor

Copies the elements from source into the positions specified by index.
index and source need to have the same number of elements, but not necessarily the same shape.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    index (LongTensor): the index to be operated in the tensor.
    source (Tensor): the tensor containing values to copy from.
    accumulate (bool, optional): whether to accumulate into self, default: ``False``.

Returns:
    Tensor, with the same dtype and shape as the `input`.

Raises:
    TypeError: If dtype of `index` is not long type.
    TypeError: If `input` and `source` have different dtypes.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore as ms
    >>> from mindspore import Tensor
    >>> src = Tensor([[4, 3, 5],[6, 7, 8]], ms.float32)
    >>> index = Tensor([1, 3], ms.int64)
    >>> source = Tensor([9, 10], ms.float32)
    >>> src.put_(index, source)
    >>> print(src)
    [[4. 9. 5.]
     [10. 7. 8.]]
""")
attach_docstr("arcsin", r"""arcsin() -> Tensor

Alias for :func:`mindspore.Tensor.asin`.
""")
attach_docstr("unsqueeze", r"""unsqueeze(dim) -> Tensor

For details, please refer to :func:`mindspore.ops.unsqueeze`.
""")
attach_docstr("log10", r"""log10() -> Tensor

For details, please refer to :func:`mindspore.ops.log10`.
""")
attach_docstr("sub_", r"""sub_(other, *, alpha=1) -> Tensor

For details, please refer to :func:`mindspore.mint.sub`.
""")
attach_docstr("negative", r"""negative() -> Tensor

Alias for :func:`mindspore.Tensor.neg`.
""")
attach_docstr("erf", r"""erf() -> Tensor

For details, please refer to :func:`mindspore.ops.erf`.""")
attach_docstr("div", r"""div(other, *, rounding_mode=None) -> Tensor

For details, please refer to :func:`mindspore.ops.div`.""")
attach_docstr("argmax", r"""argmax(axis=None, keepdims=False) -> Tensor

Return the indices of the maximum values along the given axis of the tensor.

Args:
    axis (Union[int, None], optional): Specify the axis for computation. If ``None`` , compute all elements in the
        tensor. Default ``None`` .
    keepdims (bool, optional): Whether the output tensor has dim retained. Default ``False`` .

Returns:
    Tensor

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[9, 3, 4, 5],
    ...                       [5, 2, 7, 4],
    ...                       [8, 1, 3, 6]])
    >>> # case 1: By default, compute the maximum of all elements.
    >>> x.argmax()
    Tensor(shape=[], dtype=Int64, value= 0)
    >>>
    >>> # case 2: Compute the maximum along axis 1.
    >>> x.argmax(axis=1)
    Tensor(shape=[3], dtype=Int64, value= [0, 2, 0])
    >>>
    >>> # case 3: If keepdims=True, the output shape will be same of that of the input.
    >>> x.argmax(axis=1, keepdims=True)
    Tensor(shape=[3, 1], dtype=Int64, value=
    [[0],
     [2],
     [0]])

.. method:: Tensor.argmax(dim=None, keepdim=False) -> Tensor
    :noindex:

Return the maximum values along the given dimension of the tensor. 

Args:
    dim (Union[int, None], optional): Specify the dim for computation. If ``None`` , compute all elements in the
        tensor.
    keepdim (bool, optional): Whether the output tensor has dim retained.

Returns:
    Tensor

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[9, 3, 4, 5],
    ...                       [5, 2, 7, 4],
    ...                       [8, 1, 3, 6]])
    >>> # case 1: By default, compute the maximum of all elements.
    >>> x.argmax()
    Tensor(shape=[], dtype=Int64, value= 0)
    >>>
    >>> # case 2: Compute the maximum along dim 1.
    >>> x.argmax(dim=1)
    Tensor(shape=[3], dtype=Int64, value= [0, 2, 0])
    >>>
    >>> # case 3: If keepdim=True, the output shape will be same of that of the input.
    >>> x.argmax(dim=1, keepdim=True)
    Tensor(shape=[3, 1], dtype=Int64, value=
    [[0],
     [2],
     [0]])
""")
attach_docstr("new_full", r"""new_full(size, fill_value, *, dtype=None) -> Tensor

Return a tensor of `size` filled with `fill_value`.

Args:
    size (Union[tuple(int), list(int)]): The output shape.
    fill_value (Union[Number, bool]): The value to fill the output tensor.

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The desired data type of returned Tensor. If None, the returned tensor has the same dtype as `self`. Default: ``None``.

Returns:
    Tensor, the shape and dtype is defined above and filled with `fill_value`.

Raises:
    TypeError: If `size` is not a tuple or list of int.
    TypeError: If `dtype` is not a MindSpore dtype.
    ValueError: If `size` contains negative values.

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor
    >>> x = Tensor([1, 2, 3, 4], mindspore.int32)
    >>> output = x.new_full((2, 3), 3)
    >>> print(output)
    [[3 3 3]
     [3 3 3]]
""")
attach_docstr("diag", r"""diag() -> Tensor

For details, please refer to :func:`mindspore.ops.diag`.

.. method:: Tensor.diag(diagonal=0) -> Tensor
    :noindex:

If input is a vector (1-D tensor), then returns a 2-D square tensor with the elements of input as the diagonal.

If input is a matrix (2-D tensor), then returns a 1-D tensor with the diagonal elements of input.

The argument diagonal controls which diagonal to consider:

- If `diagonal` = 0, it is the main diagonal.

- If `diagonal` > 0, it is above the main diagonal.

- If `diagonal` < 0, it is below the main diagonal.

.. warning::
    - This is an experimental API that is subject to change or deletion.
    - The graph mode and CPU/GPU backends do not support non-zero values for the diagonal parameter.

Args:
    diagonal (int, optional): the diagonal to consider. Default: ``0``.

Returns:
    Tensor, has the same dtype as the `input`, its shape is up to `diagonal`:

    - If `input` shape is :math:`(x_0)`: then output shape is :math:`(x_0 + \left | diagonal \right | , x_0 + \left | diagonal \right | )` 2-D Tensor.

    - If `input` shape is :math:`(x_0, x_1)`: then output shape is main diagonal to move :math:`(\left | diagonal \right |)` elements remains elements' length 1-D Tensor.

Raises:
    ValueError: If shape of `input` is not 1-D and 2-D.

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor
    >>> input = Tensor([1, 2, 3, 4]).astype('int32')
    >>> output = input.diag()
    >>> print(output)
    [[1 0 0 0]
     [0 2 0 0]
     [0 0 3 0]
     [0 0 0 4]]""")
attach_docstr("gcd", r"""gcd(other) -> Tensor

For details, please refer to :func:`mindspore.ops.gcd`.""")
attach_docstr("gather", r"""gather(dim, index) -> Tensor

Gather data from a tensor by indices.

.. math::
    output[(i_0, i_1, ..., i_{dim}, i_{dim+1}, ..., i_n)] =
    input[(i_0, i_1, ..., index[(i_0, i_1, ..., i_{dim}, i_{dim+1}, ..., i_n)], i_{dim+1}, ..., i_n)]

.. warning::
    On Ascend, the behavior is unpredictable in the following cases:

    - the value of `index` is not in the range `[-self.shape[dim], self.shape[dim])` in forward;
    - the value of `index` is not in the range `[0, self.shape[dim])` in backward.

Args:
    dim (int): the axis to index along, must be in range `[-self.rank, self.rank)`.
    index (Tensor): The index tensor, with int32 or int64 data type. A valid `index` should be:

        - :math:`index.rank == self.rank`;
        - for :math:`axis != dim`, :math:`index.shape[axis] <= self.shape[axis]`;
        - the value of :math:`index` is in range :math:`[-self.shape[dim], self.shape[dim])`.

Returns:
    Tensor, has the same type as `self` and the same shape as `index`.

Raises:
    ValueError: If the shape of `index` is illegal.
    ValueError: If `dim` is not in :math:`[-self.rank, self.rank)`.
    ValueError: If the value of `index` is out of the valid range.
    TypeError: If the type of `index` is illegal.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([[-0.1, 0.3, 3.6], [0.4, 0.5, -3.2]]), mindspore.float32)
    >>> index = Tensor(np.array([[0, 0], [1, 1]]), mindspore.int32)
    >>> output = input.gather(1, index)
    >>> print(output)
    [[-0.1 -0.1]
     [0.5   0.5]]

.. method:: Tensor.gather(input_indices, axis, batch_dims=0) -> Tensor
    :noindex:

Returns the slice of the input tensor corresponding to the elements of `input_indices` on the specified `axis`.

The following figure shows the calculation process of Gather commonly:

.. image:: ../../images/Gather.png

where params represents the input `input_params`, and indices represents the index to be sliced `input_indices`.

.. note::
    - The value of input_indices must be in the range of `[0, input_param.shape[axis])`.
      On CPU and GPU, an error is raised if an out of bound indice is found. On Ascend, the results may be
      undefined.
    - The data type of self cannot be
      `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ on Ascend
      platform currently.

Args:
    input_indices (Tensor): Index tensor to be sliced, the shape of tensor is :math:`(y_1, y_2, ..., y_S)`.
        Specifies the indices of elements of the original Tensor. The data type can be int32 or int64.
    axis (Union(int, Tensor[int])): Specifies the dimension index to gather indices.
        It must be greater than or equal to `batch_dims`.
        When `axis` is a Tensor, the size must be 1.
    batch_dims (int, optional): Specifies the number of batch dimensions. It must be less than or euqal to the rank
        of `input_indices`. Default: ``0`` .

Returns:
    Tensor, the shape of tensor is
    :math:`input\_params.shape[:axis] + input\_indices.shape[batch\_dims:] + input\_params.shape[axis + 1:]`.

Raises:
    TypeError:  If `axis` is not an int or Tensor.
    ValueError: If `axis` is a Tensor and its size is not 1.
    TypeError:  If `self` is not a tensor.
    TypeError:  If `input_indices` is not a tensor of type int.
    RuntimeError: If `input_indices` is out of range :math:`[0, input_param.shape[axis])` on CPU or GPU.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> # case1: input_indices is a Tensor with shape (5, ).
    >>> input_params = Tensor(np.array([1, 2, 3, 4, 5, 6, 7]), mindspore.float32)
    >>> input_indices = Tensor(np.array([0, 2, 4, 2, 6]), mindspore.int32)
    >>> axis = 0
    >>> output = input_params.gather(input_indices=input_indices, axis=axis)
    >>> print(output)
    [1. 3. 5. 3. 7.]
    >>> # case2: input_indices is a Tensor with shape (2, 2). When the input_params has one dimension,
    >>> # the output shape is equal to the input_indices shape.
    >>> input_indices = Tensor(np.array([[0, 2], [2, 6]]), mindspore.int32)
    >>> axis = 0
    >>> output = input_params.gather(input_indices=input_indices, axis=axis)
    >>> print(output)
    [[1. 3.]
     [3. 7.]]
    >>> # case3: input_indices is a Tensor with shape (2, ) and
    >>> # input_params is a Tensor with shape (3, 4) and axis is 0.
    >>> input_params = Tensor(np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]), mindspore.float32)
    >>> input_indices = Tensor(np.array([0, 2]), mindspore.int32)
    >>> axis = 0
    >>> output = input_params.gather(input_indices=input_indices, axis=axis)
    >>> print(output)
    [[ 1.  2.  3.  4.]
     [ 9. 10. 11. 12.]]
    >>> # case4: input_indices is a Tensor with shape (2, ) and
    >>> # input_params is a Tensor with shape (3, 4) and axis is 1, batch_dims is 1.
    >>> input_params = Tensor(np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]), mindspore.float32)
    >>> input_indices = Tensor(np.array([0, 2, 1]), mindspore.int32)
    >>> axis = 1
    >>> batch_dims = 1
    >>> output = input_params.gather(input_indices, axis, batch_dims)
    >>> print(output)
    [ 1.  7. 10.]
""")
attach_docstr("transpose", r"""transpose(dim0, dim1) -> Tensor

Interchange two axes of a tensor.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    dim0 (int): Specifies the first dimension to be transposed.
    dim1 (int): Specifies the second dimension to be transposed.

Returns:
    Transposed tensor, has the same data type as `self`.

Raises:
    TypeError: If `dim0` or `dim1` is not integer.
    ValueError: If `dim0` or `dim1` is not in the range of :math:`[-ndim, ndim-1]`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.ones((2,3,4), dtype=np.float32))
    >>> output = Tensor.transpose(input, 0, 2)
    >>> print(output.shape)
    (4, 3, 2)


.. method:: Tensor.transpose(*axes) -> Tensor
    :noindex:

Permutes the dimensions of the self tensor according to self permutation.

For a 1-D array this has no effect, as a transposed vector is simply the same vector.
To convert a 1-D array into a 2D column vector please refer to :func:`mindspore.ops.expand_dims`.
For a 2-D array, this is a standard matrix transpose. For an n-D array, if axes are given,
their order indicates how the axes are permuted (see Examples).
If axes are not provided and a.shape is :math:`(i[0], i[1], ... i[n-2], i[n-1])`,
then a.transpose().shape is :math:`(i[n-1], i[n-2], ... i[1], i[0])`.

Note:
    On GPU and CPU, if the value of `axes` is negative, its actual value is `axes[i] + rank(self)`.

Args:
    axes (tuple[int]): The permutation to be converted. The elements in `axes` are composed of the
        indexes of each dimension of `self`. The length of `axes` and the shape of `self` must be the
        same. Only constant value is allowed. Must be in the range [-rank(self), rank(self)).

Returns:
    Tensor, the type of output tensor is the same as `self` and the shape of output tensor is decided by the
    shape of `self` and the value of `axes`.

Raises:
    TypeError: If `axes` is not a tuple.
    ValueError: If length of shape of `self` is not equal to length of shape of `axes`.
    ValueError: If the same element exists in `axes`.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([[[1, 2, 3], [4, 5, 6]], [[7, 8, 9], [10, 11, 12]]]), mindspore.float32)
    >>> axes = (0, 2, 1)
    >>> output = Tensor.transpose(input, axes)
    >>> print(output)
    [[[ 1.  4.]
      [ 2.  5.]
      [ 3.  6.]]
     [[ 7. 10.]
      [ 8. 11.]
      [ 9. 12.]]]
""")
attach_docstr("round", r"""round(decimals=0) -> Tensor

For details, please refer to :func:`mindspore.ops.round`.
""")
attach_docstr("arctan", r"""arctan() -> Tensor

Alias for :func:`mindspore.Tensor.atan`.
""")
attach_docstr("bitwise_not", r"""bitwise_not() -> Tensor

Returns bitwise `not` of `self`.

.. warning::
    This is an experimental API that is subject to change or deletion.

Returns:
    Tensor, has the same shape and type as `self`.

Raises:
    TypeError: If `self` is not a Tensor.
    RuntimeError: If dtype of `self` is not int or bool.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([True, False, True, False]))
    >>> output = input.bitwise_not()
    >>> print(output)
    [False True False True]
""")
attach_docstr("trunc", r"""trunc() -> Tensor

For details, please refer to :func:`mindspore.ops.trunc`.
""")
attach_docstr("ne", r"""ne(other) -> Tensor

Alias for :func:`mindspore.Tensor.not_equal`.
""")
attach_docstr("all", r"""all(axis=None, keep_dims=False) -> Tensor

Tests if all element in tensor evaluates to `True` along the given axes.

Args:
    axis (Union[int, tuple(int), list(int), Tensor], optional): The dimensions to reduce. If ``None`` ,
            all dimensions are reduced. Default ``None`` .
    keep_dims (bool, optional): Whether the output tensor has dim retained or not. Default ``False`` .

Returns:
    Tensor

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[True, False], [True, True]])
    >>>
    >>> # case 1:  By default, mindspore.Tensor.all tests along all the axes.
    >>> x.all()
    Tensor(shape=[], dtype=Bool, value= False)
    >>> 
    >>> # case 2: Reduces a dimension along axis 1, with keep_dims False.
    >>> x.all(axis=1)
    Tensor(shape=[2], dtype=Bool, value= [False,  True])
    >>>
    >>> # case 3: Reduces a dimension along axis (0, 1), with keep_dims False.
    >>> x.all(axis=(0,1))
    Tensor(shape=[], dtype=Bool, value= False)
    >>>
    >>> # case 4: Reduces a dimension along axis [0, 1], with keep_dims True.
    >>> x.all(axis=[0,1], keep_dims=True)
    Tensor(shape=[1, 1], dtype=Bool, value=
    [[False]])

.. method:: Tensor.all(dim=None, keepdim=False) -> Tensor
    :noindex:

Tests if all element in tensor evaluates to `True` along the given axes.

Args:
    dim (Union[int, tuple(int), list(int), Tensor], optional): The dimensions to reduce. If ``None`` ,
            all dimensions are reduced. Default ``None`` .
    keepdim (bool, optional): Whether the output tensor has dim retained or not. Default ``False`` .

Returns:
    Tensor

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[True, False], [True, True]])
    >>>
    >>> # case 1:  By default, mindspore.Tensor.all tests along all the axes.
    >>> x.all()
    Tensor(shape=[], dtype=Bool, value= False)
    >>> 
    >>> # case 2: Reduces a dimension along dim 1, with keepdim False.
    >>> x.all(dim=1)
    Tensor(shape=[2], dtype=Bool, value= [False,  True])
    >>>
    >>> # case 3: Reduces a dimension along dim (0, 1), with keepdim False.
    >>> x.all(dim=(0,1))
    Tensor(shape=[], dtype=Bool, value= False)
    >>>
    >>> # case 4: Reduces a dimension along dim [0, 1], with keepdim True.
    >>> x.all(dim=[0,1], keepdim=True)
    Tensor(shape=[1, 1], dtype=Bool, value=
    [[False]])
""")
attach_docstr("copy_", r"""copy_(src, non_blocking=False) -> Tensor

Copies the elements from `src` into `self` tensor and returns `self`.

.. warning::
    This is an experimental API that is subject to change or deletion.

    If Copying is performed between Ascend and Ascend, the `src` tensor must be broadcastable with the `self` tensor,
    and they can be of different data types.
    Copying is performed between CPU and Ascend or CPU and CPU are only supported if `self` and `src` have
    the same shape and data type and they are all contiguous.

Args:
    src (Tensor): the source tensor to copy from.
    non_blocking (bool, optional): If ``True`` and copying is performed between CPU and Ascend, and `self` and `src`
        have the same shape and data type and are contiguous. The copy may occur asynchronously with respect to the
        host. For other cases, this argument has no effect. Default: ``False``.

Returns:
    Return self Tensor.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> a = Tensor(np.ones((3, 3)).astype("float32"))
    >>> b = Tensor(np.zeros((3, 3)).astype("float32"))
    >>> a.copy_(b)
    >>> print(a)
    [[0. 0. 0.]
     [0. 0. 0.]
     [0. 0. 0.]]
""")
attach_docstr("le", r"""le(other) -> Tensor

For details, please refer to :func:`mindspore.ops.le`.""")
attach_docstr("addmm", r"""addmm(mat1, mat2, *, beta=1, alpha=1) -> Tensor

For details, please refer to :func:`mindspore.ops.addmm`.""")
attach_docstr("clip", r"""clip(min=None, max=None) -> Tensor

Alias for :func:`mindspore.Tensor.clamp`.
""")
attach_docstr("min", r"""min() -> Tensor

Returns the minimum value of the self tensor.

Returns:
    Scalar Tensor with the same dtype as `self`, the minimum value of the self.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
    >>> output = Tensor.min(x)
    >>> print(output)
    0.0

.. method:: Tensor.min(dim, keepdim=False) -> tuple(Tensor)
    :noindex:

Calculates the minimum value along with the given dim for the self tensor, and returns the minimum values and
indices.

Args:
    dim (int): The dimension to reduce.
    keepdim (bool, optional): Whether to reduce dimension, if ``True`` the output will keep the same dimension as
        the `self` , the output will reduce dimension if ``False``. Default: ``False``.

Returns:
    tuple (Tensor), tuple of 2 tensors, containing the minimum value of the self tensor along the given
    dimension `dim` and the corresponding index.

    - **values** (Tensor) - The minimum value of self tensor along the given dimension `dim`, with the same shape
      as `index`, and same dtype as `self`.
    - **index** (Tensor) - The index for the minimum value of the self tensor, with dtype int64. If `keepdim`
      is ``True`` , the shape of output tensors is :math:`(self_1, self_2, ..., self_{dim-1}, 1, self_{dim+1}, ..., self_N)`.
      Otherwise, the shape is :math:`(self_1, self_2, ..., self_{dim-1}, self_{dim+1}, ..., self_N)` .

Raises:
    TypeError: If `keepdim` is not a bool.
    TypeError: If `dim` is not an int.
    TypeError: If self tensor data type is Complex.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([0.0, 0.4, 0.6, 0.7, 0.1]), mindspore.float32)
    >>> output, index = x.min(0, keepdim=True)
    >>> print(output, index)
    [0.0] [0]

.. method:: Tensor.min(axis=None, keepdims=False, *, initial=None, where=True, return_indices=False) -> Tensor|number.Number
    :noindex:

Return the minimum of a tensor or minimum along an axis.

Note:
    When `axis` is ``None``, `keepdims` and subsequent parameters have no effect.
    At the same time, the index is fixed to return 0.

Args:
    axis (Union[None, int, list, tuple of ints], optional): An axis or axes along which to operate. By default,
        flattened input is used. If `axis` is a tuple of ints, the minimum is selected over multiple axes,
        instead of a single axis or all the axes as before. Default: ``None`` .
    keepdims (bool, optional): If ``True`` , the axes which are reduced are left in the result as dimensions with
        size one. With this option, the result will broadcast correctly against the input array. Default: ``False`` .

Keyword Args:
    initial (scalar, optional): The minimum value of an output element. Must be present to allow computation on
        empty slice. Default: ``None`` .
    where (Tensor[bool], optional): A boolean tensor which is broadcasted to match the dimensions of array,
        and selects elements to include in the reduction. If non-default value is passed, initial must also
        be provided. Default: ``True`` .
    return_indices (bool, optional): Whether to return the index of the minimum value. Default: ``False`` .
        If `axis` is a list or tuple of ints, it must be ``False`` .

Returns:
    Tensor or scalar, minimum of self tensor. If `axis` is ``None`` , the result is a scalar
    value. If `axis` is given, the result is a tensor of dimension ``self.ndim - 1``.

Raises:
    TypeError: If arguments have types not specified above.

See also:
    - :func:`mindspore.Tensor.argmin`: Return the indices of the minimum values along an axis.
    - :func:`mindspore.Tensor.argmax`: Return the indices of the maximum values along an axis.
    - :func:`mindspore.Tensor.max`: Return the minimum of a tensor or minimum along an axis.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> a = Tensor(np.arange(4).reshape((2, 2)).astype('float32'))
    >>> output = Tensor.min(a)
    >>> print(output)
    0.0
    >>> output = Tensor.min(a, axis=0)
    >>> print(output)
    [0. 1.]
    >>> output = Tensor.min(a, axis=0, initial=9, where=Tensor([False]))
    >>> print(output)
    [9. 9.]
    >>> output = Tensor.min(a, axis=0, initial=9, where=Tensor([False, True]))
    >>> print(output)
    [9. 1.]
    >>> value, indices = Tensor.min(a, axis=0, return_indices=True)
    >>> print(value)
    [0. 1.]
    >>> print(indices)
    [0 0]
""")
attach_docstr("tan", r"""tan() ->Tensor

For details, please refer to :func:`mindspore.ops.tan`.
""")
attach_docstr("floor_divide", r"""floor_divide(other) -> Tensor

Divides the self tensor by the other input tensor element-wise and round down to the closest integer.

`self` and `other` comply with the implicit type conversion rules to make the data types consistent.
Inputs must be two tensors or one tensor and one scalar.
When the `self` and `other` are two tensors,
dtypes of them cannot be bool at the same time, and the shapes of them could be broadcast.
When the `self` and `other` are one tensor and one scalar,
the scalar could only be a constant.

.. math::
    out_{i} = \text{floor}( \frac{self_i}{other_i})

where the :math:`floor` indicates the Floor operator. For more details,
please refer to the :class:`mindspore.mint.floor` operator.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    other (Union[Tensor, Number, bool]): The other input is a number or
        a bool or a tensor whose data type is number or bool.

Returns:
    Tensor, the shape is the same as the one after broadcasting,
    and the data type is the one with higher precision or higher digits between `self` and `other`.

Raises:
    TypeError: If `self` and `other` are not the following: Tensor, number.Number or bool.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> input = Tensor(np.array([2, 4, -1]), mindspore.int32)
    >>> other = Tensor(np.array([3, 3, 3]), mindspore.int32)
    >>> output = input.floor_divide(other)
    >>> print(output)
    [ 0  1 -1]
    >>> input = Tensor(2.0, mindspore.float32)
    >>> other = Tensor(2.0, mindspore.float32)
    >>> output = input.floor_divide(other)
    >>> print(output)
    1.0
""")
attach_docstr("arctanh", r"""arctanh() -> Tensor

Alias for :func:`mindspore.Tensor.atanh`.
""")
attach_docstr("split", r"""split(split_size, dim=0) -> tuple(Tensor)

Splits the Tensor into chunks along the given dim.

Args:
    split_size (Union[int, tuple(int), list(int)]):
        If `split_size` is an int type, `tensor` will be split into equally sized chunks, each chunk with 
        size `split_size`. Last chunk will be smaller than `split_size` if `tensor.shape[dim]` is not divisible
        by `split_size`.
        If `split_size` is a list type, then `tensor` will be split into len(split_size)
        chunks with sizes `split_size` along the given `dim`.
    dim (int, optional): The dim along which to split. Default: ``0`` .

Returns:
    A tuple of sub-tensors.

Raises:
    TypeError: If argument `dim` is not int.
    ValueError: If argument `dim` is out of range of :math:`[-tensor.ndim, tensor.ndim)`.
    TypeError: If each element in `split_size` is not integer.
    TypeError: If argument `split_size` is not int, tuple(int) or list(int).
    ValueError: The sum of `split_size` is not equal to x.shape[dim].

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = np.arange(9).astype("float32")
    >>> output = Tensor.split(Tensor(input_x), 3)
    >>> print(output)
    (Tensor(shape=[3], dtype=Float32, value= [ 0.00000000e+00,  1.00000000e+00,  2.00000000e+00]),
     Tensor(shape=[3], dtype=Float32, value= [ 3.00000000e+00,  4.00000000e+00,  5.00000000e+00]),
     Tensor(shape=[3], dtype=Float32, value= [ 6.00000000e+00,  7.00000000e+00,  8.00000000e+00]))


.. method:: Tensor.split(split_size_or_sections, axis=0) -> tuple(Tensor)
    :noindex:

Splits the Tensor into chunks along the given axis.

Args:
    split_size_or_sections (Union[int, tuple(int), list(int)]):
        If `split_size_or_sections` is an int type, `tensor` will be split into equally sized chunks,
        each chunk with size `split_size_or_sections`. Last chunk will be smaller than `split_size_or_sections`
        if `tensor.shape[axis]` is not divisible by `split_size_or_sections`.
        If `split_size_or_sections` is a list type, then `tensor` will be split into len(split_size_or_sections)
        chunks with sizes `split_size_or_sections` along the given `axis`.
    axis (int, optional): The axis along which to split. Default: ``0`` .

Returns:
    A tuple of sub-tensors.

Raises:
    TypeError: If argument `axis` is not int.
    ValueError: If argument `axis` is out of range of :math:`[-tensor.ndim, tensor.ndim)`.
    TypeError: If each element in `split_size_or_sections` is not integer.
    TypeError: If argument `split_size_or_sections` is not int, tuple(int) or list(int).
    ValueError: The sum of `split_size_or_sections` is not equal to x.shape[axis].

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input_x = np.arange(9).astype("float32")
    >>> output = Tensor.split(Tensor(input_x), 3)
    >>> print(output)
    (Tensor(shape=[3], dtype=Float32, value= [ 0.00000000e+00,  1.00000000e+00,  2.00000000e+00]),
     Tensor(shape=[3], dtype=Float32, value= [ 3.00000000e+00,  4.00000000e+00,  5.00000000e+00]),
     Tensor(shape=[3], dtype=Float32, value= [ 6.00000000e+00,  7.00000000e+00,  8.00000000e+00]))
""")
attach_docstr("acos", r"""acos() -> Tensor

For details, please refer to :func:`mindspore.ops.acos`.
""")
attach_docstr("count_nonzero", r"""count_nonzero(dim=None) -> Tensor

Counts the number of non-zero values in the tensor input along the given dim. If no dim is specified then all non-zeros in the tensor are counted.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    dim (Union[None, int, tuple(int), list(int)], optional): The dimension to reduce. Default value: ``None``, which indicates that the number of non-zero elements is calculated. If `dim` is ``None``, all elements in the tensor are summed up.
          
Returns:
    Tensor, number of nonzero element across dim specified by `dim`.

Raises:
    TypeError: If `dim` is not int, tuple(int), list(int) or None.
    ValueError: If any value in `dim` is not in range :math:`[-self.ndim, self.ndim)`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> import mindspore
    >>> # case 1: each value specified.
    >>> x = Tensor(np.array([[0, 1, 0], [1, 1, 0]]).astype(np.float32))
    >>> nonzero_num = x.count_nonzero(dim=[0, 1])
    >>> print(nonzero_num)
    [[3]]
    >>> # case 2: all value is default.
    >>> nonzero_num = x.count_nonzero()
    >>> print(nonzero_num)
    3
    >>> # case 3: dim value was specified 0.
    >>> nonzero_num = x.count_nonzero(dim=[0,])
    >>> print(nonzero_num)
    [1 2 0]
    >>> # case 4: dim value was specified 1.
    >>> nonzero_num = x.count_nonzero(dim=[1,])
    >>> print(nonzero_num)
    [1 2]

.. method:: Tensor.count_nonzero(axis=(), keep_dims=False, dtype=None) -> Tensor
  :noindex:

Count number of nonzero elements across axis of input tensor.

Args:
    axis (Union[int, tuple(int), list(int)], optional): The dimensions to reduce.
        Default: ``()`` , reduce all dimensions.
    keep_dims (bool, optional): Whether to maintain dimensions specified by `axis`.
        If true, keep these reduced dimensions and the length is 1.
        If false, don't keep these dimensions. Default: ``False`` .
    dtype (Union[Number, mindspore.bool], optional): The data type of the output tensor.
        Default: ``None`` .

Returns:
    Tensor, number of nonzero element across axis specified by `axis`.
    The data type is specified by `dtype`.

Raises:
    TypeError: If `axis` is not int, tuple or list.
    ValueError: If any value in `axis` is not in range :math:`[-self.ndim, self.ndim)`.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> import mindspore
    >>> # case 1: each value specified.
    >>> x = Tensor(np.array([[0, 1, 0], [1, 1, 0]]).astype(np.float32))
    >>> nonzero_num = x.count_nonzero(x=x, axis=[0, 1], keep_dims=True, dtype=mindspore.int32)
    >>> print(nonzero_num)
    [[3]]
    >>> # case 2: all value is default.
    >>> nonzero_num = x.count_nonzero()
    >>> print(nonzero_num)
    3
    >>> # case 3: axis value was specified 0.
    >>> nonzero_num = x.count_nonzero(axis=[0,])
    >>> print(nonzero_num)
    [1 2 0]
    >>> # case 4: axis value was specified 1.
    >>> nonzero_num = x.count_nonzero(axis=[1,])
    >>> print(nonzero_num)
    [1 2]
    >>> # case 5: keep_dims value was specified.
    >>> nonzero_num = x.count_nonzero(keep_dims=True)
    >>> print(nonzero_num)
    [[3]]
    >>> # case 6: keep_dims and axis value was specified.
    >>> nonzero_num = x.count_nonzero(axis=[0,], keep_dims=True)
    >>> print(nonzero_num)
    [[1 2 0]]""")
attach_docstr("clone", r"""clone() -> Tensor

Returns a copy of self.

.. warning::
    This is an experimental API that is subject to change or deletion.

Note:
    This function is differentiable, and gradients will flow back directly from the calculation
    result of the function to the `self`.

Returns:
    Tensor, with the same data, shape and type as `self`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.ones((3,3)).astype("float32"))
    >>> output = input.clone()
    >>> print(output)
    [[1. 1. 1.]
     [1. 1. 1.]
     [1. 1. 1.]]
""")
attach_docstr("acosh", r"""acosh() -> Tensor

For details, please refer to :func:`mindspore.ops.acosh`.
""")
attach_docstr("true_divide", r"""Alias for Tensor.div() with :math:`rounding\_mode=None`.
For details, please refer to :func:`mindspore.ops.div`.
""")
attach_docstr("remainder", r"""remainder(other) -> Tensor

Computes the remainder of `self` divided by `other` element-wise. The result has the same sign as the divisor and
its absolute value is less than that of `other`.

Supports broadcasting to a common shape and implicit type promotion.

.. code:: python

    remainder(input, other) == input - input.div(other, rounding_mode="floor") * other

.. note::
    Complex inputs are not supported. At least one input need to be tensor, but not both are bool tensors.

    The dividend `self` is a tensor whose data type is
    `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
    `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.

Args:
    other (Union[Tensor, numbers.Number, bool]): The divisor is a numbers.Number or
        a bool or a tensor whose data type is number or bool when the dividend is a tensor.

Returns:
    Tensor, with dtype promoted and shape broadcasted.

Raises:
    TypeError: If `self` and `other` are not of types: (Tensor, Tensor), (Tensor, Number),
        (Tensor, bool), (Number, Tensor) or (bool, Tensor).
    ValueError: If `self` and `other` are not broadcastable.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([-4.0, 5.0, 6.0]).astype(np.float32))
    >>> y = Tensor(np.array([3.0, 2.0, 3.0]).astype(np.float64))
    >>> output = x.remainder(y)
    >>> print(output)
    [2.  1.  0.]

.. method:: Tensor.remainder(divisor) -> Tensor
    :noindex:

Computes the remainder of dividing the first input tensor by the second input tensor element-wise.

Inputs of `self` and `divisor` comply with the implicit type conversion rules to make the data types consistent.
The inputs must be two tensors or one tensor and one scalar. When the inputs are two tensors,
both dtypes cannot be bool, and the shapes of them could be broadcast. When the inputs are one tensor
and one scalar, the scalar could only be a constant.

.. code:: python

    remainder(input, other) == input - input.div(other, rounding_mode="floor") * other

.. warning::
    - When the elements of input exceed 2048, there might be accuracy problems.
    - The calculation results of this operator on Ascend and CPU might be inconsistent.
    - If shape is expressed as (D1,D2... ,Dn), then D1\*D2... \*DN<=1000000,n<=8.

.. note::
    The first input `self` is a tensor whose data type is number.

Args:
    divisor (Union[Tensor, numbers.Number, bool]): When the first input is a tensor, The second input
        could be a number, a bool or a tensor whose data type is number.

Returns:
    Tensor, the shape is the same as the one after broadcasting,
    and the data type is the one with higher precision.

Raises:
    TypeError: If neither `self` nor `divisor` is one of the following: Tensor, Number, bool.
    ValueError: If the shape of `self` and `divisor` cannot be broadcasted to each other.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([-4.0, 5.0, 6.0]).astype(np.float16))
    >>> y = Tensor(np.array([3.0, 2.0, 3.0]).astype(np.float16))
    >>> output = x.remainder(divisor=y)
    >>> print(output)
    [2.  1.  0.]
""")
attach_docstr("mean", r"""mean(dim=None, keepdim=False, *, dtype=None) -> Tensor

Reduces all dimension of a tensor by averaging all elements in the dimension, by default.
And reduce a dimension of `self` along the specified `dim`. `keepdim`
determines whether the dimensions of the output and self are the same.

Note:
    The `dim` with tensor type is only used for compatibility with older versions and is not recommended.

Args:
    dim (Union[int, tuple(int), list(int), Tensor], optional): The dimensions to reduce. Default: ``None`` ,
        reduce all dimensions. Only constant value is allowed. Assume the rank of `self` is r,
        and the value range is [-r,r).
    keepdim (bool, optional): If ``True`` , keep these reduced dimensions and the length is 1.
        If ``False`` , don't keep these dimensions. Default: ``False`` .

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The desired data type of returned Tensor. Default: ``None`` .

Returns:
    Tensor, has the same data type as self tensor.

    - If `dim` is ``None`` , and `keepdim` is ``False`` ,
      the output is a 0-D tensor representing the product of all elements in the self tensor.
    - If `dim` is int, set as 1, and `keepdim` is ``False`` ,
      the shape of output is :math:`(x_0, x_2, ..., x_R)`.
    - If `dim` is tuple(int), set as (1, 2), and `keepdim` is ``False`` ,
      the shape of output is :math:`(x_0, x_3, ..., x_R)`.
    - If `dim` is 1-D Tensor, set as [1, 2], and `keepdim` is ``False`` ,
      the shape of output is :math:`(x_0, x_3, ..., x_R)`.

Raises:
    TypeError: If `dim` is not one of the following: int, tuple, list or Tensor.
    TypeError: If `keepdim` is not a bool.
    ValueError: If `dim` is out of range.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.random.randn(3, 4, 5, 6).astype(np.float32))
    >>> output = Tensor.mean(x, 1, keepdim=True)
    >>> result = output.shape
    >>> print(result)
    (3, 1, 5, 6)
    >>> # case 1: Reduces a dimension by averaging all elements in the dimension.
    >>> x = Tensor(np.array([[[2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2], [2, 2, 2, 2, 2, 2]],
    ... [[4, 4, 4, 4, 4, 4], [5, 5, 5, 5, 5, 5], [6, 6, 6, 6, 6, 6]],
    ... [[6, 6, 6, 6, 6, 6], [8, 8, 8, 8, 8, 8], [10, 10, 10, 10, 10, 10]]]),
    ... mindspore.float32)
    >>> output = Tensor.mean(x)
    >>> print(output)
    5.0
    >>> print(output.shape)
    ()
    >>> # case 2: Reduces a dimension along the dim 0
    >>> output = Tensor.mean(x, 0, True)
    >>> print(output)
    [[[4. 4. 4. 4. 4. 4.]
      [5. 5. 5. 5. 5. 5.]
      [6. 6. 6. 6. 6. 6.]]]
    >>> # case 3: Reduces a dimension along the dim 1
    >>> output = Tensor.mean(x, 1, True)
    >>> print(output)
    [[[2. 2. 2. 2. 2. 2.]]
     [[5. 5. 5. 5. 5. 5.]]
     [[8. 8. 8. 8. 8. 8.]]]
    >>> # case 4: Reduces a dimension along the dim 2
    >>> output = Tensor.mean(x, 2, True)
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

.. method:: Tensor.mean(axis=None, keep_dims=False) -> Tensor
    :noindex:

For details, please refer to :func:`mindspore.ops.mean` .
""")
attach_docstr("ge", r"""ge(other) -> Tensor

Alias for :func:`mindspore.Tensor.greater_equal`.
""")
attach_docstr("floor_divide_", r"""floor_divide_(other) -> Tensor

Divides the self tensor by the other tensor element-wise and round down to the closest integer.

.. math::
    out_{i} = \text{floor}( \frac{self_i}{other_i})

where the :math:`floor` indicates the Floor operator. For more details,
please refer to the :class:`mindspore.mint.floor` operator.

.. warning::
    This is an experimental API that is subject to change or deletion.

Note:
    When `self` and `other` have different shapes, `other` should be able to broadcast to `self`.

Args:
    other (Union[Tensor, Number, bool]): The other input is a number or
        a bool or a tensor whose data type is number or bool.

Returns:
    Tensor, the shape is the same as `self` , and the data type is the same as `self` .

Raises:
    TypeError: If `other` is not one of the following: Tensor, number.Number or bool.
    RuntimeError: If `other` cannot be broadcast to `self`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> x = Tensor(np.array([2, 4, -1]), mindspore.int32)
    >>> other = Tensor(np.array([3, 3, 3]), mindspore.int32)
    >>> output = x.floor_divide_(other)
    >>> print(output)
    [ 0  1 -1]
    >>> print(x)
    [ 0  1 -1]
""")
attach_docstr("masked_scatter", r"""masked_scatter(mask, source) -> Tensor

Returns a Tensor. Updates the value in the "self Tensor" with the `tensor` value according to the mask.
The shape of `mask` and the shape of the "self Tensor" must be the same or `mask` is broadcastable.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    mask (Tensor[bool]): A bool tensor with a shape broadcastable to the "self Tensor".
    source (Tensor): A tensor with the same data type as the "self Tensor". The number
        of elements must be greater than or equal to the number of True's in `mask`.

Returns:
    Tensor, with the same type and shape as the "self Tensor".

Raises:
    TypeError: If `mask` or `source` is not a Tensor.
    TypeError: If data type of the "self Tensor" is not be supported.
    TypeError: If dtype of `mask` is not bool.
    TypeError: If the dim of the "self Tensor" is less than the dim of `mask`.
    ValueError: If `mask` can not be broadcastable to the "self Tensor".
    ValueError: If the number of elements in `source` is less than the number of elements to be updated in the tensor.

Supported Platforms:
    ``Ascend`` ``CPU``

Examples:
    >>> import numpy as np
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> source = Tensor(np.array([1., 2., 3., 4.]), mindspore.float32)
    >>> mask = Tensor(np.array([True, True, False, True]), mindspore.bool_)
    >>> tensor = Tensor(np.array([5., 6., 7.]), mindspore.float32)
    >>> output = source.masked_scatter(mask, tensor)
    >>> print(output)
    [5. 6. 3. 7.]""")
attach_docstr("remainder_", r"""remainder_(other) -> Tensor

Computes the remainder of `self` divided by `other` element-wise. The result has the same sign as the divisor `other`
and its absolute value is less than that of `other`.

.. code-block::

    remainder(self, other) == self - self.div(other, rounding_mode="floor") * other

.. warning::
    This is an experimental API that is subject to change or deletion.

Note:
    - Complex inputs are not supported.
    - The dividend `self` is a tensor whose data type is
      `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
    - When `self` and `other` have different shapes, `other` should be able to broadcast to a `self`.

Args:
    other (Union[Tensor, number, bool]): The divisor is a number or
        a bool or a tensor whose data type is number or bool.

Returns:
    Tensor, the shape and the data type are the same as those of `self` .

Raises:
    RuntimeError: If `other` cannot be broadcast to `self`.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> import numpy as np
    >>> x = Tensor(np.array([2, 4, -1]), mindspore.int32)
    >>> other = Tensor(np.array([3, -6, -2]), mindspore.int32)
    >>> output = x.remainder_(other)
    >>> print(output)
    [ 2 -2 -1]
    >>> print(x)
    [ 2 -2 -1]
""")
attach_docstr("abs", r"""abs() -> Tensor

For details, please refer to :func:`mindspore.ops.abs`.
""")
attach_docstr("subtract", r"""subtract(other, *, alpha=1) -> Tensor

This interface is deprecated from version 2.4 and will be removed in a future version.
""")
attach_docstr("baddbmm", r"""baddbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor

For details, please refer to :func:`mindspore.ops.baddbmm`.""")
attach_docstr("exp_", r"""exp_() -> Tensor

Inplace version of :func:`mindspore.Tensor.exp`.

.. warning::
    This is an experimental API that is subject to change or deletion.
""")
attach_docstr("isneginf", r"""isneginf() -> Tensor

For details, please refer to :func:`mindspore.ops.isneginf`.
""")
attach_docstr("floor", r"""floor() -> Tensor

For details, please refer to :func:`mindspore.ops.floor`.""")
attach_docstr("add_", r"""add_(other) -> Tensor

In-place version of :func:`mindspore.Tensor.add`.""")
attach_docstr("asin", r"""asin() -> Tensor

For details, please refer to :func:`mindspore.ops.asin`.
""")
attach_docstr("new_ones", r"""new_ones(size, dtype=None) -> Tensor

Return a tensor of `size` filled with ones.

Args:
    size (Union[int, tuple(int), list(int)]): An int, list or tuple of integers defining the output shape.
    dtype (:class:`mindspore.dtype`, optional): The desired dtype of the output tensor. If None, the returned
        tensor has the same dtype as `self`. Default: ``None``.

Returns:
    Tensor, the shape and dtype is defined above and filled with ones.

Raises:
    TypeError: If `size` is neither an int nor a tuple/list of int.
    TypeError: If `dtype` is not a MindSpore dtype.
    ValueError: If `size` contains negative values.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> x = Tensor((), mindspore.int32)
    >>> x.new_ones((2, 3))
    Tensor(shape=[2, 3], dtype=Int32, value=
    [[1, 1, 1],
     [1, 1, 1]])
""")
attach_docstr("outer", r"""outer(vec2) -> Tensor

For details, please refer to :func:`mindspore.ops.outer`.
""")
attach_docstr("__isub__", r"""__isub__(other, *, alpha=1) -> Tensor

Alias for :func:`mindspore.Tensor.sub` of `mindspore.Tensor.sub(other, *, alpha=1)`.

.. method:: Tensor.__isub__(y) -> Tensor
    :noindex:

Alias for :func:`mindspore.Tensor.sub` of `mindspore.Tensor.sub(y)`.
""")
attach_docstr("sqrt", r"""sqrt() -> Tensor

For details, please refer to :func:`mindspore.ops.sqrt`.
""")
attach_docstr("cos", r"""cos() -> Tensor

For details, please refer to :func:`mindspore.ops.cos`.""")
attach_docstr("reciprocal", r"""reciprocal() -> Tensor

For details, please refer to :func:`mindspore.ops.reciprocal`.
""")
attach_docstr("__pow__", r"""__pow__() -> Tensor

Alias for :func:`mindspore.Tensor.pow`.
""")
attach_docstr("logaddexp", r"""logaddexp(other) -> Tensor

For details, please refer to :func:`mindspore.ops.logaddexp`.
""")
attach_docstr("log2", r"""log2() -> Tensor

For details, please refer to :func:`mindspore.ops.log2`.
""")
attach_docstr("pow", r"""pow(exponent) -> Tensor

For details, please refer to :func:`mindspore.ops.pow`.
""")
attach_docstr("take", r"""take(indices, axis=None, mode='clip') -> Tensor

Takes elements from a tensor along an axis.

Args:
    indices (Tensor): The indices with shape :math:`(Nj...)` of the values to extract.
    axis (int, optional): The axis over which to select values. By default,
        the flattened input tensor is used. Default: ``None`` .
    mode (str, optional): Support ``'raise'``, ``'wrap'``, ``'clip'``.

        - ``raise``: Raises an error;

        - ``wrap``: Wraps around;

        - ``clip``: Clips to the range. ``'clip'`` mode means that all indices that are
          too large are replaced by the index that addresses the last element
          along that axis. Note that this disables indexing with negative numbers.

        Default: ``'clip'`` .

Returns:
    Tensor, the indexed result.

Raises:
    ValueError: If `axis` is out of range, or `mode` has values other than ('raise', 'wrap', 'clip').

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> a = Tensor(np.array([4, 3, 5, 7, 6, 8]))
    >>> indices = Tensor(np.array([0, 1, 4]))
    >>> output = a.take(indices)
    >>> print(output)
    [4 3 6]

.. method:: Tensor.take(index) -> Tensor
    :noindex:

Select the self element at the given index.

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    index (LongTensor): The index tensor of self tensor.

Returns:
    Tensor, has the same data type as index tensor.

Raises:
    TypeError: If the dtype of `index` is not long type.

Examples:
    >>> import mindspore as ms
    >>> from mindspore import Tensor
    >>> input = Tensor([[4, 3, 5],[6, 7, 8]], ms.float32)
    >>> index = Tensor([0, 2, 5], ms.int64)
    >>> output = input.take(index)
    >>> print(output)
    [4, 5, 8]""")
attach_docstr("lt", r"""lt(other) -> Tensor

For more details, please refer to :func:`mindspore.Tensor.less`.
""")
attach_docstr("sigmoid", r"""sigmoid() -> Tensor

For details, please refer to :func:`mindspore.ops.sigmoid`.""")
attach_docstr("addbmm", r"""addbmm(batch1, batch2, *, beta=1, alpha=1) -> Tensor

For details, please refer to :func:`mindspore.ops.addbmm`.""")
attach_docstr("logical_xor", r"""logical_xor(other) -> Tensor

Computes the "logical XOR" of two tensors element-wise.

.. math::
    out_{i} = self_{i} \oplus other_{i}

.. note::
    - `self` and `other` comply with the type conversion rules to make the data types consistent.
    - When the `other` is bool, it could only be a constant.

Args:
    other (Union[Tensor, bool]): A bool or a tensor whose data type can be implicitly converted to bool.

Returns:
    Tensor, the shape is the same as the `self` and `other` after broadcasting, and the data type is bool.

Supported Platforms:
    ``Ascend`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([True, False, True]), mindspore.bool)
    >>> other = Tensor(np.array([True, True, False]), mindspore.bool)
    >>> output = input.logical_xor(other)
    >>> print(output)
    [ False True True]
    >>> x = Tensor(1, mindspore.bool)
    >>> other = Tensor(0, mindspore.bool)
    >>> output = input.logical_xor(other)
    >>> print(output)
    True
""")
attach_docstr("sinc", r"""sinc() -> Tensor

For details, please refer to :func:`mindspore.ops.sinc`.
""")
attach_docstr("allclose", r"""allclose(other, rtol=1e-05, atol=1e-08, equal_nan=False) -> Tensor

Returns a new Tensor with boolean elements representing if each element of `self`
is "close" to the corresponding element of `other`. Closeness is defined as:

.. math::
    |self-other| <= atol + rtol x |other|

.. warning::
    This is an experimental API that is subject to change or deletion.

Args:
    other (Tensor): Tensor to compare. Dtype must be same as `self`.
    rtol (Union[float, int, bool], optional): Relative tolerance. Default: ``1e-05`` .
    atol (Union[float, int, bool], optional): Absolute tolerance. Default: ``1e-08`` .
    equal_nan (bool, optional): If ``True`` , then two NaNs will be considered equal. Default: ``False``.

Returns:
    A bool Scalar.

Raises:
    TypeError: `self` or `other` is not Tensor.
    TypeError: Data types of `self` and `other` are not in the list of supported types.
    TypeError: `atol` or `rtol` is not float, int or bool.
    TypeError: `equal_nan` is not bool.
    TypeError: `self` and `other` have different dtypes.
    ValueError: `self` and `other` cannot broadcast.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> input = Tensor(np.array([1.3, 2.1, 3.2, 4.1, 5.1]), mindspore.float16)
    >>> other = Tensor(np.array([1.3, 3.3, 2.3, 3.1, 5.1]), mindspore.float16)
    >>> output = input.allclose(other)
    >>> print(output)
    False
""")
attach_docstr("triu", r"""triu(diagonal=0) -> Tensor

For details, please refer to :func:`mindspore.ops.triu`.
""")
attach_docstr("unbind", r"""unbind(dim=0) -> Tensor

For details, please refer to :func:`mindspore.ops.unbind`.
""")
attach_docstr("nansum", r"""nansum(dim=None, keepdim=False, *, dtype=None) -> Tensor

Computes sum of input Tensor over a given dimension, treating NaNs as zero.

.. warning::
    - It is only supported on Atlas A2 Training Series Products.
    - This is an experimental API that is subject to change or deletion.

Args:
    dim (Union[int, tuple(int)], optional): The dimensions to sum.
        Dim must be in the range [-rank(self), rank(self)). Default: ``None``, which indicates the sum of all elements in a tensor.
    keepdim (bool, optional): Whether the output Tensor keeps dimensions or not. Default: ``False``, indicating that no dimension is kept.

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The dtype of output Tensor. Default: ``None``.

Returns:
    Tensor, the sum of input Tensor in the given dimension dim, treating NaNs as zero.

    - If dim is None, keepdim is False,
      the output is a 0-D Tensor representing the sum of all elements in the self Tensor.
    - If dim is int, set as 2, and keepdim is False,
      the shape of output is :math:`(self_1, self_3, ..., self_R)`.
    - If dim is tuple(int) or list(int), set as (2, 3), and keepdim is False,
      the shape of output is :math:`(self_1, self_4, ..., self_R)`.

Raises:
    TypeError: If `keepdim` is not a bool.
    TypeError: If the dtype of `self` or `dtype` is complex type.
    ValueError: If `dim` is not in [-rank(self), rank(self)).

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[float("nan"), 2, 3], [1, 2, float("nan")]]), mindspore.float32)
    >>> output1 = x.nansum(dim=0, keepdim=False, dtype=mindspore.float32)
    >>> output2 = x.nansum(dim=0, keepdim=True, dtype=mindspore.float32)
    >>> print(output1)
    [1. 4. 3.]
    >>> print(output2)
    [[1. 4. 3.]]

.. method:: Tensor.nansum(axis=None, keepdims=False, *, dtype=None) -> Tensor
    :noindex:

Computes sum of `input` over a given dimension, treating NaNs as zero.

Args:
    axis (Union[int, tuple(int)], optional): The dimensions to reduce. Supposed the rank of `self` is r,
        axis must be in the range [-r,r). Default: ``None``, all dimensions are reduced.
    keepdims (bool, optional): Whether the output Tensor keeps dimensions or not. Default: ``False``.

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The dtype of output Tensor. Default: ``None``.

Returns:
    Tensor, the sum of input Tensor in the given dimension dim, treating NaNs as zero.

    - If axis is None, keepdims is False,
      the output is a 0-D Tensor representing the sum of all elements in the input Tensor.
    - If axis is int, set as 2, and keepdims is False,
      the shape of output is :math:`(self_1, self_3, ..., self_R)`.
    - If axis is tuple(int) or list(int), set as (2, 3), and keepdims is False,
      the shape of output is :math:`(self_1, self_4, ..., self_R)`.

Raises:
    TypeError: If `keepdims` is not a bool.
    TypeError: If the dtype of `self` or `dtype` is complex type.
    ValueError: If `axis` not in [-rank(self), rank(self)).

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[float("nan"), 2, 3], [1, 2, float("nan")]]), mindspore.float32)
    >>> output1 = x.nansum(axis=0, keepdims=False, dtype=mindspore.float32)
    >>> output2 = x.nansum(axis=0, keepdims=True, dtype=mindspore.float32)
    >>> print(output1)
    [1. 4. 3.]
    >>> print(output2)
    [[1. 4. 3.]]""")
attach_docstr("cumsum", r"""cumsum(dim, *, dtype=None) -> Tensor

Computes the cumulative sum of self Tensor along `dim`.

.. math::

    y_i = x_1 + x_2 + x_3 + ... + x_i

Args:
    dim (int): Dim along which the cumulative sum is computed.

Keyword Args:
    dtype (:class:`mindspore.dtype`, optional): The desired dtype of returned Tensor. If specified,
        the self Tensor will be cast to `dtype` before the computation. This is useful for preventing overflows.
        If not specified, stay the same as original Tensor. Default: ``None`` .

Returns:
    Tensor, the shape of the output Tensor is consistent with the self Tensor's.

Raises:
    ValueError: If the `dim` is out of range.

Supported Platforms:
    ``Ascend``

Examples:
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[3, 4, 6, 10], [1, 6, 7, 9], [4, 3, 8, 7], [1, 3, 7, 9]]).astype(np.float32))
    >>> # case 1: along the dim 0
    >>> y = x.cumsum(dim=0)
    >>> print(y)
    [[ 3.  4.  6. 10.]
     [ 4. 10. 13. 19.]
     [ 8. 13. 21. 26.]
     [ 9. 16. 28. 35.]]
    >>> # case 2: along the dim 1
    >>> y = x.cumsum(dim=1)
    >>> print(y)
    [[ 3.  7. 13. 23.]
     [ 1.  7. 14. 23.]
     [ 4.  7. 15. 22.]
     [ 1.  4. 11. 20.]]

.. method:: Tensor.cumsum(axis=None, dtype=None) -> Tensor
    :noindex:

Computes the cumulative sum of self Tensor along `axis`.

.. math::

    y_i = x_1 + x_2 + x_3 + ... + x_i

Note:
    On Ascend, the dtype of `self` only supports :int8, uint8, int32, float16 or float32 in case of static shape.
    For the case of dynamic shape, the dtype of `self` only supports int32, float16 or float32.

Args:
    axis (int): Axis along which the cumulative sum is computed.
    dtype (:class:`mindspore.dtype`, optional): The desired dtype of returned Tensor. If specified,
        the self Tensor will be cast to `dtype` before the computation. This is useful for preventing overflows.
        If not specified, stay the same as original Tensor. Default: ``None`` .

Returns:
    Tensor, the shape of the output Tensor is consistent with the self Tensor's.

Raises:
    ValueError: If the axis is out of range.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> import numpy as np
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([[3, 4, 6, 10], [1, 6, 7, 9], [4, 3, 8, 7], [1, 3, 7, 9]]).astype(np.float32))
    >>> # case 1: along the axis 0
    >>> y = x.cumsum(axis=0)
    >>> print(y)
    [[ 3.  4.  6. 10.]
     [ 4. 10. 13. 19.]
     [ 8. 13. 21. 26.]
     [ 9. 16. 28. 35.]]
    >>> # case 2: along the axis 1
    >>> y = x.cumsum(axis=1)
    >>> print(y)
    [[ 3.  7. 13. 23.]
     [ 1.  7. 14. 23.]
     [ 4.  7. 15. 22.]
     [ 1.  4. 11. 20.]]
""")
attach_docstr("argmin", r"""argmin(axis=None, keepdims=False) -> Tensor

Returns the indices of the minimum values along the given axis of the tensor.

Args: 
    axis (Union[int, None], optional): Specify the axis for computation. If ``None`` , compute all elements in the
        tensor. Default ``None`` .
    keepdims (bool, optional): Whether the output tensor has dim retained. Default ``False`` .

Returns:
    Tensor

Supported Platforms:
   ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[2, 5, 1, 6],
    ...                       [3, -7, -2, 4],
    ...                       [8, -4, 1, -3]])
    >>> # case 1: By default, compute the minimum of all elements.
    >>> x.argmin()
    Tensor(shape=[], dtype=Int32, value= 5)
    >>>
    >>> # case 2: Compute the minimum along axis 1.
    >>> x.argmin(axis=1)
    Tensor(shape=[3], dtype=Int32, value= [2, 1, 1])
    >>>
    >>> # case 3: If keepdims=True, the output shape will be same of that of the input.
    >>> x.argmin(axis=1, keepdims=True)
    Tensor(shape=[3, 1], dtype=Int32, value=
    [[2],
     [1],
     [1]])

.. method:: Tensor.argmin(dim=None, keepdim=False) -> Tensor
    :noindex:

Returns the indices of the minimum values along the given axis of the tensor.

Args:
    dim (Union[int, None], optional): Specify the axis for computation. If ``None`` , compute all elements in the
        tensor.
    keepdim (bool, optional): Whether the output tensor has dim retained.

Returns:
    Tensor

Supported Platforms:
    ``Ascend``

Examples:
    >>> import mindspore
    >>> x = mindspore.tensor([[2, 5, 1, 6],
    ...                       [3, -7, -2, 4],
    ...                       [8, -4, 1, -3]])
    >>> # case 1: By default, compute the minimum of all elements.
    >>> x.argmin()
    Tensor(shape=[], dtype=Int32, value= 5)
    >>>
    >>> # case 2: Compute the minimum along dim 1.
    >>> x.argmin(dim=1)
    Tensor(shape=[3], dtype=Int32, value= [2, 1, 1])
    >>>
    >>> # case 3: If keepdim=True, the output shape will be same of that of the input.
    >>> x.argmin(dim=1, keepdim=True)
    Tensor(shape=[3, 1], dtype=Int32, value=
    [[2],
     [1],
     [1]])
""")
attach_docstr("inverse", r"""inverse() -> Tensor

For details, please refer to :func:`mindspore.ops.inverse`.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``
""")
attach_docstr("log_", r"""log_() -> Tensor

Inplace version of :func:`mindspore.Tensor.log`.

.. warning::
    This is an experimental API that is subject to change or deletion.
""")
attach_docstr("sub", r"""sub(other, *, alpha=1) -> Tensor

Subtracts scaled other value from self Tensor.

.. math::

    out_{i} = self_{i} - alpha \times other_{i}

Note:
    - When the two inputs have different shapes,
      they must be able to broadcast to a common shape.
    - The two inputs and alpha comply with the implicit type conversion rules to make the data types
      consistent.

Args:
    other (Union[Tensor, number.Number, bool]): The second self, is a number.Number or
        a bool or a tensor whose data type is
        `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
        `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.

Keyword Args:
    alpha (number.Number, optional): A scaling factor applied to `other`, default ``1``.

Returns:
    Tensor with a shape that is the same as the broadcasted shape of the self `self` and `other`,
    and the data type is the one with higher precision or higher digits among the two inputs and alpha.

Raises:
    TypeError: If the type of `other` or `alpha` is not one of the following: Tensor, number.Number, bool.
    TypeError: If `alpha` is of type float but `self` and `other` are not of type float.
    TypeError: If `alpha` is of type bool but `self` and `other` are not of type bool.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> x = Tensor(np.array([4, 5, 6]).astype(np.float32))
    >>> y = Tensor(1, mindspore.int32)
    >>> output = Tensor.sub(x, y, alpha=0.5)
    >>> print(output)
    [3.5 4.5 5.5]
    >>> # the data type of x is float32, the data type of y is int32,
    >>> # alpha is a float, and the output is the data format of higher precision float32.
    >>> print(output.dtype)
    Float32


.. method:: Tensor.sub(y) -> Tensor
    :noindex:

For details, please refer to :func:`mindspore.ops.sub` .
""")
attach_docstr("reshape", r"""reshape(*shape) -> Tensor

For details, please refer to :func:`mindspore.ops.reshape`.
""")
attach_docstr("logsumexp", r"""logsumexp(dim, keepdim=False) -> Tensor

For details, please refer to :func:`mindspore.ops.logsumexp`.
""")
attach_docstr("fmod", r"""fmod(other) -> Tensor

For details, please refer to :func:`mindspore.ops.fmod`.""")
attach_docstr("isfinite", r"""isfinite() -> Tensor

For details, please refer to :func:`mindspore.ops.isfinite`.
""")
attach_docstr("ceil", r"""ceil() -> Tensor

For details, please refer to :func:`mindspore.ops.ceil`.""")
attach_docstr("minimum", r"""minimum(other) -> Tensor

For details, please refer to :func:`mindspore.ops.minimum`.""")
attach_docstr("add", r"""add(other) -> Tensor

Adds other value to `self` element-wise.

.. math::

    out_{i} = self_{i} + other_{i}

Note:
    - When `self` and `other` have different shapes,
      they must be able to broadcast to a common shape.
    - `self` and `other` can not be bool type at the same time,
      [True, Tensor(True), Tensor(np.array([True]))] are all considered bool type.
    - `self` and `other` comply with the implicit type conversion rules to make the data types
      consistent.
    - The dimension of `self` should be greater than or equal to 1.

Args:
    other (Union[Tensor, number.Number, bool]): `other` is a number.Number or a bool or a tensor whose data type is
        `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
        `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.

Returns:
    Tensor with a shape that is the same as the broadcasted shape of `self` and `other`,
    and the data type is the one with higher precision or higher digits between `self` and `other`.

Raises:
    TypeError: If `other` is not one of the following: Tensor, number.Number, bool.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> # case 1: x and y are both Tensor.
    >>> x = Tensor(np.array([1, 2, 3]).astype(np.float32))
    >>> y = Tensor(np.array([4, 5, 6]).astype(np.float32))
    >>> output = Tensor.add(x, y)  # x.add(y)
    >>> print(output)
    [5. 7. 9.]
    >>> # case 2: x is a scalar and y is a Tensor
    >>> x = Tensor(1, mindspore.int32)
    >>> y = Tensor(np.array([4, 5, 6]).astype(np.float32))
    >>> output = Tensor.add(x, y)  # x.add(y)
    >>> print(output)
    [5. 6. 7.]
    >>> # the data type of x is int32, the data type of y is float32,
    >>> # and the output is the data format of higher precision float32.
    >>> print(output.dtype)
    Float32

.. method:: Tensor.add(other, *, alpha=1) -> Tensor
    :noindex:

Adds scaled other value to `self`.

.. math::

    out_{i} = self_{i} + alpha \times other_{i}

Note:
    - When `self` and `other` have different shapes,
      they must be able to broadcast to a common shape.
    - `self`, `other` and alpha comply with the implicit type conversion rules to make the data types
      consistent.

Args:
    other (Union[Tensor, number.Number, bool]): `other` is a number.Number or a bool or a tensor whose data type is
        `number <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_ or
        `bool <https://www.mindspore.cn/docs/en/master/api_python/mindspore/mindspore.dtype.html>`_.
    
Keyword Args:
    alpha (number.Number): A scaling factor applied to `other`, default 1.

Returns:
    Tensor with a shape that is the same as the broadcasted shape of the `self` and `other`,
    and the data type is the one with higher precision or higher digits among `self`, `other` and `alpha`.

Raises:
    TypeError: If the type of `other` or `alpha` is not one of the following: Tensor, number.Number, bool.
    TypeError: If `alpha` is of type float but `self` and `other` are not of type float.
    TypeError: If `alpha` is of type bool but `self` and `other` are not of type bool.

Supported Platforms:
    ``Ascend`` ``GPU`` ``CPU``

Examples:
    >>> import numpy as np
    >>> import mindspore
    >>> from mindspore import Tensor
    >>> x = Tensor(1, mindspore.int32)
    >>> y = Tensor(np.array([4, 5, 6]).astype(np.float32))
    >>> alpha = 0.5
    >>> output = Tensor.add(x, y, alpha=alpha)  # x.add(y, alpha=alpha)
    >>> print(output)
    [3. 3.5 4.]
    >>> # the data type of x is int32, the data type of y is float32,
    >>> # alpha is a float, and the output is the data format of higher precision float32.
    >>> print(output.dtype)
    Float32
""")
attach_docstr("erfc", r"""erfc() -> Tensor

For details, please refer to :func:`mindspore.ops.erfc`.""")
attach_docstr("not_equal", r"""not_equal(other) -> Tensor

For details, please refer to :func:`mindspore.ops.ne`.
""")
