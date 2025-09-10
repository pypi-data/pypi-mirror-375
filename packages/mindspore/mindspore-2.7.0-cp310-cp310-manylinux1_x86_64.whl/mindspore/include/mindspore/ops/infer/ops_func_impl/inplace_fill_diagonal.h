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

#ifndef MINDSPORE_CORE_OPS_OP_FUNC_INPLACE_FILLDIAGONAL_IMPL_H
#define MINDSPORE_CORE_OPS_OP_FUNC_INPLACE_FILLDIAGONAL_IMPL_H

#include <vector>
#include <set>
#include <memory>
#include "ops/ops_func_impl/op_func_impl.h"

namespace mindspore::ops {
class InplaceFillDiagonalFuncImpl : public OpFuncImpl {
 public:
  ShapeArray InferShape(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos) const override;
  std::vector<TypeId> InferType(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos) const override;
  bool GeneralInferRegistered() const override { return true; };
};
using InplaceFillDiagonalFuncImplPtr = std::shared_ptr<InplaceFillDiagonalFuncImpl>;
}  // namespace mindspore::ops
#endif  // MINDSPORE_CORE_OPS_OP_FUNC_INPLACE_FILLDIAGONAL_IMPL_H
