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

tensor_cpp_methods = ['cos', 'maximum', 'log_', 'floor_divide', 'sub_', '__isub__', 'bitwise_and', '__and__', 'addcdiv', 'addmm', 'argsort', 'sinc', 'pow', '__pow__', 'cosh', 'mul_', '__imul__', 'less_equal', 'le', 'narrow', 'outer', 'rsqrt', 'mean', 'cumsum', 'count_nonzero', 'floor_divide_', '__ifloordiv__', 'log', 'roll', 'nansum', 'remainder', 'acos', 'arccos', 'repeat_interleave', 'bitwise_xor', '__xor__', 'kthvalue', 'greater_equal', 'ge', 'sort', 'tanh', 'tan', 'view_as', 'masked_fill', 'log10', 'isinf', 'new_zeros', 'mm', 'clamp', 'clip', 'logaddexp2', 'add', '__add__', 'masked_scatter', 'exp_', 'tril', 'asin', 'arcsin', 'atan', 'arctan', 'fill_diagonal_', 'gather', 'baddbmm', 'mul', 'atan2', 'arctan2', 'index_select', 'transpose', 'erfc', 'addbmm', 'trunc', 'logical_and', 'reshape', 'expm1', 'sub', '__sub__', 'add_', '__iadd__', 'bitwise_not', 'select', 'square', 'unique', 'new_full', 'take', 'greater', 'gt', 'expand_as', 'logical_xor', 'div_', '__itruediv__', 'logical_or', 'scatter_', 'xlogy', 'isneginf', 'remainder_', '__imod__', 'new_empty', 'div', 'divide', 'clone', 'exp', 'neg', 'negative', 'nan_to_num', 'acosh', 'arccosh', 'flatten', 'atanh', 'arctanh', 'var', 'fill_', 'isclose', 'histc', 'any', 'max', 'type_as', 'scatter_add', 'matmul', 'hardshrink', 'unbind', 'reciprocal', 'bitwise_or', '__or__', 'fmod', 'copy_', 'isfinite', 'round', 'min', 'prod', 'masked_fill_', 'unsqueeze', 'topk', 'abs', '__abs__', 'absolute', 'allclose', 'median', 'split', '__mod__', 'logsumexp', 'gcd', 'sigmoid', 'addmv', 'sum', 'dot', 'inverse', 'argmax', '_to', 'logaddexp', 'less', 'lt', 'tile', 'lerp', 'all', 'sqrt', 'asinh', 'arcsinh', 'scatter', 'masked_select', 'new_ones', 'logical_not', 'diag', 'argmin', 'index_add', 'std', 'floor', 'ceil', 'sin', 'erf', 'eq', 'subtract', 'true_divide', 'minimum', 't', 'bincount', 'log2', 'not_equal', 'ne', 'repeat', 'put_', 'log1p', 'frac', 'sinh', 'where', 'triu', 'chunk']
