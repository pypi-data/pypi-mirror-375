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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_ADAMW_H_
#define MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_ADAMW_H_

#include <memory>
#include <vector>
#include <tuple>
#include "ir/tensor.h"
#include "ir/value.h"
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
std::tuple<tensor::TensorPtr, tensor::TensorPtr, tensor::TensorPtr> AdamWAscendCustomize(
  const std::shared_ptr<OpRunner> &op, const TensorPtr &var, const TensorPtr &m, const TensorPtr &v,
  const TensorPtr &max_v, const TensorPtr &grad, const TensorPtr &step, const FP32ImmPtr &lr, const FP32ImmPtr &beta1,
  const FP32ImmPtr &beta2, const FP32ImmPtr &decay, const FP32ImmPtr &epsilon, const BoolImmPtr &amsgrad,
  const BoolImmPtr &maximize);
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_ADAMW_H_
