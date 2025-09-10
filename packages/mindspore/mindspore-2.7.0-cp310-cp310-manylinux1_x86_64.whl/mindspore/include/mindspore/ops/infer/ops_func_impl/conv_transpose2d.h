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

#ifndef MINDSPORE_CORE_OPS_OPS_FUNC_IMPL_CONV_TRANSPOSE_2D_H_
#define MINDSPORE_CORE_OPS_OPS_FUNC_IMPL_CONV_TRANSPOSE_2D_H_

#include <memory>
#include <vector>
#include "infer/ops_func_impl/conv_base.h"

namespace mindspore {
namespace ops {
class OPS_API ConvTranspose2DFuncImpl final : public ConvBaseFunImpl {
 public:
  ConvTranspose2DFuncImpl() {
    idxes_.input_idx = 0;
    idxes_.weight_idx = 1;
    idxes_.bias_idx = 2;
    idxes_.stride_idx = 3;
    idxes_.padding_idx = 4;
    idxes_.output_padding_idx = 5;
    idxes_.groups_idx = 6;
    idxes_.dilation_idx = 7;
  }
  ~ConvTranspose2DFuncImpl() = default;

  ShapeArray InferShape(const PrimitivePtr &primitive, const InferInfoPtrList &input_infos) const override;
};
}  // namespace ops
}  // namespace mindspore

#endif  // MINDSPORE_CORE_OPS_OPS_FUNC_IMPL_CONV_TRANSPOSE_2D_H_
