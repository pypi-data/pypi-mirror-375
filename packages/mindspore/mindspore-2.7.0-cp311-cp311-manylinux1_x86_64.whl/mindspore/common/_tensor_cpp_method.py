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

tensor_cpp_methods = ['prod', 'dot', 'isinf', 'index_add', 'pow', '__pow__', 'cumsum', 'histc', 'atan', 'arctan', 'std', 'masked_fill', 'sub', '__sub__', 'sinc', 'tile', 'chunk', 'less', 'lt', 'nan_to_num', 'kthvalue', 'reciprocal', 'ceil', 'tanh', 'sinh', 'diag', 'where', 'new_full', 'greater', 'gt', 'clone', 'unbind', 'transpose', 'mul', 'eq', 'logical_or', 'roll', 'var', 'reshape', 'new_ones', 'lerp', 'narrow', 'scatter', 'fill_diagonal_', 'repeat', 'allclose', 'copy_', 'addmm', 'all', 'cos', 'logical_not', 'expm1', 'round', 'tril', 'inverse', 'gather', 'div_', '__itruediv__', 'abs', '__abs__', 'absolute', 'add', '__add__', 'repeat_interleave', 'gcd', 'remainder', 'isfinite', 'hardshrink', 'view_as', 'less_equal', 'le', 'addbmm', 'square', 'clamp', 'clip', 'flatten', 'expand_as', 'count_nonzero', 'addmv', 'min', 'log_', 'minimum', 'matmul', 'atan2', 'arctan2', 'sigmoid', 'fmod', 'isneginf', 'true_divide', 'masked_select', 'new_empty', 'masked_scatter', 'trunc', 'mul_', '__imul__', 'floor', 'logsumexp', 'asinh', 'arcsinh', 'select', 'max', 'div', 'divide', 'addcdiv', 'sqrt', 'any', 'logical_xor', 'log1p', 't', 'bitwise_xor', '__xor__', 'not_equal', 'ne', 'subtract', 'mean', 'exp_', 'argsort', 'triu', 'isclose', 'argmin', 'nansum', 'argmax', 'put_', 'topk', 'exp', 'new_zeros', 'bincount', 'scatter_', 'tan', 'asin', 'arcsin', 'logaddexp', 'greater_equal', 'ge', 'masked_fill_', 'median', 'sort', 'bitwise_or', '__or__', 'acos', 'arccos', 'floor_divide', 'mm', 'atanh', 'arctanh', 'maximum', 'sub_', '__isub__', 'bitwise_not', 'neg', 'negative', 'rsqrt', 'add_', '__iadd__', 'unique', 'erfc', 'remainder_', '__imod__', 'sum', 'erf', '__mod__', 'fill_', 'type_as', 'frac', 'unsqueeze', 'index_select', '_to', 'outer', 'take', 'acosh', 'arccosh', 'logical_and', 'scatter_add', 'bitwise_and', '__and__', 'baddbmm', 'log2', 'split', 'sin', 'xlogy', 'logaddexp2', 'cosh', 'log', 'floor_divide_', '__ifloordiv__', 'log10']
