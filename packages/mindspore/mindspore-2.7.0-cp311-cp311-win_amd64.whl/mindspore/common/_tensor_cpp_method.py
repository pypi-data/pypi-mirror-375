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

tensor_cpp_methods = ['abs', 'absolute', '__abs__', 'acos', 'arccos', 'acosh', 'arccosh', 'add', '__add__', 'addbmm', 'addcdiv', 'addmm', 'addmv', 'add_', '__iadd__', 'all', 'allclose', 'any', 'argmax', 'argmin', 'argsort', 'asin', 'arcsin', 'asinh', 'arcsinh', 'atan', 'arctan', 'atan2', 'arctan2', 'atanh', 'arctanh', 'baddbmm', 'bincount', 'bitwise_and', '__and__', 'bitwise_not', 'bitwise_or', '__or__', 'bitwise_xor', '__xor__', 'ceil', 'chunk', 'clamp', 'clip', 'clone', 'copy_', 'cos', 'cosh', 'count_nonzero', 'cumsum', 'diag', 'div', 'divide', 'div_', '__itruediv__', 'dot', 'eq', 'erf', 'erfc', 'exp', 'expand_as', 'expm1', 'exp_', 'fill_', 'fill_diagonal_', 'flatten', 'floor', 'floor_divide', 'floor_divide_', '__ifloordiv__', 'fmod', 'frac', 'gather', 'gcd', 'greater', 'gt', 'greater_equal', 'ge', 'hardshrink', 'histc', 'index_add', 'index_select', 'inverse', 'isclose', 'isfinite', 'isinf', 'isneginf', 'kthvalue', 'lerp', 'less', 'lt', 'less_equal', 'le', 'log', 'log10', 'log1p', 'log2', 'logaddexp', 'logaddexp2', 'logical_and', 'logical_not', 'logical_or', 'logical_xor', 'logsumexp', 'log_', 'masked_fill', 'masked_fill_', 'masked_scatter', 'masked_select', 'matmul', 'max', 'maximum', 'mean', 'median', 'min', 'minimum', 'mm', 'mul', 'mul_', '__imul__', 'nansum', 'nan_to_num', 'narrow', 'neg', 'negative', 'new_empty', 'new_full', 'new_ones', 'new_zeros', 'not_equal', 'ne', 'outer', 'pow', '__pow__', 'prod', 'put_', 'reciprocal', 'remainder', 'remainder_', '__imod__', 'repeat', 'repeat_interleave', 'reshape', 'roll', 'round', 'rsqrt', 'scatter', 'scatter_', 'scatter_add', 'select', 'sigmoid', 'sin', 'sinc', 'sinh', 'sort', 'split', 'sqrt', 'square', 'std', 'sub', '__sub__', 'subtract', 'sub_', '__isub__', 'sum', 't', 'take', 'tan', 'tanh', 'tile', 'topk', 'transpose', 'tril', 'triu', 'true_divide', 'trunc', 'type_as', 'unbind', 'unique', 'unsqueeze', 'var', 'view_as', 'where', 'xlogy', '_to', '__mod__']
