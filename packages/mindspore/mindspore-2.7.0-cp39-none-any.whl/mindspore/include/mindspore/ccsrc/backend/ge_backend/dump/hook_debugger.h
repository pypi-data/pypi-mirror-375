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

#ifndef MINDSPORE_CCSRC_BACKEND_GE_BACKEND_DUMP_HOOK_DEBUGGER_H_
#define MINDSPORE_CCSRC_BACKEND_GE_BACKEND_DUMP_HOOK_DEBUGGER_H_

#include <vector>
#include "include/backend/kernel_graph.h"

namespace mindspore {
namespace dump {
class BACKEND_EXPORT HookDebugger {
 public:
  HookDebugger() : is_enabled_(IsHookerEnabled()) {
    if (is_enabled_) {
      MS_LOG(INFO) << "Dump Hook is enabled.";
    } else {
      MS_LOG(INFO) << "Dump Hook is not enabled, please set MS_HOOK_ENABLE.";
    }
  }

  ~HookDebugger() = default;

  static HookDebugger &GetInstance();

  HookDebugger(const HookDebugger &) = delete;
  HookDebugger &operator=(const HookDebugger &) = delete;

  bool IsHookerEnabled();

  void HookOnStepBegin(uint32_t device_id, const std::vector<KernelGraphPtr> &graphs, int step_count, bool is_kbyk);

  void HookOnStepBegin(uint32_t device_id, const KernelGraphPtr &graph, int step_count, bool is_kbyk);

  void HookOnStepEnd();

 private:
  bool is_enabled_ = false;
  int dataset_sink_ = 0;
};
}  // namespace dump
}  // namespace mindspore

#endif
