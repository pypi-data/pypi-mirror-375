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

#ifndef MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_ARANGE_INFO_H_
#define MINDSPORE_CCSRC_FRONTEND_PARALLEL_OPS_INFO_ARANGE_INFO_H_

#include <string>
#include <memory>
#include <vector>

#include "utils/hash_map.h"
#include "ir/value.h"
#include "frontend/parallel/auto_parallel/operator_costmodel.h"
#include "frontend/parallel/ops_info/operator_info.h"
#include "frontend/parallel/ops_info/lin_space_info.h"
#include "frontend/parallel/strategy.h"

namespace mindspore {
namespace parallel {
class ArangeInfo : public LinSpaceExtInfo {
 public:
  ArangeInfo(const std::string &name, const Shapes &inputs_shape, const Shapes &outputs_shape,
             const PrimitiveAttrs &attrs)
      : LinSpaceExtInfo(name, inputs_shape, outputs_shape, attrs) {}
  ~ArangeInfo() override = default;

 protected:
  Status CheckStrategyForDynamicShape(const StrategyPtr &strategy) override { return SUCCESS; }
  Status ComputeReplaceGraph(const CNodePtr &cnode);
};

}  // namespace parallel
}  // namespace mindspore

#endif
