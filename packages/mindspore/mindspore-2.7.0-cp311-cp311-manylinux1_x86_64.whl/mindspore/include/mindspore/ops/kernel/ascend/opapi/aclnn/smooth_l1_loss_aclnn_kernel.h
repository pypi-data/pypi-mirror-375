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
#ifndef MINDSPORE_OPS_KERNEL_ASCEND_OPAPI_ACLNN_SMOOTH_L1_LOSS_ACLNN_KERNEL_H_
#define MINDSPORE_OPS_KERNEL_ASCEND_OPAPI_ACLNN_SMOOTH_L1_LOSS_ACLNN_KERNEL_H_
#include <vector>
#include <utility>
#include <string>
#include "ops/base_operator.h"
#include "kernel/ascend/opapi/aclnn_kernel_mod.h"
#include "kernel/ascend/acl_ir/acl_convert.h"

namespace mindspore {
namespace kernel {
namespace smooth_l1_loss {
class SmoothL1LossAscendKernelMod : public AclnnKernelMod {
 public:
  SmoothL1LossAscendKernelMod() : AclnnKernelMod(std::move("aclnnSmoothL1Loss")) {}
  ~SmoothL1LossAscendKernelMod() = default;
  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs, void *stream_ptr) override;
  void GetWorkSpaceInfo(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

 private:
  DEFINE_GET_WORKSPACE_FOR_RESIZE()
  float beta_ = 1.0;
  int64_t reduction_value_{2};
};
}  // namespace smooth_l1_loss
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_OPS_KERNEL_ASCEND_OPAPI_ACLNN_SMOOTH_L1_LOSS_ACLNN_KERNEL_H_
