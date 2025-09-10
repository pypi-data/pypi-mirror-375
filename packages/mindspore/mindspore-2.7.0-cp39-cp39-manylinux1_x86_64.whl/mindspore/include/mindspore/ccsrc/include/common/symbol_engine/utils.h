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
#ifndef MINDSPORE_CCSRC_INCLUDE_COMMON_SYMBOL_ENGINE_UTILS_H_
#define MINDSPORE_CCSRC_INCLUDE_COMMON_SYMBOL_ENGINE_UTILS_H_
#include <vector>
#include <utility>
#include <unordered_map>
#include <map>
#include <string>
#include <memory>
#include <set>
#include <mutex>

#include "ir/anf.h"
#include "ir/func_graph.h"
#include "symbolic_shape/symbol_engine.h"
#include "symbolic_shape/symbol.h"
#include "symbolic_shape/operation_builder.h"
#include "symbolic_shape/operation.h"
#include "include/common/visible.h"

namespace mindspore {
namespace symshape {
struct COMMON_EXPORT DependStatus {
  bool shape{false};
  bool value{false};
};

/// \brief nodes have same digital shape may use same abstract object, but their symbolic shape may not same, clone a
/// new abstract for symbolic info.
COMMON_EXPORT AbstractBasePtr CloneAbstractIfSymbolExists(const AbstractBasePtr &abs);
inline AbstractBasePtr CloneAbstractIfSymbolExists(const AnfNodePtr &node) {
  node->set_abstract(CloneAbstractIfSymbolExists(node->abstract()));
  return node->abstract();
}

COMMON_EXPORT void CleanSymbols(const FuncGraphPtr &func_graph);
COMMON_EXPORT AbstractBasePtrList ExtractInputsAbstract(const CNodePtr &cnode);
COMMON_EXPORT bool HasAbstractAny(const AbstractBasePtrList &inputs, const AbstractBasePtr &output);
}  // namespace symshape
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_INCLUDE_COMMON_SYMBOL_ENGINE_UTILS_H_
