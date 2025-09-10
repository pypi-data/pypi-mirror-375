/**
 * Copyright 2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_AVGPOOL3DGRADEXT_ASCEND_H_
#define MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_AVGPOOL3DGRADEXT_ASCEND_H_

#include <vector>
#include <memory>
#include "ir/tensor.h"
#include "ir/value.h"
#include "runtime/hardware/device_context_manager.h"
#include "mindspore/ccsrc/pyboost/op_runner.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
tensor::TensorPtr AvgPool3DGradExtAscendCustomize(const std::shared_ptr<OpRunner> &op, const TensorPtr &grad,
                                                  const TensorPtr &input, const ValueTuplePtr &kernel_size,
                                                  const std::optional<mindspore::ValueTuplePtr> &stride,
                                                  const ValueTuplePtr &padding, const BoolImmPtr &ceil_mode,
                                                  const BoolImmPtr &count_include_pad,
                                                  const std::optional<Int64ImmPtr> &divisor_override);
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_CUSTOMIZE_AVGPOOL3DGRADEXT_ASCEND_H_
