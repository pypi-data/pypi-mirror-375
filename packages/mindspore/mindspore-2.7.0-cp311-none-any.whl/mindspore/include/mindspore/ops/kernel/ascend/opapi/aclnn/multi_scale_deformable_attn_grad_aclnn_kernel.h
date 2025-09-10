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
#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_MULTI_SCALE_DEFORMABLE_ATTN_GRAD_ACLNN_KERNEL_MOD_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_MULTI_SCALE_DEFORMABLE_ATTN_GRAD_ACLNN_KERNEL_MOD_H_
#include <vector>
#include <utility>
#include "ops/base_operator.h"
#include "kernel/ascend/opapi/aclnn_kernel_mod.h"
#include "kernel/ascend/acl_ir/acl_convert.h"

namespace mindspore {
namespace kernel {
namespace multi_scale_deformable_attn_grad {
class MultiScaleDeformableAttnGradAscend : public AclnnKernelMod {
 public:
  MultiScaleDeformableAttnGradAscend() : AclnnKernelMod(std::move("aclnnMultiScaleDeformableAttnGrad")) {}
  ~MultiScaleDeformableAttnGradAscend() = default;
  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs, void *stream_ptr) override;
  void GetWorkSpaceInfo(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

 private:
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastValue)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastShape)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastOffset)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastLocations)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastWeight)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastGradOutput)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastFirstOutput)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastSecondOutput)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnCast, CastThirdOutput)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnMultiScaleDeformableAttentionGrad, MultiScaleDeformableAttnGrad)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnInplaceZero, InplaceZeroValue)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnInplaceZero, InplaceZeroLocations)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnInplaceZero, InplaceZeroWeight)

  KernelTensor value_expand_;
  KernelTensor shape_expand_;
  KernelTensor offset_expand_;
  KernelTensor locations_expand_;
  KernelTensor weight_expand_;
  KernelTensor grad_output_expand_;
  KernelTensor output_mid1_;
  KernelTensor output_mid2_;
  KernelTensor output_mid3_;

  std::vector<size_t> expand_indices_{};
};
}  // namespace multi_scale_deformable_attn_grad
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_MULTI_SCALE_DEFORMABLE_ATTN_ACLNN_KERNEL_MOD_H_
