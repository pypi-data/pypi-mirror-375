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

#ifndef MINDSPORE_CCSRC_RUNTIME_DEVICE_GPU_GPU_MEMORY_MANAGER_H_
#define MINDSPORE_CCSRC_RUNTIME_DEVICE_GPU_GPU_MEMORY_MANAGER_H_
#include <vector>
#include <string>
#include <unordered_map>
#include "runtime/device/res_manager/memory_manager.h"
#include "plugin/res_manager/gpu/visible.h"

namespace mindspore {
namespace device {
namespace gpu {
class GPU_RES_MANAGER_EXPORT GPUMemoryManager : public MemoryManager {
 public:
  GPUMemoryManager() = default;
  virtual ~GPUMemoryManager() = default;

  void Initialize() override;
  void Finalize() override;

  void *MallocMemFromMemPool(size_t size, bool from_persistent_mem, bool need_recycle = false,
                             uint32_t stream_id = kDefaultStreamIndex) override;
  void FreeMemFromMemPool(void *device_ptr) override;
  std::vector<void *> MallocContinuousMemFromMemPool(const std::vector<size_t> &size_list,
                                                     uint32_t stream_id = kDefaultStreamIndex) override;
  bool MallocContinuousMemFromMemPool(const DeviceAddressPtrList &addr_list, size_t total_size,
                                      std::vector<size_t> size_list, uint32_t stream_id = kDefaultStreamIndex) override;
  size_t GetAvailableMemSize() override;

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

  DynamicMemPool *GetMemoryPool() override;

 protected:
  uint8_t *MallocStaticMem(size_t size, bool communication_mem, uint32_t graph_id) override;
};
}  // namespace gpu
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_RUNTIME_DEVICE_GPU_GPU_MEMORY_MANAGER_H_
