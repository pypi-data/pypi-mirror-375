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
"""Add tensor cpp methods for stub tensor"""

tensor_cpp_methods = ['atan2', 'arctan2', 'greater_equal', 'ge', 'acos', 'arccos', 'argmin', 'index_select', 'erfc', 'addcdiv', 'matmul', 'eq', 'put_', 'floor', 'addmv', 'type_as', 'reshape', 'nansum', 'logical_xor', 'logsumexp', 'topk', 'view_as', 'scatter_add', 'tan', 'narrow', 'sin', 'unique', 'copy_', 'baddbmm', 'logical_or', 'scatter_', 'logical_and', 'fill_diagonal_', 'frac', 't', 'median', 'square', 'masked_fill', 'less_equal', 'le', 'true_divide', 'outer', 'sigmoid', 'sinc', 'clamp', 'clip', 'argmax', 'atanh', 'arctanh', 'std', 'div_', '__itruediv__', 'sinh', 'subtract', '_to', 'sub', '__sub__', 'floor_divide', 'rsqrt', 'not_equal', 'ne', 'dot', 'max', 'clone', 'acosh', 'arccosh', 'unsqueeze', 'lerp', 'masked_fill_', 'ceil', 'masked_select', 'index_add', 'mul_', '__imul__', 'chunk', 'unbind', 'log10', 'fmod', 'scatter', 'transpose', 'mm', 'min', 'bitwise_or', '__or__', 'diag', 'greater', 'gt', 'cumsum', 'expm1', 'abs', 'absolute', '__abs__', 'logical_not', 'log', 'gather', 'sqrt', 'where', 'inverse', 'bitwise_and', '__and__', 'new_full', 'flatten', 'argsort', 'xlogy', 'triu', 'tril', 'neg', 'negative', 'erf', 'isfinite', 'repeat', 'add', '__add__', 'logaddexp', 'div', 'divide', 'floor_divide_', '__ifloordiv__', 'bincount', 'sum', 'new_zeros', 'roll', 'var', 'exp_', 'nan_to_num', 'isneginf', 'addbmm', 'minimum', 'remainder_', '__imod__', 'isinf', 'exp', 'pow', '__pow__', 'tanh', 'gcd', 'add_', '__iadd__', 'log1p', 'expand_as', 'isclose', 'allclose', 'bitwise_xor', '__xor__', 'histc', 'cosh', 'asin', 'arcsin', 'new_empty', 'maximum', 'atan', 'arctan', 'any', 'asinh', 'arcsinh', 'masked_scatter', 'trunc', 'mul', 'select', 'bitwise_not', 'fill_', 'all', 'mean', 'sort', 'hardshrink', 'kthvalue', 'addmm', 'remainder', 'reciprocal', 'round', 'log_', 'cos', 'split', 'tile', 'new_ones', 'logaddexp2', '__mod__', 'log2', 'prod', 'less', 'lt', 'sub_', '__isub__', 'take', 'count_nonzero', 'repeat_interleave']
