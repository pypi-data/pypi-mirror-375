/**
 * Copyright 2022-2025 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_HAL_HARDWARE_ASCEND_DEPRECATED_INTERFACE_H_
#define MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_HAL_HARDWARE_ASCEND_DEPRECATED_INTERFACE_H_

#include <vector>
#include <memory>
#include <string>
#include <map>
#include "base/base.h"
#include "utils/ms_context.h"
#include "plugin/res_manager/ascend/visible.h"

namespace mindspore {
namespace device {
namespace ascend {
class ASCEND_RES_MANAGER_EXPORT TdtManager {
 public:
  ~TdtManager() = default;
  static TdtManager &GetInstance();

  bool OpenTsd(const std::shared_ptr<MsContext> &ms_context_ptr);
  bool CloseTsd(const std::shared_ptr<MsContext> &ms_context_ptr, bool force);

 private:
  TdtManager() = default;
};
}  // namespace ascend
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_HAL_HARDWARE_ASCEND_DEPRECATED_INTERFACE_H_
