/**
 * Copyright 2021 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_RUNTIME_HARDWARE_GPU_GPU_DEVICE_CONTEXT_H_
#define MINDSPORE_CCSRC_RUNTIME_HARDWARE_GPU_GPU_DEVICE_CONTEXT_H_

#include <tuple>
#include <vector>
#include <memory>
#include <string>
#include <utility>
#include <unordered_map>
#include "runtime/hardware/device_context.h"
#include "runtime/hardware/device_context_manager.h"
#include "kernel/gpu/cuda_impl/cuda_ops/cuda_device_info.h"
#include "plugin/res_manager/gpu/gpu_res_manager.h"

namespace mindspore {
namespace device {
namespace gpu {
class GPUKernelExecutor;
class GPUDeviceResManager : public DeviceResManager {
 public:
  GPUDeviceResManager() {
    auto ms_context = MsContext::GetInstance();
    MS_EXCEPTION_IF_NULL(ms_context);
    auto device_id = ms_context->get_param<uint32_t>(MS_CTX_DEVICE_ID);
    ResKey res_key = {DeviceType::kGPU, device_id};
    gpu_res_manager_ = static_cast<GPUResManager *>(HalResManager::GetInstance().GetOrCreateResManager(res_key));
  }
  ~GPUDeviceResManager() override = default;

  // Set device id and initialize device resource, such as stream, cudnn and cublas handle.
  void Initialize() override;

  // Release device memory, stream, cudnn and cublas handle, etc.
  void Destroy() override;

  bool BindDeviceToCurrentThread(bool force_bind) const override;

  std::shared_ptr<void> AllocateHostMemory(size_t size) const override;

  std::vector<void *> AllocateContinuousMemory(const std::vector<size_t> &size_list,
                                               uint32_t stream_id = kDefaultStreamIndex) const override;

  DeviceAddressPtr CreateDeviceAddress() const override;
  DeviceAddressPtr CreateDeviceAddress(void *ptr, size_t size, const ShapeVector &shape_vector, const Format &format,
                                       TypeId type_id, const std::string &device_name, uint32_t device_id,
                                       uint32_t stream_id, const UserDataPtr &user_data = nullptr) const override;
  std::pair<std::vector<size_t>, std::vector<size_t>> AllocDeviceMemoryForTensorList(
    const std::vector<tensor::TensorPtr> &tensor_list, bool enable_mem_align) override;
  tensor::TensorPtr GetSliceByTensorListIndexHandle(const std::vector<tensor::TensorPtr> &tensor_list,
                                                    const std::vector<size_t> &before_padding_size,
                                                    const std::vector<size_t> &after_padding_size, size_t start,
                                                    size_t end) override;
  tensor::TensorPtr GetSliceByPaddingShapeHandle(const tensor::TensorPtr &first_tensor, size_t start,
                                                 size_t end) override;

  bool CreateStream(size_t *stream_id) const override;
  bool CreateStreamWithPriority(size_t *stream_id, int32_t priority) const override;
  size_t QueryStreamSize() const override;
  std::vector<uint32_t> GetStreamIds() const override;
  void *GetStream(size_t stream_id) const;
  size_t GetCommunicationStreamID() const override;
  bool DestroyStream(size_t stream_id) const override;
  void SetCurrentStreamId(size_t stream_id) override;
  size_t GetCurrentStreamId() const override;
  bool QueryStream(size_t stream_id) const override;
  bool SyncStream(size_t stream_id) const override;
  bool SyncAllStreams() const override;
  bool SyncNotDefaultStreams() const override;
  size_t DefaultStream() const override;

  // Create device event for runtime.
  DeviceEventPtr CreateRuntimeEvent(bool enable_blocking, bool enable_record_wait) override;

  DeviceEventPtr CreateEventWithFlag(bool enable_timing, bool blocking, bool use_extensional_api) override;
  bool DestroyEvent(const DeviceEventPtr &event) override;
  bool DestroyAllEvents() override;

  bool LoadCollectiveCommLib() override;
  mindspore::device::CollectiveCommunicationLib *collective_comm_lib() const override;

  bool single_op_multi_stream_enable() const override;
  void set_single_op_multi_stream_enable(bool single_op_multi_stream_enable) override;

 protected:
  // Relevant function to allocate and free device memory of raw ptr.
  void *AllocateMemory(size_t size, uint32_t stream_id = kDefaultStreamIndex) const override;
  void FreeMemory(void *ptr) const override;
  void FreePartMemorys(const std::vector<void *> &free_addrs, const std::vector<void *> &keep_addrs,
                       const std::vector<size_t> &keep_addr_sizes) const override;

  bool AllocateMemory(DeviceAddress *const &address, uint32_t stream_id = UINT32_MAX) const override;

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

 private:
  friend class GPUKernelExecutor;
  bool InitDevice();
  GPUResManager *gpu_res_manager_{nullptr};
};

class GPUKernelExecutor : public KernelExecutor {
 public:
  GPUKernelExecutor() = default;
  ~GPUKernelExecutor() override = default;

  void Initialize() override;
  void Destroy() override;

  // Optimize the kernel graph for graph mode.
  void OptimizeGraph(const FuncGraphPtr &graph) const override;

  void CreateKernel(const std::vector<CNodePtr> &nodes) const override;
  kernel::KernelModPtr CreateKernelMod(const std::string &op_name) const override;

  void PreprocessBeforeRun(const FuncGraphPtr &graph) const override;

  bool LaunchKernel(const CNodePtr &kernel, const std::vector<KernelTensor *> &inputs,
                    const std::vector<KernelTensor *> &workspace, const std::vector<KernelTensor *> &outputs,
                    KernelMod *kernel_mod, void *stream) const override;
  bool LaunchKernelHP(const CNodePtr &kernel, const std::vector<KernelTensor *> &inputs,
                      const std::vector<KernelTensor *> &workspace, const std::vector<KernelTensor *> &outputs,
                      KernelMod *kernel_mod, void *stream) const override {
    return LaunchKernel(kernel, inputs, workspace, outputs, kernel_mod, stream);
  }

  bool ExecuteKernelTask(const runtime::KernelTaskType &task_type, const device::DeviceAddressPtrList &input_addr_list,
                         const device::DeviceAddressPtrList &output_addr_list, const size_t &stream_id) const override;

  bool ExecuteKernelTask(const runtime::KernelTaskType &task_type,
                         const std::vector<device::DeviceAddress *> &input_addr_list,
                         const std::vector<device::DeviceAddress *> &output_addr_list,
                         const size_t &stream_id) const override;

 private:
  // Select the matching backend kernels according to the data type and format of input and output for all
  // execution operators, and set final device data type and format information for backend kernels, device
  // data type and format which replace original data type and format will use for executing kernels.
  void SetOperatorInfo(const KernelGraphPtr &graph) const;

  // General graph optimezer ignore device data type and format.
  void OptimizeGraphWithoutDeviceInfo(const KernelGraphPtr &graph) const;
  // Optimize the kernel graph according to device type, such format transform.
  void OptimizeGraphWithDeviceInfo(const KernelGraphPtr &graph) const;

  // Operator fusion optimization.
  void FuseOperators(const KernelGraphPtr &graph) const;

  // Update kernel ref info before create kernel
  void UpdateKernelRefInfo(const KernelGraphPtr &graph) const;

  // Launch a kernel and record the elapsed time end to end.
  bool LaunchKernelWithProfiling(const CNodePtr &kernel, const std::vector<KernelTensor *> &inputs,
                                 const std::vector<KernelTensor *> &workspace,
                                 const std::vector<KernelTensor *> &outputs, KernelMod *kernel_mod, void *stream) const;
  // Launch a kernel by 'KernelMod' of the kernel.
  bool DoLaunchKernel(const CNodePtr &kernel, const std::vector<KernelTensor *> &inputs,
                      const std::vector<KernelTensor *> &workspace, const std::vector<KernelTensor *> &outputs,
                      KernelMod *kernel_mod, void *stream) const;

  // The cublas handle is not thread safety specifically, it is not recommended that multiple threads access the same
  // cublas handle at the same time, so need the launch mutex when multiple threads launch the cublas kernels.
  mutable std::mutex launch_mutex_;
  GPUDeviceResManager *res_manager_{nullptr};
  bool initialized_ = false;
};

class GPUDeviceContext : public DeviceInterface<GPUKernelExecutor, GPUDeviceResManager> {
 public:
  explicit GPUDeviceContext(const DeviceContextKey &device_context_key) : DeviceInterface(device_context_key) {}
  ~GPUDeviceContext() override = default;

  // Set device id and initialize device resource, such as stream, cudnn and cublas handle.
  void Initialize() override;

  // Release device memory, stream, cudnn and cublas handle, etc.
  void Destroy() override;

  static uint32_t GetDeviceCount();
  static std::string GetDeviceName(uint32_t device_id);
  static std::tuple<int, int> GetDeviceCapability(uint32_t device_id);
  static cudaDeviceProp GetDeviceProperties(uint32_t device_id);
  static std::string GetArchList();

 private:
  DISABLE_COPY_AND_ASSIGN(GPUDeviceContext);
};
}  // namespace gpu
}  // namespace device
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_RUNTIME_HARDWARE_GPU_GPU_DEVICE_CONTEXT_H_
