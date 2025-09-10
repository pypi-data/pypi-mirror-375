/**
 * Copyright 2023-2025 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CORE_OPS_GEN_OPS_PRIMITIVE_z_H_
#define MINDSPORE_CORE_OPS_GEN_OPS_PRIMITIVE_z_H_

#include "ir/primitive.h"
#include "mindapi/base/macros.h"
#include "mindspore/ops/op_def/auto_generate/gen_ops_name_z.h"

namespace mindspore::prim {
OPS_API extern const PrimitivePtr kPrimZerosLike;
OPS_API extern const PrimitivePtr kPrimZeros;
OPS_API extern const PrimitivePtr kPrimZerosLikeExt;
}  // namespace mindspore::prim
#endif  // MINDSPORE_CORE_OPS_GEN_OPS_PRIMITIVE_z_H_
