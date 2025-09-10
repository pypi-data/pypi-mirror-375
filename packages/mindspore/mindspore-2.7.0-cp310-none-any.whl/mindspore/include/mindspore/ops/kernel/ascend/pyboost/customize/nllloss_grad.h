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

#ifndef MINDSPORE_OPS_KERNEL_ASCEND_PYBOOST_CUSTOMIZE_NLLLOSS_GRAD_H_
#define MINDSPORE_OPS_KERNEL_ASCEND_PYBOOST_CUSTOMIZE_NLLLOSS_GRAD_H_
#include <vector>
#include <memory>
#include <tuple>
#include "ir/tensor.h"
#include "ir/value.h"
#include "runtime/hardware/device_context_manager.h"
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
tensor::TensorPtr NLLLossGradAscendCustomize(const std::shared_ptr<OpRunner> &op, const TensorPtr &logits_tensor,
                                             const TensorPtr &loss_grad_tensor, const TensorPtr &labels_tensor,
                                             const TensorPtr &weight_tensor, const TensorPtr &total_weight_tensor,
                                             const Int64ImmPtr &reduction, const Int64ImmPtr &ignore_index);
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_OPS_KERNEL_ASCEND_PYBOOST_CUSTOMIZE_NLLLOSS_GRAD_H_
