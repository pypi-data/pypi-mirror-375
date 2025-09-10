/**
 * Copyright 2024 Huawei Technologies Co., Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_KV_CACHE_SCATTER_UPDATE_H_
#define MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_KV_CACHE_SCATTER_UPDATE_H_
#include <vector>
#include <memory>
#include "ir/tensor.h"
#include "ir/value.h"
#include "runtime/hardware/device_context_manager.h"
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
tensor::TensorPtr KVCacheScatterUpdateAscendCustomize(const std::shared_ptr<OpRunner> &op, const TensorPtr &var_tensor,
                                                      const TensorPtr &indices_tensor, const TensorPtr &updates_tensor,
                                                      const Int64ImmPtr &axis, const Int64ImmPtr &reduce);
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_KV_CACHE_SCATTER_UPDATE_H_
