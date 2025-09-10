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

tensor_cpp_methods = ['split', 'logsumexp', 'addbmm', 'histc', 'sinh', 'logical_and', 'transpose', 'log1p', 'square', 'log10', 'mul_', '__imul__', 'median', 'cos', 'mm', 'acosh', 'arccosh', 'atanh', 'arctanh', 'repeat_interleave', 'log2', 'abs', 'absolute', '__abs__', 'nan_to_num', 'cumsum', 'all', 'pow', '__pow__', 'bitwise_xor', '__xor__', 'neg', 'negative', 'floor_divide_', '__ifloordiv__', 'argsort', 'remainder', 'hardshrink', 'clone', '_to', 'masked_fill_', 'view_as', 'tile', 'exp_', 'diag', 'baddbmm', 'erf', 'atan2', 'arctan2', 'sigmoid', 'bitwise_or', '__or__', 'bitwise_and', '__and__', 'trunc', 'scatter_add', 'inverse', 'sub', '__sub__', 'select', 'greater', 'gt', 'greater_equal', 'ge', 'unique', 'fill_', 'where', 'narrow', 'minimum', 'sinc', 'logical_or', '__mod__', 'sqrt', 'allclose', 'ceil', 'reciprocal', 'nansum', 'any', 'isfinite', 'max', 'roll', 'matmul', 'maximum', 'isinf', 'chunk', 'atan', 'arctan', 'scatter', 'logical_not', 'log_', 'less_equal', 'le', 'sum', 'tan', 'less', 'lt', 'not_equal', 'ne', 'copy_', 'log', 'bitwise_not', 'exp', 'unsqueeze', 'unbind', 'bincount', 'sub_', '__isub__', 't', 'argmax', 'addmm', 'round', 'floor', 'reshape', 'mean', 'subtract', 'var', 'addcdiv', 'fmod', 'fill_diagonal_', 'gather', 'new_ones', 'div', 'divide', 'flatten', 'count_nonzero', 'masked_fill', 'dot', 'expand_as', 'eq', 'isclose', 'topk', 'floor_divide', 'new_empty', 'index_add', 'isneginf', 'kthvalue', 'prod', 'asinh', 'arcsinh', 'addmv', 'expm1', 'outer', 'argmin', 'cosh', 'lerp', 'sin', 'sort', 'take', 'frac', 'logaddexp', 'xlogy', 'masked_select', 'true_divide', 'acos', 'arccos', 'gcd', 'clamp', 'clip', 'std', 'tanh', 'tril', 'type_as', 'remainder_', '__imod__', 'add_', '__iadd__', 'div_', '__itruediv__', 'logical_xor', 'index_select', 'repeat', 'asin', 'arcsin', 'erfc', 'rsqrt', 'min', 'new_full', 'add', '__add__', 'put_', 'triu', 'mul', 'scatter_', 'masked_scatter', 'logaddexp2', 'new_zeros']
