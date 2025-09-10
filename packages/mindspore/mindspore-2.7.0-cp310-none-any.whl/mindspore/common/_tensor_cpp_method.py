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

tensor_cpp_methods = ['sinh', 'log', 'subtract', 'bitwise_or', '__or__', 'roll', 'allclose', '__mod__', 'div_', '__itruediv__', 'logical_and', 'nansum', 'isinf', 'put_', 'isfinite', 'prod', 'atan2', 'arctan2', 'square', 'chunk', 'atan', 'arctan', 'eq', 'argmax', 'unbind', 'sub_', '__isub__', 'erf', 'logaddexp2', 'lerp', 'expand_as', 'sub', '__sub__', 'acos', 'arccos', 'logical_or', 'frac', 'acosh', 'arccosh', 'greater_equal', 'ge', 'outer', 'remainder_', '__imod__', 'masked_scatter', 'xlogy', 'isneginf', 'kthvalue', 'index_add', 'log_', 'unique', 'argsort', 'div', 'divide', 'reciprocal', 'less', 'lt', 'median', 'atanh', 'arctanh', 'addcdiv', 'gather', 'exp_', 'add', '__add__', 'new_empty', 'nan_to_num', 'bitwise_not', 'isclose', 'logical_xor', 'where', 'min', 'bitwise_xor', '__xor__', 'new_full', 'gcd', 'narrow', 'copy_', 'fill_diagonal_', 'pow', '__pow__', 'true_divide', 'tanh', 'mm', 'less_equal', 'le', 'log1p', 'exp', 'logaddexp', 'std', 'cumsum', 'fill_', 'ceil', 'repeat_interleave', 'clamp', 'clip', 'hardshrink', 'expm1', 'tril', 'floor_divide_', '__ifloordiv__', 'all', 'new_ones', 'sqrt', 'bitwise_and', '__and__', 'topk', 'sort', 'add_', '__iadd__', 'mul_', '__imul__', 'count_nonzero', 'split', 'addbmm', 'reshape', 'greater', 'gt', 'tile', '_to', 'round', 'floor', 'sigmoid', 'flatten', 'logical_not', 'dot', 'not_equal', 'ne', 'sum', 'histc', 'maximum', 'bincount', 'remainder', 'tan', 'view_as', 'transpose', 'asin', 'arcsin', 'masked_fill_', 'masked_fill', 'scatter', 'cos', 'trunc', 'logsumexp', 'repeat', 'scatter_', 'scatter_add', 'take', 'asinh', 'arcsinh', 'triu', 'addmv', 'erfc', 't', 'addmm', 'cosh', 'index_select', 'sinc', 'log10', 'select', 'max', 'mul', 'minimum', 'var', 'neg', 'negative', 'log2', 'sin', 'clone', 'rsqrt', 'masked_select', 'argmin', 'abs', 'absolute', '__abs__', 'diag', 'any', 'inverse', 'baddbmm', 'unsqueeze', 'floor_divide', 'new_zeros', 'matmul', 'type_as', 'mean', 'fmod']
