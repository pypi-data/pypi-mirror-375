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
"""activation layer for mint"""
from __future__ import absolute_import
from __future__ import division

from mindspore import mint
from mindspore.nn.cell import Cell


class SiLU(Cell):
    r"""
    Calculates the SiLU activation function element-wise. It is also sometimes referred to as Swish
    function.

    The SiLU function is defined as follows:

    .. math::

        \text{SiLU}(x) = x * \sigma(x),

    where :math:`x_i` is an element of the input, :math:`\sigma(x)` is Sigmoid function.

    .. math::

        \text{sigmoid}(x_i) = \frac{1}{1 + \exp(-x_i)},

    SiLU Activation Function Graph:

    .. image:: ../images/SiLU.png
        :align: center

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        inplace (bool, optional): If it is ``True``, enable the in-place update function.
            Default value: ``False``.

    Inputs:
        - **input** (Tensor) - `input` is :math:`x` in the preceding formula.
          Input with the data type float16 or float32. Tensor of any dimension.

    Outputs:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is neither float16 nor float32.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, mint
        >>> import numpy as np
        >>> input = Tensor(np.array([-1, 2, -3, 2, -1]), mindspore.float16)
        >>> silu = mint.nn.SiLU(inplace=False)
        >>> output = silu(input)
        >>> print(output)
        [-0.269  1.762  -0.1423  1.762  -0.269]
    """

    def __init__(self, inplace=False):
        """Initialize SiLU."""
        super(SiLU, self).__init__()
        self.inplace = inplace

    def construct(self, x):
        return mint.nn.functional.silu(x, self.inplace)


class Sigmoid(Cell):
    r"""
    Applies sigmoid activation function element-wise.

    Sigmoid function is defined as:

    .. math::

        \text{sigmoid}(x_i) = \frac{1}{1 + \exp(-x_i)},

    where :math:`x_i` is the element of `x`.

    Sigmoid Activation Function Graph:

    .. image:: ../images/Sigmoid.png
        :align: center

    Inputs:
        - **input** (Tensor) - `input` is :math:`x` in the preceding formula. Tensor of any dimension,
          the data type is float16, float32, float64, complex64 or complex128.

    Outputs:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is not float16, float32, float64, complex64 or complex128.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend`` ``GPU`` ``CPU``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, nn
        >>> import numpy as np
        >>> input = Tensor(np.array([-1, -2, 0, 2, 1]), mindspore.float16)
        >>> sigmoid = mint.nn.Sigmoid()
        >>> output = sigmoid(input)
        >>> print(output)
        [0.2688  0.11914 0.5     0.881   0.7305 ]
    """
    def __init__(self):
        """Initialize LogSigmoid."""
        super(Sigmoid, self).__init__()

    def construct(self, input):
        return mint.nn.functional.sigmoid(input)


class LogSigmoid(Cell):
    r"""
    Applies logsigmoid activation element-wise. The input is a Tensor with any valid shape.

    Logsigmoid is defined as:

    .. math::
        \text{LogSigmoid}(x_{i}) = \log(\frac{1}{1 + \exp(-x_i)}),

    where :math:`x_{i}` is the element of the input.

    LogSigmoid Activation Function Graph:

    .. image:: ../images/LogSigmoid.png
        :align: center

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Inputs:
        - **input** (Tensor) - The input of LogSigmoid with data type of bfloat16, float16 or float32.
          The shape is :math:`(*)` where :math:`*` means, any number of additional dimensions.

    Outputs:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is not bfloat16, float16 and float32.
        TypeError: If `input` is not a Tensor.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor
        >>> net = mint.nn.LogSigmoid()
        >>> input = Tensor([1.0, 2.0, 3.0], mindspore.float32)
        >>> output = net(input)
        >>> print(output)
        [-0.31326166 -0.12692806 -0.04858734]
    """
    def __init__(self):
        """Initialize LogSigmoid."""
        super(LogSigmoid, self).__init__()

    def construct(self, input):
        return mint.nn.functional.logsigmoid(input)


class ELU(Cell):
    r"""
    Exponential Linear Unit activation function

    Applies the exponential linear unit function element-wise.The activation function is defined as:

    .. math::
        ELU_{i} =
        \begin{cases}
        x_i, &\text{if } x_i \geq 0; \cr
        \alpha * (\exp(x_i) - 1), &\text{otherwise.}
        \end{cases}

    where :math:`x_i` represents the element of the input and :math:`\alpha` represents the `alpha` parameter, and
    `alpha` represents the smoothness of the ELU.

    ELU Activation Function Graph:

    .. image:: ../images/ELU.png
        :align: center

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Args:
        alpha (float, optional): The alpha value of ELU, the data type is float. Default: ``1.0``.
        inplace (bool, optional): Whether to use inplace mode, the data type is bool. Default: ``False``.

    Inputs:
        - **input** (Tensor) - The input of ELU is a Tensor of any dimension.

    Outputs:
        Tensor, with the same shape and type as the `input`.

    Raises:
        RuntimeError: If the dtype of `input` is not float16, float32 or bfloat16.
        TypeError: If the dtype of `alpha` is not float.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, mint
        >>> import numpy as np
        >>> input = Tensor(np.array([-1, -2, 0, 2, 1]), mindspore.float32)
        >>> elu = mint.nn.ELU()
        >>> result = elu(input)
        >>> print(result)
        [-0.63212055  -0.86466473  0.  2.  1.]
    """

    def __init__(self, alpha=1.0, inplace=False):
        """Initialize ELU."""
        super(ELU, self).__init__()
        self.alpha = alpha
        self.inplace = inplace

    def construct(self, input):
        return mint.nn.functional.elu(input, self.alpha, self.inplace)


