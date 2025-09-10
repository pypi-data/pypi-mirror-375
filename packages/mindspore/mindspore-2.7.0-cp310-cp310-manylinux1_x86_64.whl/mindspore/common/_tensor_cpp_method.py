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

tensor_cpp_methods = ['div', 'divide', 'frac', 'mul', 'roll', 'expand_as', '__mod__', 'bitwise_xor', '__xor__', 'asinh', 'arcsinh', 'repeat', 'sub', '__sub__', 'split', 'narrow', 'kthvalue', 'trunc', 'unique', 'histc', 'gcd', 'true_divide', 'addmm', 'count_nonzero', 'all', 'median', 'tile', 'addbmm', 'diag', 'put_', 'ceil', 'new_ones', 'log10', 'argmin', 'scatter', 'xlogy', 'matmul', 'greater_equal', 'ge', 'mm', 'addcdiv', 'min', 'new_full', 'round', 'argsort', 'isinf', 'std', 'masked_fill', 'index_add', 'log1p', 'abs', 'absolute', '__abs__', 'cumsum', 'take', 'rsqrt', 'acosh', 'arccosh', 'gather', 'argmax', 'flatten', 'copy_', 'max', 'chunk', 'sort', 'not_equal', 'ne', 'neg', 'negative', 'minimum', 'exp', 'mean', 'asin', 'arcsin', 'triu', 'reciprocal', 'unbind', 'pow', '__pow__', 'subtract', 'isneginf', 'fill_diagonal_', 'floor_divide_', '__ifloordiv__', 'masked_select', 'masked_fill_', 'acos', 'arccos', 'isclose', 'nansum', 'tanh', 'repeat_interleave', '_to', 'scatter_', 'bitwise_and', '__and__', 'remainder', 'fmod', 'scatter_add', 'reshape', 'sqrt', 'logaddexp', 'outer', 'sub_', '__isub__', 'erfc', 'maximum', 'greater', 'gt', 'bitwise_or', '__or__', 'sinc', 'log2', 'logical_and', 'log', 'logaddexp2', 'sin', 'clamp', 'clip', 'nan_to_num', 'remainder_', '__imod__', 'topk', 'unsqueeze', 'div_', '__itruediv__', 'cosh', 'square', 'floor', 'erf', 'baddbmm', 't', 'var', 'add_', '__iadd__', 'isfinite', 'where', 'any', 'exp_', 'type_as', 'expm1', 'hardshrink', 'bitwise_not', 'dot', 'log_', 'select', 'transpose', 'new_zeros', 'prod', 'atan2', 'arctan2', 'logical_or', 'tril', 'atan', 'arctan', 'floor_divide', 'sinh', 'bincount', 'tan', 'clone', 'addmv', 'lerp', 'sigmoid', 'logical_xor', 'add', '__add__', 'logical_not', 'fill_', 'new_empty', 'less', 'lt', 'logsumexp', 'inverse', 'less_equal', 'le', 'cos', 'sum', 'index_select', 'masked_scatter', 'mul_', '__imul__', 'view_as', 'eq', 'allclose', 'atanh', 'arctanh']
