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

#ifndef MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_TRIU_INFO_H_
#define MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_TRIU_INFO_H_

#include <memory>
#include <string>
#include <vector>
#include <tuple>

#include "utils/hash_map.h"
#include "ir/value.h"
#include "frontend/parallel/auto_parallel/operator_costmodel.h"
#include "frontend/parallel/ops_info/tril_info.h"
#include "frontend/parallel/strategy.h"

namespace mindspore {
namespace parallel {
class TriuInfo : public TrilInfo {
 public:
  TriuInfo(const std::string &name, const Shapes &input_shape, const Shapes &output_shape, const PrimitiveAttrs &attrs)
      : TrilInfo(name, input_shape, output_shape, attrs) {}
  ~TriuInfo() = default;
  ReplaceGraphPtr replace_graph(const CNodePtr &cnode) override;

 protected:
  Status GetAttrs() override;
  void ReplaceNodeInputOrAttrs() override;
  int64_t GetDiag();
  Status ReplaceGraphForDynamicShape(const CNodePtr &cnode);
  std::tuple<int64_t, int64_t, int64_t, int64_t> GetSliceInfo();
};
}  // namespace parallel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_TRIU_INFO_H_
