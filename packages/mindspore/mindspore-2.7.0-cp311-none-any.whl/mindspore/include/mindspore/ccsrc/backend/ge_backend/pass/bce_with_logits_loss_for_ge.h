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
#ifndef MINDSPORE_CCSRC_BACKEND_GE_BACKEND_PASS_BCE_WITH_LOGITS_LOSS_FOR_GE_H_
#define MINDSPORE_CCSRC_BACKEND_GE_BACKEND_PASS_BCE_WITH_LOGITS_LOSS_FOR_GE_H_

#include <utility>
#include <string>
#include <vector>
#include <map>
#include "include/backend/optimizer/optimizer.h"

namespace mindspore {
namespace opt {
class BCEWithLogitsLossForGe : public PatternProcessPass {
 public:
  explicit BCEWithLogitsLossForGe(bool multi_graph = true)
      : PatternProcessPass("bce_with_logits_loss_for_ge", multi_graph) {}
  ~BCEWithLogitsLossForGe() override = default;
  const BaseRef DefinePattern() const override;
  const AnfNodePtr Process(const FuncGraphPtr &graph, const AnfNodePtr &node, const EquivPtr &) const override;
};
}  // namespace opt
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_BACKEND_GE_BACKEND_PASS_BCE_WITH_LOGITS_LOSS_FOR_GE_H_
