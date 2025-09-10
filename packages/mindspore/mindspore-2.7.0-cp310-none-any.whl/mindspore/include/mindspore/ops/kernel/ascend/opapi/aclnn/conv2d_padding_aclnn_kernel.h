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
#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CONV2D_PADDING_ACLNN_KERNEL_MOD_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CONV2D_PADDING_ACLNN_KERNEL_MOD_H_
#include <vector>
#include <utility>
#include <memory>
#include "ops/base_operator.h"
#include "kernel/ascend/opapi/aclnn_kernel_mod.h"
#include "kernel/ascend/acl_ir/acl_convert.h"
#include "kernel/ascend/pyboost/aclnn_utils.h"

namespace mindspore {
namespace kernel {
namespace conv2d_padding {

class Conv2DPaddingAscend : public AclnnKernelMod {
 public:
  Conv2DPaddingAscend() : AclnnKernelMod(std::move("aclnnConvolution")) {}
  ~Conv2DPaddingAscend() = default;
  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs, void *stream_ptr) override;
  void GetWorkSpaceInfo(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

 private:
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnConstantPadNd, ConstantPadNd)
  DEFINE_GET_WORKSPACE_FOR_OPS(aclnnConvolution, Conv2DPadding)

  bool GetSymmetricPadding(const std::vector<int64_t> &stride_, const std::vector<int64_t> &dilation_,
                           const ShapeVector &input_sizes, const ShapeVector &weight_sizes, const size_t dim,
                           std::vector<int64_t> &padding_l, std::vector<int64_t> &padding_r);
  std::vector<int64_t> GetOriginStrides(const std::vector<int64_t> &shape);
  TensorStorageInfoPtr CreateTensorStorageInfoPtr(const std::vector<int64_t> &new_shape,
                                                  const TensorStorageInfoPtr &old_tensor_storage_info);
  template <typename T>
  void SetTensorStorageInfo(T kernel_tensor, const ShapeVector &shape);
  void SetExpandTensor(KernelTensor *input_tensor, const std::vector<KernelTensor *> &inputs);

  std::vector<int64_t> stride_;
  std::vector<int64_t> dilation_;
  int64_t padding_{0};
  int64_t groups_{0};
  bool transposed_{false};
  bool need_ConstantPadNd_{false};
  bool is_batchfy_{false};

  std::vector<int64_t> output_padding_{0, 0};
  std::vector<int64_t> pad_vector_;
  std::vector<int64_t> pad_nd_{};
  std::vector<int64_t> pad_nd_shape_{};
  KernelTensor input_expand_;
  ScalarPtr zero_ = std::make_shared<Int64Imm>(static_cast<int64_t>(0));

  size_t expand_count_{0};
  std::vector<size_t> expand_indices_{};
  std::shared_ptr<KernelTensor> input_kernel_tensor_;
  std::shared_ptr<KernelTensor> output_kernel_tensor_;
};
}  // namespace conv2d_padding
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CONV2D_PADDING_ACLNN_KERNEL_MOD_H_
