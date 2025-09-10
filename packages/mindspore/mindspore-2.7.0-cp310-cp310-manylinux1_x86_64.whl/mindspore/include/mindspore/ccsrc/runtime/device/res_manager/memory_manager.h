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

#ifndef MINDSPORE_CCSRC_RUNTIME_DEVICE_MEMORY_MANAGER_H_
#define MINDSPORE_CCSRC_RUNTIME_DEVICE_MEMORY_MANAGER_H_
#include <memory>
#include <utility>
#include <vector>
#include <map>
#include <queue>
#include <string>
#include <unordered_map>
#include "include/backend/mem_reuse/dynamic_mem_pool.h"
#include "common/device_address.h"
#include "runtime/device/res_manager/utils/visible.h"

namespace mindspore {
namespace device {
enum class MemType { kStaticMem, kDynamicMem, kSomasReuseDynamicMem };
const uint32_t kInvalidGraphId = UINT32_MAX;
constexpr int kGetAllOuts = -1;
constexpr uint64_t kMemAlignSize = 512;
constexpr uint64_t kTwiceMemAlignSize = kMemAlignSize << 1;
class RES_EXPORT MemoryManager {
 public:
  MemoryManager() = default;
  virtual ~MemoryManager() = default;

  virtual void Initialize() = 0;
  virtual void Finalize() = 0;
  virtual void ResetDynamicMemory() {}
  virtual void ClearGlobalIdleMem() {}

  uint8_t *MallocOutputMem(const AnfNodePtr &node, size_t index, MemType type, size_t size,
                           const DeviceAddressPtr &address, bool comm_mem);
  uint8_t *MallocWorkSpaceMem(const AnfNodePtr &node, size_t index, MemType type, size_t size);
  uint8_t *MallocWorkSpaceMem(size_t size);
  virtual uint8_t *MallocMem(MemType type, size_t size, const DeviceAddressPtr &address, uint32_t graph_id);
  virtual uint8_t *MallocMem(MemType type, size_t size, const DeviceAddressPtr &address) {
    return MallocMem(type, size, address, kInvalidGraphId);
  }
  // param address is the address type of each device
  // param from_persistent_mem shows whether the tensor is a parameter in Pynative mode
  virtual bool MallocMemFromMemPool(const DeviceAddressPtr &address, size_t size);
  virtual void *MallocMemFromMemPool(size_t size, bool from_persistent_mem, bool need_recycle = false,
                                     uint32_t stream_id = kDefaultStreamIndex);
  virtual size_t GetMaxUsedMemorySize() const { return 0; }
  virtual void FreeMemFromMemPool(const DeviceAddressPtr address);
  virtual void FreeMemFromMemPool(void *device_ptr);
  virtual bool MallocContinuousMemFromMemPool(const DeviceAddressPtrList &addr_list, size_t total_size,
                                              std::vector<size_t> size_list, uint32_t stream_id = kDefaultStreamIndex);
  virtual std::vector<void *> MallocContinuousMemFromMemPool(const std::vector<size_t> &size_list,
                                                             uint32_t stream_id = kDefaultStreamIndex);

  static size_t GetCommonAlignSize(size_t input_size);
  static size_t GetCommunicationAlignSize(size_t input_size);

  virtual void SwapIn(const void *host_ptr, void *device_ptr, size_t mem_size, void *stream) {
    MS_LOG(INFO) << "Call default swap in " << host_ptr << "," << device_ptr << "," << mem_size << "," << stream;
  }
  virtual void SwapOut(const void *device_ptr, void *host_ptr, size_t mem_size, void *stream) {
    MS_LOG(INFO) << "Call default swap out " << host_ptr << "," << device_ptr << "," << mem_size << "," << stream;
  }
  virtual size_t GetAvailableMemSize() {
    MS_LOG(ERROR) << "Return default 0 mem size!";
    return 0;
  }

  bool RecordEvent(int64_t task_id_on_stream, uint32_t user_stream_id,
                   const std::vector<std::pair<uint32_t, DeviceMemPtr>> &memory_stream_addresses,
                   const DeviceEventPtr &event) {
    if (GetMemoryPool() == nullptr) {
      MS_LOG(WARNING) << "memory pool is nullptr.";
      return false;
    }
    return GetMemoryPool()->RecordEvent(task_id_on_stream, user_stream_id, memory_stream_addresses, event);
  }
  bool WaitEvent(int64_t task_id_on_stream, uint32_t user_stream_id, uint32_t memory_stream_id) {
    if (GetMemoryPool() == nullptr) {
      MS_LOG(WARNING) << "memory pool is nullptr.";
      return false;
    }
    return GetMemoryPool()->WaitEvent(task_id_on_stream, user_stream_id, memory_stream_id);
  }
  bool WaitEvent(int64_t task_id_on_stream, uint32_t memory_stream_id) {
    if (GetMemoryPool() == nullptr) {
      MS_LOG(WARNING) << "memory pool is nullptr.";
      return false;
    }
    return GetMemoryPool()->WaitEvent(task_id_on_stream, memory_stream_id);
  }
  bool SyncAllEvents() {
    if (GetMemoryPool() == nullptr) {
      MS_LOG(WARNING) << "memory pool is nullptr.";
      return false;
    }
    return GetMemoryPool()->SyncAllEvents();
  }

  virtual DynamicMemPool *GetMemoryPool() = 0;

  // Relevant function to manage memory statistics
  virtual size_t GetTotalMemStatistics() const { return 0; }
  virtual size_t GetTotalUsedMemStatistics() const { return 0; }
  virtual size_t GetTotalIdleMemStatistics() const { return 0; }
  virtual size_t GetTotalEagerFreeMemStatistics() const { return 0; }
  virtual size_t GetUsedMemPeakStatistics() const { return 0; }
  virtual size_t GetReservedMemPeakStatistics() const { return 0; }
  virtual std::unordered_map<std::string, std::size_t> GetBlockCountsStatistics() const { return {}; }
  virtual std::unordered_map<std::string, std::size_t> GetBlockUnitSizeStatistics() const { return {}; }
  virtual std::unordered_map<device::DeviceMemPtr, std::unordered_map<std::string, size_t>>
  GetCommonMemBlocksInfoStatistics() const {
    return {};
  }
  virtual std::unordered_map<device::DeviceMemPtr, std::unordered_map<std::string, size_t>>
  GetPersistentMemBlocksInfoStatistics() const {
    return {};
  }
  virtual void ResetMaxMemoryReserved() {}
  virtual void ResetMaxMemoryAllocated() {}
  virtual size_t EmptyCache() { return -1L; }

 protected:
  virtual uint8_t *MallocStaticMem(size_t size, bool communication_mem, uint32_t graph_id) = 0;
  virtual uint8_t *MallocStaticMem(size_t size, bool communication_mem) {
    return MallocStaticMem(size, communication_mem, kInvalidGraphId);
  }
  virtual uint8_t *MallocDynamicMem(size_t size, bool communication_mem);

  // Hold memory pool for common operations on memory.
  DynamicMemPool *memory_pool_{nullptr};
};
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_RUNTIME_DEVICE_MEMORY_MANAGER_H_
