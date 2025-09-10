/**
 * Copyright 2019 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_RUNTIME_DEVICE_ASCEND_ASCEND_MEMORY_MANAGER_H_
#define MINDSPORE_CCSRC_RUNTIME_DEVICE_ASCEND_ASCEND_MEMORY_MANAGER_H_

#include <vector>
#include <string>

#include <unordered_map>
#include "runtime/device/res_manager/memory_manager.h"
#include "plugin/res_manager/ascend/mem_manager/ascend_memory_pool.h"

namespace mindspore {
namespace device {
namespace ascend {
class ASCEND_RES_MANAGER_EXPORT AscendMemoryManager : public MemoryManager {
 public:
  AscendMemoryManager() = default;
  ~AscendMemoryManager() override = default;

  void Initialize() override;
  void Finalize() override;
  void ResetDynamicMemory() override;
  void ClearGlobalIdleMem() override;
  void *MallocMemFromMemPool(size_t size, bool from_persistent_mem, bool need_recycle = false,
                             uint32_t stream_id = kDefaultStreamIndex) override;
  void FreeMemFromMemPool(void *device_ptr) override;
  size_t GetMaxUsedMemorySize() const override;
  uint64_t GetMsMaxMemSize() const;
  bool MallocContinuousMemFromMemPool(const DeviceAddressPtrList &addr_list, size_t total_size,
                                      std::vector<size_t> size_list, uint32_t stream_id = kDefaultStreamIndex) override;
  std::vector<void *> MallocContinuousMemFromMemPool(const std::vector<size_t> &size_list,
                                                     uint32_t stream_id = kDefaultStreamIndex) override {
    return AscendMemoryPool::GetInstance().AllocContinuousTensorMem(size_list, stream_id);
  }

  void SwapIn(const void *host_ptr, void *device_ptr, size_t mem_size, void *stream) override;
  void SwapOut(const void *device_ptr, void *host_ptr, size_t mem_size, void *stream) override;
  size_t GetAvailableMemSize() override;
  uint64_t GetMsUsedHbmSize() const;

  // Relevant function to manage memory statistics
  size_t GetTotalMemStatistics() const override;
  size_t GetTotalUsedMemStatistics() const override;
  size_t GetTotalIdleMemStatistics() const override;
  size_t GetTotalEagerFreeMemStatistics() const override;
  size_t GetUsedMemPeakStatistics() const override;
  size_t GetReservedMemPeakStatistics() const override;
  std::unordered_map<std::string, std::size_t> GetBlockCountsStatistics() const override;
  std::unordered_map<std::string, std::size_t> GetBlockUnitSizeStatistics() const override;
  std::unordered_map<device::DeviceMemPtr, std::unordered_map<std::string, size_t>> GetCommonMemBlocksInfoStatistics()
    const override;
  std::unordered_map<device::DeviceMemPtr, std::unordered_map<std::string, size_t>>
  GetPersistentMemBlocksInfoStatistics() const override;
  void ResetMaxMemoryReserved() override;
  void ResetMaxMemoryAllocated() override;
  size_t EmptyCache() override;

  DynamicMemPool *GetMemoryPool() override;

 protected:
  uint8_t *MallocStaticMem(size_t size, bool communication_mem, uint32_t graph_id) override;
  uint8_t *MallocDynamicMem(size_t size, bool communication_mem) override;
};

class ASCEND_RES_MANAGER_EXPORT EnhancedAscendMemoryManager : public AscendMemoryManager {
 public:
  EnhancedAscendMemoryManager() = default;
  ~EnhancedAscendMemoryManager() override = default;

  void Initialize() override;

  void Finalize() override;

  void *MallocMemFromMemPool(size_t size, bool from_persistent_mem, bool need_recycle, uint32_t stream_id) override;

  bool MallocContinuousMemFromMemPool(const DeviceAddressPtrList &addr_list, size_t total_size,
                                      std::vector<size_t> size_list, uint32_t stream_id = kDefaultStreamIndex) override;

 private:
  inline uint64_t GetCurrentTick() {
    auto &&ts = std::chrono::system_clock::now();
    return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::nanoseconds>(ts.time_since_epoch()).count());
  }

  std::vector<size_t> alloc_costs_;
};
}  // namespace ascend
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_RUNTIME_DEVICE_ASCEND_ASCEND_MEMORY_MANAGER_H_
