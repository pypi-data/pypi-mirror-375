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
#ifndef MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_DVM_COMM_INFO_H_
#define MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_DVM_COMM_INFO_H_
#include "backend/common/graph_kernel/adapter/graph_kernel_comm_info_manager.h"
#include "utils/ms_context.h"
namespace mindspore {
namespace graphkernel {
bool EnableDvmComm();
class DvmCommInfo : public GraphKernelCommInfo {
 public:
  DvmCommInfo() = default;
  ~DvmCommInfo() = default;
  bool EnableComm() override;
  bool IsTargetCommOp(const AnfNodePtr op) override;
};

REG_GRAPH_KERNEL_COMM_INFO(kAscendDevice, DvmCommInfo);
}  // namespace graphkernel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_DVM_COMM_INFO_H_
