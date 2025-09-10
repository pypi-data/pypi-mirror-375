/**
 * Copyright 2024-2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_FRONTEND_PARALLEL_PARALLEL_PREPROCESSOR_H_
#define MINDSPORE_CCSRC_FRONTEND_PARALLEL_PARALLEL_PREPROCESSOR_H_

#include <vector>
#include <memory>
#include "ir/anf.h"
#include "utils/hash_set.h"
#include "frontend/parallel/parallel_processor_context.h"
#include "frontend/parallel/ops_info/operator_info.h"

namespace mindspore {
namespace parallel {
class ParallelPreprocessor {
 public:
  explicit ParallelPreprocessor(const ParallelProcessorContextPtr &context) : processor_context_(context) {
    MS_EXCEPTION_IF_NULL(processor_context_);
  }

  void Process();

  static void ExtractInformation(const std::vector<AnfNodePtr> &all_nodes);
  static void HandleRootReshapeAndSaveStrategy(const std::vector<AnfNodePtr> &all_nodes);
  static void HandleForwardMakeTupleAndMakeList(const std::vector<AnfNodePtr> &all_nodes);

 private:
  void MarkAndModifyGraph();
  void SetOperatorInfo();
  void SetParameterInfo();
  void PipelinePreProcess();

  const ParallelProcessorContextPtr &processor_context_;
};
}  // namespace parallel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_FRONTEND_PARALLEL_PARALLEL_PREPROCESSOR_H_
