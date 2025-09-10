/**
 * Copyright 2023 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_MOEDISTRIBUTECOMBINE_ASCEND_H_
#define MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_MOEDISTRIBUTECOMBINE_ASCEND_H_

#include "mindspore/ccsrc/pyboost/auto_generate/moe_distribute_combine.h"
#include "ir/tensor.h"
#include "ir/scalar.h"
#include "mindspore/ops/ops_utils/memory_overlap.h"
#include "kernel/ascend/visible.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
class OPS_ASCEND_API MoeDistributeCombineAscend : public pyboost::MoeDistributeCombine {
 public:
  MoeDistributeCombineAscend(PrimitivePtr primitive, const DeviceContext *device_context)
      : MoeDistributeCombine(std::move(primitive), device_context) {}
  ~MoeDistributeCombineAscend() = default;

  mindspore::tensor::TensorPtr Call(const mindspore::tensor::TensorPtr &expand_x_tensor, const mindspore::tensor::TensorPtr &expert_ids_tensor, const mindspore::tensor::TensorPtr &expand_idx_tensor, const mindspore::tensor::TensorPtr &ep_send_counts_tensor, const mindspore::tensor::TensorPtr &expert_scales_tensor, const mindspore::Int64ImmPtr &ep_world_size, const mindspore::Int64ImmPtr &ep_rank_id, const mindspore::Int64ImmPtr &moe_expert_num, const std::optional<mindspore::tensor::TensorPtr> &tp_send_counts_tensor, const std::optional<mindspore::tensor::TensorPtr> &x_active_mask_tensor, const std::optional<mindspore::tensor::TensorPtr> &activate_scale_tensor, const std::optional<mindspore::tensor::TensorPtr> &weight_scale_tensor, const std::optional<mindspore::tensor::TensorPtr> &group_list_tensor, const std::optional<mindspore::tensor::TensorPtr> &expand_scales_tensor, const std::optional<mindspore::StringImmPtr> &group_ep, const std::optional<mindspore::StringImmPtr> &group_tp, const mindspore::Int64ImmPtr &tp_world_size, const mindspore::Int64ImmPtr &tp_rank_id, const mindspore::Int64ImmPtr &expert_shard_type, const mindspore::Int64ImmPtr &shared_expert_num, const mindspore::Int64ImmPtr &shared_export_rank_num, const mindspore::Int64ImmPtr &global_bs, const mindspore::Int64ImmPtr &out_dtype, const mindspore::Int64ImmPtr &common_quant_mode, const mindspore::Int64ImmPtr &group_list_type) override;
};
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_PYBOOST_MOEDISTRIBUTECOMBINE_ASCEND_H_
