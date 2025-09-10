/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_SELF_DEFINE_SHARD_INFO_H_
#define MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_SELF_DEFINE_SHARD_INFO_H_

#include <memory>
#include <string>
#include <vector>
#include "ir/value.h"
#include "frontend/parallel/ops_info/operator_info.h"
#include "frontend/parallel/auto_parallel/operator_costmodel.h"
#include "frontend/parallel/strategy.h"

namespace mindspore {
namespace parallel {
class SelfDefineShardInfo : public OperatorInfo {
 public:
  SelfDefineShardInfo(const std::string &name, const Shapes &inputs_shape, const Shapes &outputs_shape,
                      const PrimitiveAttrs &attrs)
      : OperatorInfo(name, inputs_shape, outputs_shape, attrs, std::make_shared<BatchParallelCost>()) {}

  ~SelfDefineShardInfo() override = default;
  std::vector<StrategyPtr> GenerateOpStrategies(int64_t stage_id) override;
  Status SetCostUnderStrategy(const StrategyPtr &strategy) override;

 protected:
  Status UnreachableError();
  Status CheckStrategy(const StrategyPtr &strategy) override;
  Status InferAsLossDivisorByLayout() override;
  Status CheckInputLayout() override;
  Status CheckOutputLayout() override;
  Status InferOutputTensorInfo() override;
  Status InferMirrorOpsByLayout() override;
  Status GetAttrs() override { return SUCCESS; }
  Status InferTensorInfo() override { return UnreachableError(); }
  Status InferForwardCommunication() override { return UnreachableError(); }
  Status InferDevMatrixShape() override { return UnreachableError(); }
  Status InferTensorMap() override { return UnreachableError(); }
  Status InferAsLossDivisor() override { return UnreachableError(); }
  Status CheckLayout(const NewShapes &in_shapes, const std::vector<TensorInfoBasePtr> &tensor_info, const string &name);

 private:
  Status InferOperatorVectorListForShapeList(const TensorInfoBasePtr &tensor_info, const int64_t &input_idx,
                                             std::vector<OperatorVectorBasePtr> *mirror_ops_new, bool *group_is_empty);
  Status InferOperatorVectorValueForShapeValue(const TensorInfoBasePtr &tensor_info, const int64_t &input_idx,
                                               std::vector<OperatorVectorBasePtr> *mirror_ops_new,
                                               MirrorOps *mirror_ops, bool *group_is_empty);
};

class CustomInfo : public SelfDefineShardInfo {
 public:
  CustomInfo(const std::string &name, const Shapes &inputs_shape, const Shapes &outputs_shape,
             const PrimitiveAttrs &attrs)
      : SelfDefineShardInfo(name, inputs_shape, outputs_shape, attrs) {}
  ~CustomInfo() override = default;

 protected:
  Status CheckInputLayout() override;
  Status GetAttrs() override;
};

}  // namespace parallel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_SELF_DEFINE_SHARD_INFO_H_
