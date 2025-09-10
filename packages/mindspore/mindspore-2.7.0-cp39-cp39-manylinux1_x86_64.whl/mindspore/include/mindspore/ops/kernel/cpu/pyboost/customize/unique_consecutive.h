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

#ifndef MINDSPORE_MINDSPORE_OPS_KERNEL_CPU_PYBOOST_CUSTOMIZE_UNIQUE_CONSECUTIVE_H_
#define MINDSPORE_MINDSPORE_OPS_KERNEL_CPU_PYBOOST_CUSTOMIZE_UNIQUE_CONSECUTIVE_H_

#include <tuple>
#include <vector>
#include <memory>
#include "ir/tensor.h"
#include "ir/value.h"
#include "runtime/hardware/device_context_manager.h"
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
std::tuple<tensor::TensorPtr, tensor::TensorPtr, tensor::TensorPtr> UniqueConsecutiveCPUCustomize(
  const std::shared_ptr<OpRunner> &op, const TensorPtr &input_tensor, const BoolImmPtr &return_inverse,
  const BoolImmPtr &return_counts, const std::optional<Int64ImmPtr> &dim);

}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_OPS_KERNEL_CPU_PYBOOST_CUSTOMIZE_UNIQUE_CONSECUTIVE_H_
