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

#ifndef MINDSPORE_INPLACE_NODE_PASS_H
#define MINDSPORE_INPLACE_NODE_PASS_H

#include <memory>
#include <string>
#include "ir/func_graph.h"
#include "include/backend/visible.h"
#include "include/backend/optimizer/node_pass.h"

namespace mindspore {
namespace opt {
class BACKEND_COMMON_EXPORT InplaceNodePass : public NodePass {
 public:
  explicit InplaceNodePass(const std::string &name = "") : NodePass(name) {}
  ~InplaceNodePass() override = default;
  virtual bool Process(const AnfNodePtr &) const = 0;
  AnfNodePtr Run(const FuncGraphPtr &, const AnfNodePtr &node) override;
  bool IsFastPass() override { return true; }
};
}  // namespace opt
}  // namespace mindspore

#endif  // MINDSPORE_INPLACE_NODE_PASS_H
