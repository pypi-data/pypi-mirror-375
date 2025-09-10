/*
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

#ifndef MINDSPORE_CCSRC_FRONTEND_OPERATOR_META_DSL_COMMON_META_FUNC_BUILDER_H_
#define MINDSPORE_CCSRC_FRONTEND_OPERATOR_META_DSL_COMMON_META_FUNC_BUILDER_H_

#include <string>
#include <memory>
#include "mindspore/ccsrc/frontend/operator/meta_dsl/common/utils.h"

namespace mindspore::prim {
class MetaFuncBuilder {
 public:
  explicit MetaFuncBuilder(const std::string &name) : name_(name), graph_(std::make_shared<FuncGraph>()) {}
  ~MetaFuncBuilder() = default;

  void BeginFunc();
  FuncGraphPtr EndFunc() const;
  AnfNodePtr AddParameter(const std::string &name);
  AnfNodePtr CreateNode(const AnfNodePtrList &nodes);
  void SetOutput(const AnfNodePtr &output);

 private:
  std::string name_;
  FuncGraphPtr graph_{nullptr};
};
using MetaFuncBuilderPtr = std::shared_ptr<MetaFuncBuilder>;
}  // namespace mindspore::prim
#endif  // MINDSPORE_CCSRC_FRONTEND_OPERATOR_META_DSL_COMMON_META_FUNC_BUILDER_H_
