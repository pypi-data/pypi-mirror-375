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

#ifndef MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_LLM_BOOST_ATB_BUFFER_DEVICE_H
#define MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_LLM_BOOST_ATB_BUFFER_DEVICE_H
#include <string>
#include <cstdint>
#include "runtime/hardware/device_context.h"

namespace mindspore {
namespace kernel {
class BufferDevice {
 public:
  explicit BufferDevice(uint64_t bufferSize);
  virtual ~BufferDevice();
  void *GetBuffer(uint64_t bufferSize);

 private:
  void *buffer_ = nullptr;
  uint64_t bufferSize_ = 0;
  device::DeviceContext *device_context_{nullptr};
};
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_LLM_BOOST_ATB_BUFFER_DEVICE_H
