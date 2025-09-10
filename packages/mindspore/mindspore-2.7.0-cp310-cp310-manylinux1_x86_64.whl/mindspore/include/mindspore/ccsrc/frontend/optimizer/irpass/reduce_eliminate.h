/**
 * Copyright 2020-2021 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_FRONTEND_OPTIMIZER_IRPASS_REDUCE_ELIMINATE_H_
#define MINDSPORE_CCSRC_FRONTEND_OPTIMIZER_IRPASS_REDUCE_ELIMINATE_H_

#include <vector>
#include <algorithm>
#include <memory>

#include "frontend/optimizer/irpass.h"
#include "mindspore/ops/op_def/math_ops.h"
#include "frontend/optimizer/optimizer.h"
#include "frontend/optimizer/anf_visitor.h"
#include "frontend/operator/ops.h"
#include "abstract/dshape.h"
#include "utils/anf_utils.h"

namespace mindspore {
namespace opt {
namespace irpass {
using abstract::Shape;
using abstract::ShapePtr;

// {ReduceLike, X, axis}
class ReduceOneEliminater : public AnfVisitor {
 public:
  AnfNodePtr operator()(const OptimizerPtr &, const AnfNodePtr &node) override;

  void Visit(const AnfNodePtr &node) override;

  void Visit(const ValueNodePtr &vnode) override;

  void Reset();

 private:
  bool is_axis_one_{false}, is_tensor_{false};
  std::vector<int64_t> axis_{}, x_shape_{};
  AnfNodePtr x_{nullptr};
};
}  // namespace irpass
}  // namespace opt
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_FRONTEND_OPTIMIZER_IRPASS_REDUCE_ELIMINATE_H_
