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

#ifndef MINDSPORE_CCSRC_RUNTIME_DEVICE_ABSTRACT_ASCEND_ASCEND_MEMORY_POOL_SUPPORT_H_
#define MINDSPORE_CCSRC_RUNTIME_DEVICE_ABSTRACT_ASCEND_ASCEND_MEMORY_POOL_SUPPORT_H_

#include <memory>

#include "include/backend/mem_reuse/dynamic_mem_pool.h"
#include "plugin/res_manager/ascend/visible.h"

namespace mindspore {
namespace device {
namespace ascend {
// Definition for abstract ascend memory pool support class, wrap device interface of ascend.
class ASCEND_RES_MANAGER_EXPORT AbstractAscendMemoryPoolSupport : virtual public DynamicMemPool {
 public:
  ~AbstractAscendMemoryPoolSupport() override = default;

  size_t AllocDeviceMem(size_t size, DeviceMemPtr *addr) override;

  bool FreeDeviceMem(const DeviceMemPtr &addr) override;

  size_t MmapDeviceMem(const size_t size, const DeviceMemPtr addr) override;

  size_t GetMaxUsedMemSize() const override;

  size_t GetVmmUsedMemSize() const override;

  size_t free_mem_size() override;

  uint64_t total_mem_size() const override;

  // Set mem pool block size
  void SetMemPoolBlockSize(size_t available_device_mem_size) override;

  virtual void ResetIdleMemBuf() const;

  // Calculate memory block required alloc size when adding the memory block.
  size_t CalMemBlockAllocSize(size_t size, bool from_persistent_mem, bool need_recycle) override;

  // The related interface of device memory eager free.
  const bool IsEnableEagerFree() const override;

  const bool SyncAllStreams() override;

  size_t AllocDeviceMemByEagerFree(size_t size, DeviceMemPtr *addr) override;

  size_t FreeDeviceMemByEagerFree(const DeviceMemPtr addr, const size_t size) override;

  size_t EmptyCache() override;
};
using AbstractAscendMemoryPoolSupportPtr = std::shared_ptr<AbstractAscendMemoryPoolSupport>;
}  // namespace ascend
}  // namespace device
}  // namespace mindspore

#endif  // #define MINDSPORE_CCSRC_RUNTIME_DEVICE_ABSTRACT_ASCEND_ASCEND_MEMORY_POOL_SUPPORT_H_
