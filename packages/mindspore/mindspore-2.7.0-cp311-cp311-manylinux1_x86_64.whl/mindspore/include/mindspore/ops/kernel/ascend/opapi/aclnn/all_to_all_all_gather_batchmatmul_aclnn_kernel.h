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
#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_ALL_TO_ALL_ALL_GATHER_BATCHMATMUL_ACLNN_KERNEL_MOD_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_ALL_TO_ALL_ALL_GATHER_BATCHMATMUL_ACLNN_KERNEL_MOD_H_
#include <vector>
#include <string>
#include <utility>
#include "ops/base_operator.h"
#include "kernel/ascend/opapi/aclnn_kernel_mod.h"
#include "kernel/ascend/acl_ir/acl_convert.h"

namespace mindspore {
namespace kernel {
namespace all_to_all_all_gather_batchmatmul {

class AlltoAllAllGatherBatchMatMulAscend : public AclnnKernelMod {
 public:
  AlltoAllAllGatherBatchMatMulAscend() : AclnnKernelMod(std::move("aclnnAlltoAllAllGatherBatchMatMul")) {}
  ~AlltoAllAllGatherBatchMatMulAscend() = default;
  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs, void *stream_ptr) override;
  void GetWorkSpaceInfo(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

 private:
  DEFINE_GET_WORKSPACE_FOR_RESIZE()
  std::pair<KernelTensor *, bool> input_x_;
  std::pair<KernelTensor *, bool> input_weight_;
  KernelTensor *input_bias_;
  KernelTensor *output_y1_;
  KernelTensor *output_y2_;
  KernelTensor *output_y3_;
  void InitializeCommunicationAttributes();
  std::string group_ep_;
  std::string group_tp_;
  std::string hccl_inner_comm_ep_name_;
  std::string hccl_inner_comm_tp_name_;
  int64_t ep_world_size_;
  int64_t tp_world_size_;
  int64_t x_shard_type_;
  int64_t act_type_;
  bool transpose_weight_;
  bool output_y2_flag_;
  bool output_y3_flag_;
  //  Integer on the host side, enumeration of acl flow mode, currently only supports 1
  const int64_t stream_mode_ = 1;
};
}  // namespace all_to_all_all_gather_batchmatmul
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_ALL_TO_ALL_ALL_GATHER_BATCHMATMUL_ACLNN_KERNEL_MOD_H
