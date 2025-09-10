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
#ifndef MINDSPORE_CORE_OPS_OPS_FUNC_IMPL_REDUCE_REDUCE_ARITHMETIC_H_
#define MINDSPORE_CORE_OPS_OPS_FUNC_IMPL_REDUCE_REDUCE_ARITHMETIC_H_

#include <vector>
#include <set>
#include <memory>
#include "ir/primitive.h"
#include "ops/ops_func_impl/op_func_impl.h"

namespace mindspore {
namespace ops {
constexpr auto kReduceInputAtLeastLen = 3;
BaseShapePtr ReduceInferShape(const PrimitivePtr &primitive, const std::vector<AbstractBasePtr> &input_args);
ShapeArray ReduceInferShape(const PrimitivePtr &primitive, const ValuePtrList &input_values);
ShapeArray ReduceInferShape(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos);
ShapeArray NormInferShape(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos);
BaseShapePtr ReduceExtandInferShape(const PrimitivePtr &primitive, const std::vector<AbstractBasePtr> &input_args);
ShapeArray ReduceExtandSimpleInferShape(const PrimitivePtr &primitive, const ValuePtrList &input_values);
ShapeArray ReduceGeneralInferShape(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos);
ShapeArray ReduceGeneralInferShapeV2(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos);
int64_t CalRealAixs(const int64_t &axis, const size_t &x_shape_size, const PrimitivePtr &primitive);
}  // namespace ops
}  // namespace mindspore
#endif  // MINDSPORE_CORE_OPS_OPS_FUNC_IMPL_REDUCE_REDUCE_ARITHMETIC_H_
