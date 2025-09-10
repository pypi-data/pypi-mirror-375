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
"""
Optimizer.

Provide common optimizers for training, such as AdamW.
The optimizer is used to calculate and update the gradients.
"""
from __future__ import absolute_import
from mindspore.mint.optim.adamw import AdamW
from mindspore.mint.optim.adam import Adam
from mindspore.mint.optim.sgd import SGD

__all__ = ['AdamW', 'Adam', 'SGD']