class GLU(Cell):
    r"""
    Computes GLU (Gated Linear Unit activation function) of the input tensor.

    .. math::
        {GLU}(a, b)= a \otimes \sigma(b)

    where :math:`a` is the first half of the `input` Tensor after `input` is split and :math:`b` is the second half.

    Here :math:`\sigma` is the sigmoid function, and :math:`\otimes` is the Hadamard product.
    See `Language Modeling with Gated Convluational Networks <https://arxiv.org/abs/1612.08083>`_ .

    Args:
        dim (int, optional): The dimension to split the input `input`. The value range is `[-r, r)` where `r`
            is the number of dimensions of `input`. Default: ``-1`` , the last dimension in `input`.

    Inputs:
        - **input** (Tensor) - Tensor to be calculated. Dtype is floating point and the shape
          is :math:`(\ast_1, N, \ast_2)` where `*` means, any number of additional dimensions. :math:`N`
          is required to be an even number, where :math:`N` is the size of `input` on the dimension
          selected by `dim`.

    Outputs:
        Tensor, the same dtype as the `input`, with the shape :math:`(\ast_1, M, \ast_2)` where :math:`M=N/2`.

    Raises:
        TypeError: If `input` is not a Tensor or `dim` is not an int.
        IndexError: If the value of `dim` is out of the range of `[-r, r)`, where `r` is the number
            of dimensions of `input`.
        RuntimeError: If dtype of `input` is not supported.
        RuntimeError: If the length of `input` in the dimension selected by `dim` is not even.

    Supported Platforms:
        ``Ascend`` ``CPU``

    Examples:
        >>> from mindspore import mint, Tensor
        >>> glu = mint.nn.GLU()
        >>> input = Tensor([[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]])
        >>> output = glu(input)
        >>> print(output)
        [[0.05744425 0.11973753]
         [0.33409387 0.41398472]]
    """

    def __init__(self, dim=-1):
        """Initialize GLU."""
        super().__init__("GLU")
        self.dim = dim

    def construct(self, input):
        return mint.nn.functional.glu(input, self.dim)


class Tanh(Cell):
    r"""
    Applies the Tanh function element-wise, returns a new tensor with the hyperbolic tangent of the elements of input.

    Tanh function is defined as:

    .. math::
        tanh(x_i) = \frac{\exp(x_i) - \exp(-x_i)}{\exp(x_i) + \exp(-x_i)} = \frac{\exp(2x_i) - 1}{\exp(2x_i) + 1},

    where :math:`x_i` is an element of the input Tensor.

    Tanh Activation Function Graph:

    .. image:: ../images/Tanh.png
        :align: center

    .. warning::
        This is an experimental API that is subject to change or deletion.

    Inputs:
        - **input** (Tensor) - Tensor of any dimension, input with data type of float16 or float32.

    Outputs:
        Tensor, with the same type and shape as the `input`.

    Raises:
        TypeError: If dtype of `input` is neither float16 nor float32.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, mint
        >>> import numpy as np
        >>> input = Tensor(np.array([1, 2, 3, 2, 1]), mindspore.float16)
        >>> tanh = mint.nn.Tanh()
        >>> output = tanh(input)
        >>> print(output)
        [0.7617 0.964  0.995  0.964  0.7617]
    """

    def __init__(self):
        """Initialize Tanh."""
        super(Tanh, self).__init__()

    def construct(self, input):
        return mint.nn.functional.tanh(input)


class Threshold(Cell):
    r"""
    Compute the Threshold activation function element-wise.

    The Threshold is defined as:

    .. math::
        y =
        \begin{cases}
        x, &\text{ if } x > \text{threshold} \\
        \text{value}, &\text{ otherwise }
        \end{cases}

    Args:
        threshold (Union[int, float]): The value of the threshold.
        value (Union[int, float]): The value to replace with when element is less than threshold.
        inplace (bool, optional): Whether to apply erasing inplace. Default: ``False``.

    Inputs:
        - **input** (Tensor) - The input Tensor.

    Outputs:
        Tensor, the same shape and data type as the input.

    Raises:
        TypeError: If `input` is not a Tensor.
        TypeError: If `threshold` is not a float or an int.
        TypeError: If `value` is not a float or an int.

    Supported Platforms:
        ``Ascend``

    Examples:
        >>> import mindspore
        >>> from mindspore import Tensor, mint
        >>> inputs = mindspore.Tensor([0.0, 2, 3], mindspore.float32)
        >>> net = mint.nn.Threshold(1, 100)
        >>> outputs = net(inputs)
        >>> print(outputs)
        [100.   2.   3.]
    """

    def __init__(self, threshold, value, inplace=False):
        """Initialize Tanh."""
        super(Threshold, self).__init__()
        self.threshold = threshold
        self.value = value
        self.inplace = inplace

    def construct(self, input):
        return mint.nn.functional.threshold(input, self.threshold, self.value,
                                            self.inplace)

__all__ = [
    'LogSigmoid',
    'SiLU',
    'ELU',
    'GLU',
    'Tanh',
    'Threshold',
]
