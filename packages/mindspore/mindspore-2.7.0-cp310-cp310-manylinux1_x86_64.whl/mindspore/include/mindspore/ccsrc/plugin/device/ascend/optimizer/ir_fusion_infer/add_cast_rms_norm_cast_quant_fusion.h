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
#ifndef MINDSPORE_CCSRC_BACKEND_OPTIMIZER_ADD_CAST_RMSNORM_CAST_QUANT_FUSION_H_
#define MINDSPORE_CCSRC_BACKEND_OPTIMIZER_ADD_CAST_RMSNORM_CAST_QUANT_FUSION_H_
#include <memory>
#include <string>
#include <vector>
#include "include/backend/optimizer/optimizer.h"

namespace mindspore {
namespace opt {
class AddCastRmsNormCastQuantFusion : public PatternProcessPass {
 public:
  explicit AddCastRmsNormCastQuantFusion(bool multigraph = true)
      : PatternProcessPass("add_cast_rms_norm_cast_quant_fusion", multigraph) {
    x1_ = std::make_shared<Var>();
    x2_ = std::make_shared<Var>();
    gamma_ = std::make_shared<Var>();
    scale_ = std::make_shared<Var>();
    offset_ = std::make_shared<Var>();
    eps_ = std::make_shared<Var>();
  }
  ~AddCastRmsNormCastQuantFusion() override = default;
  const BaseRef DefinePattern() const override;
  const AnfNodePtr Process(const FuncGraphPtr &, const AnfNodePtr &, const EquivPtr &) const override;

 private:
  std::vector<std::string> MustExistPrimitiveName() const override;

  VarPtr x1_;
  VarPtr x2_;
  VarPtr gamma_;
  VarPtr scale_;
  VarPtr offset_;
  VarPtr eps_;
  mutable VarPtr sqrt_mode_;
  mutable VarPtr rounding_mode_;
  mutable VarPtr dst_type_;
};
}  // namespace opt
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_BACKEND_OPTIMIZER_ADD_CAST_RMSNORM_CAST_QUANT_FUSION_H_
