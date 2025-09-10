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
#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_BINCOUNT_EXT_ACLNN_KERNEL_MOD_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_BINCOUNT_EXT_ACLNN_KERNEL_MOD_H_
#include <memory>
#include <vector>
#include <utility>
#include "ops/base_operator.h"
#include "kernel/ascend/opapi/aclnn_kernel_mod.h"
#include "kernel/ascend/acl_ir/acl_convert.h"

namespace mindspore {
namespace kernel {
namespace bincount_ext {

class BincountExtAscend : public AclnnKernelMod {
 public:
  BincountExtAscend() : AclnnKernelMod(std::move("aclnnBincount")) {}
  ~BincountExtAscend() = default;
  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs, void *stream_ptr) override;
  void GetWorkSpaceInfo(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;
  bool IsNeedUpdateOutputShapeAndSize() override { return true; }
  void UpdateOutputShapeAndSize(const std::vector<KernelTensor *> &inputs,
                                const std::vector<KernelTensor *> &outputs) override;

 private:
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnMin, Min)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnMax, Max)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnBincount, Bincount)

  KernelTensor *min_output_tensor_ = nullptr;
  KernelTensor *max_output_tensor_ = nullptr;
  std::vector<ShapeVector> output_shape_{{0}};
  int64_t input_dim_ = 0;
  int64_t input_numel_ = 0;
  int64_t min_length_ = 0;
  TypePtr origin_output_typeptr_;
};
}  // namespace bincount_ext
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_BINCOUNT_EXT_ACLNN_KERNEL_MOD_H_
