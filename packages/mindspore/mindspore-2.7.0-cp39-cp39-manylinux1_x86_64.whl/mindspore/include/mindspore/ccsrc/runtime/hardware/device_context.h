/**
 * Copyright 2021-2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_RUNTIME_HARDWARE_DEVICE_CONTEXT_H_
#define MINDSPORE_CCSRC_RUNTIME_HARDWARE_DEVICE_CONTEXT_H_

#include <map>
#include <memory>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include "common/device_type.h"
#include "common/device_address.h"
#include "runtime/device/res_manager/swap_manager.h"
#include "runtime/device/res_manager/capture_graph.h"
#include "runtime/collective/collective_communication_lib.h"
#include "runtime/collective/collective_comm_lib_loader.h"
#include "include/backend/kernel_graph.h"
#include "utils/anf_utils.h"
#include "runtime/device/res_manager/memory_manager.h"
#include "runtime/device/res_manager/auto_mem_offload.h"
#include "runtime/pipeline/task/task.h"
#include "ir/device_event.h"
#include "utils/ms_context.h"
#include "ir/tensor.h"
#ifdef __APPLE__
#include "async/spinlock.h"
#endif

namespace mindspore {
namespace device {
using mindspore::kernel::KernelMod;
using mindspore::kernel::KernelTensor;

struct DeviceContextKey {
  // device type name, such as 'GPU' 'Ascend' 'CPU'.
  std::string device_name_;
  uint32_t device_id_{0};

  // Use the result of ToString() as key to look up DeviceContext
  // in cache map which maintains created DeviceContext objects.
  std::string ToString() const { return device_name_ + "_" + std::to_string(device_id_); }
};

class DeviceResManager;
class KernelExecutor;

// DeviceContext is unified interface of interaction with device.
class BACKEND_COMMON_EXPORT DeviceContext {
 public:
  explicit DeviceContext(const DeviceContextKey &device_context_key)
      : device_context_key_(device_context_key), initialized_(false) {}
  virtual ~DeviceContext() = default;

  // Initialize the device context.
  virtual void Initialize() = 0;

  // Destroy device context and release device resource.
  virtual void Destroy() = 0;

  // Get device_context_key_ to obtain device name and device id.
  const DeviceContextKey &device_context_key() const { return device_context_key_; }

  // Get device address type according different device type, such GPU, Ascend.
  DeviceType GetDeviceType() const { return GetDeviceTypeByName(device_context_key_.device_name_); }

  // Get kernel executor.
  std::shared_ptr<KernelExecutor> GetKernelExecutor() const { return kernel_executor_; }

  void SetKernelExecutor(const std::shared_ptr<KernelExecutor> &kernel_executor) { kernel_executor_ = kernel_executor; }

  // Return whether this device context is initialized.
  bool initialized() const {
#ifdef __APPLE__
    std::lock_guard<SpinLock> spin_lock(init_lock_);
#else
    std::lock_guard<std::mutex> lock(init_mutex_);
#endif
    return initialized_;
  }

  DeviceContextKey device_context_key_;
  std::unique_ptr<DeviceResManager> device_res_manager_;

 protected:
#ifdef __APPLE__
  // There are some problems with using mutex on Mac, use spinlocks instead.
  inline static SpinLock init_lock_;
#else
  inline static std::mutex init_mutex_;
#endif
  bool initialized_;

 private:
  std::shared_ptr<KernelExecutor> kernel_executor_;
};
using DeviceContextPtr = std::shared_ptr<DeviceContext>;

class BACKEND_COMMON_EXPORT DeviceResManager {
 public:
  DeviceResManager() : collective_comm_lib_(nullptr), device_context_(nullptr) {
    offloaded_mem_pool_ = std::make_shared<device::OffloadedMemPool>();
  }

  virtual ~DeviceResManager() = default;

  // Initialize the device resource manager.
  virtual void Initialize() {}

  // Set the deterministic mode.
  virtual void SetDeterministic() {}

  virtual void SetAclDeterministic() {}

  // Destroy device resource manager and release device resource.
  virtual void Destroy() {}

  // Bind device to current thread to gain device control privileges
  // If force_bind is true, bind context to current thread every time;
  // Otherwise, only bind context to current thread for the first time.
  virtual bool BindDeviceToCurrentThread(bool force_bind) const { return true; }
  virtual void ResetStreamAndCtx() {}

  // Relevant function to allocate and free device memory of raw ptr.
  virtual void *AllocateMemory(size_t size, uint32_t stream_id = kDefaultStreamIndex) const = 0;
  virtual void FreeMemory(void *ptr) const = 0;
  virtual void FreePartMemorys(const std::vector<void *> &free_addrs, const std::vector<void *> &keep_addrs,
                               const std::vector<size_t> &keep_addr_sizes) const = 0;
  virtual void DefragMemory() {}
  virtual bool IsEnableVmm() const { return false; }

  virtual void SwapIn(const void *host_ptr, void *device_ptr, size_t mem_size, void *stream) {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
    return;
  }
  virtual void SwapOut(const void *device_ptr, void *host_ptr, size_t mem_size, void *stream) {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
    return;
  }

  // Relevant function to allocate and free device memory of DeviceAddress.
  virtual bool AllocateMemory(DeviceAddress *const &address, uint32_t stream_id = UINT32_MAX) const;
  virtual void FreeMemory(DeviceAddress *const &address) const;
  virtual size_t GetMaxUsedMemorySize() const { return 0; }

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

  // Allocate host memory with raii and ref count
  virtual std::shared_ptr<void> AllocateHostMemory(size_t size) const {
    return std::shared_ptr<void>(::malloc(size), ::free);
  }
  // Allocate host memory for offload device memory.
  virtual void *AllocateOffloadMemory(size_t size) const;
  // Release host memory which was allocated by AllocateOffloadMemory to pool.
  // It will not be free to os.
  virtual void FreeOffloadMemory(void *ptr) const;
  virtual size_t GetAvailableMemSize() const { return 0; }

  // Allocate continuous device memory according to size list.
  // Communication operators may need continuous memory for input and output
  // to optimize the communication performance.
  virtual std::vector<void *> AllocateContinuousMemory(const std::vector<size_t> &size_list,
                                                       uint32_t stream_id = kDefaultStreamIndex) const {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
  }

  virtual DeviceAddressPtr CreateDeviceAddress() const { MS_LOG(EXCEPTION) << "Unimplemented interface."; }

  virtual DeviceAddressPtr CreateDeviceAddress(void *ptr, size_t size, const ShapeVector &shape_vector,
                                               const Format &format, TypeId type_id, const std::string &device_name,
                                               uint32_t device_id, uint32_t stream_id,
                                               const UserDataPtr &user_data = nullptr) const = 0;

  // Create a stream with assigning a stream id, the assigned stream id will be written to the parameter '*stream_id'.
  virtual bool CreateStream(size_t *stream_id) const {
    MS_LOG(WARNING) << "Unimplemented interface: 'CreateStream'.";
    *stream_id = kSizeZero;
    return false;
  }

  // Create a stream with priority.
  virtual bool CreateStreamWithPriority(size_t *stream_id, int32_t priority) const {
    *stream_id = kSizeZero;
    return false;
  }

  virtual size_t QueryStreamSize() const { return 0L; }
  virtual std::vector<uint32_t> GetStreamIds() const { return {}; }

  // If multi-stream used in pynative mode, other streams must be sync before the graph
  // is executed. Otherwise, out-of-order occurs. Therefore this flag is added.
  // This solution is a temporary solution, this flag will be removed after multi-stream is
  // supported in graph mode.
  virtual bool single_op_multi_stream_enable() const { return false; }
  virtual void set_single_op_multi_stream_enable(bool single_op_multi_stream_enable) {}

  // Get the stream pointer by stream_id.
  virtual void *GetStream(size_t stream_id) const { return nullptr; };

  // Set currently using stream id.
  virtual void SetCurrentStreamId(size_t stream_id) { return; }

  // Get currently using stream id.
  virtual size_t GetCurrentStreamId() const { return kSizeZero; }

  virtual void *GetStream() const { return nullptr; };

  virtual size_t GetCommunicationStreamID() const { return kDefaultStreamIndex; };

  virtual size_t GetCommunicationStreamIDByGroup(const std::string &group) const { return GetCommunicationStreamID(); };

  // Destroy a stream bound to the input parameter "stream_id".
  virtual bool DestroyStream(size_t stream_id) const { return false; }

  // Query tasks' completion status of a stream.
  virtual bool QueryStream(size_t stream_id) const { return true; }

  // Synchronize stream, device such as GPU and Ascend need stream to launch kernel asynchronously,
  // Using 'SyncStream' to block thread and wait for completing all tasks on specific stream.
  // Using 'SyncAllStream' to block thread and wait for completing all tasks on all streams.
  // Devices without stream could ignore the implementation of these function.
  // Since the current entry for creating streams is not unified, the implementation of the 'SyncStream' and
  // "SyncAllStreams" interfaces are implemented by subclasses.
  virtual bool SyncStream(size_t stream_id) const { return true; }

  virtual bool SyncAllStreams() const { return true; }

  virtual bool SyncNotDefaultStreams() const { return true; }

  // Return default stream id. Normally it's 0.
  virtual size_t DefaultStream() const { return 0; }

  // Create device event for runtime.
  virtual DeviceEventPtr CreateRuntimeEvent(bool enable_blocking, bool enable_record_wait) { return nullptr; }

  // Create mind graph
  virtual CaptureGraphPtr CreateCaptureGraph() { return nullptr; }

  // Create device event with flag.
  virtual DeviceEventPtr CreateEventWithFlag(bool enable_timing, bool blocking, bool use_extensional_api = true) {
    return nullptr;
  };

  // Destroy specified device event.
  virtual bool DestroyEvent(const DeviceEventPtr &event) { return true; }

  // Destroy all device events.
  virtual bool DestroyAllEvents() { return true; }

  // Detect stress.
  virtual int StressDetect() const { MS_LOG(EXCEPTION) << "Stress detection is not supported."; }

  // Send and receive parameters.
  virtual int SendRecv(const std::vector<tensor::TensorPtr> &params, int src_rank, int dst_rank) const {
    MS_LOG(EXCEPTION) << "Send and receive parameters is not supported.";
  }

  // Reset parameters.
  virtual int ResetParams(const std::vector<tensor::TensorPtr> &params) const {
    MS_LOG(EXCEPTION) << "Reset parameters is not supported.";
  }

  // Clean tdt channel
  virtual int CleanTdtChannel() const { MS_LOG(EXCEPTION) << "Clean tdt channel is not supported."; }

  // Dynamically load collective communication library.
  // Currently, four types are supported: OpenMPI and self developed framework for CPU. NCCL for GPU. HCCL for Ascend.
  virtual bool LoadCollectiveCommLib() = 0;

  // Return collective communication object for caller to access
  virtual CollectiveCommunicationLib *collective_comm_lib() const = 0;

  virtual std::shared_ptr<SwapManager> swap_manager() const { return nullptr; }

  virtual std::pair<std::vector<size_t>, std::vector<size_t>> AllocDeviceMemoryForTensorList(
    const std::vector<tensor::TensorPtr> &tensor_list, bool enable_mem_align) {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
  }

  virtual tensor::TensorPtr GetSliceByTensorListIndexHandle(const std::vector<tensor::TensorPtr> &tensor_list,
                                                            const std::vector<size_t> &before_padding_size,
                                                            const std::vector<size_t> &after_padding_size, size_t start,
                                                            size_t end) {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
  }
  virtual tensor::TensorPtr GetSliceByPaddingShapeHandle(const tensor::TensorPtr &first_tensor, size_t start,
                                                         size_t end) {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
  }
  virtual bool GetMemUceInfo(int32_t device_id) { return false; }
  virtual std::vector<uint64_t> GetOptimizerTimestamps() {
    MS_LOG(EXCEPTION) << "Get optimizer timestamps not support.";
  }
  virtual void UceMemRepair(int32_t device_id) { MS_LOG(EXCEPTION) << "Uce repair device is not supported."; }
  virtual void StopDevice(int32_t device_id) { MS_LOG(EXCEPTION) << "Uce stop device is not supported."; }
  virtual std::vector<std::pair<device::DeviceMemPtr, size_t>> GetMemUceAddr() { return {}; };

 protected:
  // The collective communication library.
  CollectiveCommunicationLib *collective_comm_lib_;

  DeviceContext *device_context_{nullptr};

 private:
  template <class... Args>
  friend class DeviceInterface;
  void SetDeviceContext(DeviceContext *device_context) { device_context_ = device_context; }
  std::shared_ptr<device::OffloadedMemPool> offloaded_mem_pool_;
};

using CallbackFunc = std::function<void(void)>;

class BACKEND_COMMON_EXPORT KernelExecutor {
 public:
  virtual ~KernelExecutor() = default;

  virtual void Initialize() {}
  virtual void Destroy() {}

  // Optimize the kernel graph for graph mode.
  virtual void OptimizeGraph(const FuncGraphPtr &graph) const {}

  // Generate 'KernelMod' for all kernels and set 'KernelMod' into kernel,
  // 'KernelMod' is real executive object of kernel.
  virtual void CreateKernel(const std::vector<CNodePtr> &nodes) const {}
  virtual kernel::KernelModPtr CreateKernelMod(const std::string &op_name) const { MS_LOG(EXCEPTION) << "Unrealized"; }

  // Adjust kernel graph before run graph.
  virtual void PreprocessBeforeRun(const FuncGraphPtr &graph) const {}

  // Create event for graph from cache.
  virtual void CreateEventForCache(const KernelGraphPtr &kernel_graph) const {}

  // Launch a kernel via 'KernelMod' of the kernel, use KernelTensor input type.
  virtual bool LaunchKernel(const CNodePtr &kernel, const std::vector<KernelTensor *> &inputs,
                            const std::vector<KernelTensor *> &workspace, const std::vector<KernelTensor *> &outputs,
                            KernelMod *kernel_mod, void *stream) const {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
  }
  // This is a high performance version of 'LaunchKernel', which will be called in performance-critical scenario.
  virtual bool LaunchKernelHP(const CNodePtr &kernel, const std::vector<KernelTensor *> &inputs,
                              const std::vector<KernelTensor *> &workspace, const std::vector<KernelTensor *> &outputs,
                              KernelMod *kernel_mod, void *stream) const {
    MS_LOG(EXCEPTION) << "Unimplemented interface.";
  }

  virtual void AddMindIRPass(const KernelGraphPtr &graph) const {}

  void SetDeviceContext(DeviceContext *device_context) { device_context_ = device_context; }

  virtual bool ExecuteKernelTask(const runtime::KernelTaskType &task_type,
                                 const device::DeviceAddressPtrList &input_addr_list,
                                 const device::DeviceAddressPtrList &output_addr_list, const size_t &stream_id) const {
    return false;
  };

  virtual bool ExecuteKernelTask(const runtime::KernelTaskType &task_type,
                                 const std::vector<device::DeviceAddress *> &input_addr_list,
                                 const std::vector<device::DeviceAddress *> &output_addr_list,
                                 const size_t &stream_id) const {
    return false;
  };

  virtual std::vector<size_t> GetLaunchIgnoredInputAddressIdx(const AnfNodePtr &node) const {
    MS_EXCEPTION_IF_NULL(node);
    auto kernel_info = dynamic_cast<device::KernelInfo *>(node->kernel_info());
    MS_EXCEPTION_IF_NULL(kernel_info);
    auto kernel_mod = kernel_info->MutableKernelMod();
    MS_EXCEPTION_IF_NULL(kernel_mod);
    return kernel_mod->GetLaunchIgnoredInputAddressIdx();
  }

  virtual bool IsLaunchIgnoredInputAddressIdx(const AnfNodePtr &node, size_t input_idx) const {
    auto ignored_input_list = GetLaunchIgnoredInputAddressIdx(node);
    if (std::find(ignored_input_list.begin(), ignored_input_list.end(), input_idx) != ignored_input_list.end()) {
      return true;
    }
    return false;
  }

 protected:
  DeviceContext *device_context_{nullptr};
};

template <class... Args>
class DeviceInterface : public DeviceContext {};

template <>
class DeviceInterface<> : public DeviceContext {
 public:
  explicit DeviceInterface(const DeviceContextKey &key) : DeviceContext(key) {}

 protected:
  void CheckUnset(const void *ptr, const std::string &error_msg) const {
    if (ptr != nullptr) {
      MS_LOG(EXCEPTION) << error_msg;
    }
  }
};

template <class T, class... Args>
class DeviceInterface<T, Args...> : public DeviceInterface<Args...> {
 public:
  explicit DeviceInterface(const DeviceContextKey &key) : DeviceInterface<Args...>(key) {
    if constexpr (std::is_base_of_v<DeviceResManager, T>) {
      DeviceInterface::CheckUnset(reinterpret_cast<void *>(DeviceContext::device_res_manager_.get()),
                                  "DeviceResManager has been registered!");
      DeviceContext::device_res_manager_ = std::make_unique<T>();
      DeviceContext::device_res_manager_->SetDeviceContext(this);
    } else if constexpr (std::is_base_of_v<KernelExecutor, T>) {
      DeviceInterface::CheckUnset(reinterpret_cast<void *>(DeviceContext::GetKernelExecutor().get()),
                                  "KernelExecutor has been registered!");
      DeviceContext::SetKernelExecutor(std::make_shared<T>());
      DeviceContext::GetKernelExecutor()->SetDeviceContext(this);
    }
  }
};
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_RUNTIME_HARDWARE_DEVICE_CONTEXT_H_
