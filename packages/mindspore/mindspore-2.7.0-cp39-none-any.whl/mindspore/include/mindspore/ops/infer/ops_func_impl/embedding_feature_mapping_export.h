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

#ifndef MINDSPORE_CORE_OPS_FUNC_IMPL_EMBEDDING_FEATURE_MAPPING_EXPORT_H_
#define MINDSPORE_CORE_OPS_FUNC_IMPL_EMBEDDING_FEATURE_MAPPING_EXPORT_H_

#include <vector>
#include "infer/ops_func_impl/embedding_feature_mapping_insert.h"

namespace mindspore {
namespace ops {
class OPS_API EmbeddingFeatureMappingExportFuncImpl final : public EmbeddingFeatureMappingInsertFuncImpl {
 public:
  EmbeddingFeatureMappingExportFuncImpl() {
    table_name_idx_ = 1;
    feature_id_idx_ = 5;
    other_arg_num_ = 5;
  }

  ~EmbeddingFeatureMappingExportFuncImpl() = default;

 protected:
  void SetDynInputSizes(const PrimitivePtr &primitive, int64_t table_num) const override;

  int32_t SpecifiedCheck(const PrimitivePtr &primitive, const std::vector<AbstractBasePtr> &input_args,
                         size_t table_num, const std::vector<int64_t> &feature_size) const override;

 private:
  const size_t values_idx_{3};
  const size_t embedding_dim_idx_{4};
};
}  // namespace ops
}  // namespace mindspore

#endif  // MINDSPORE_CORE_OPS_FUNC_IMPL_EMBEDDING_FEATURE_MAPPING_EXPORT_H_
