/**
 * Copyright 2019-2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_PLUGIN_RES_MANAGER_CPU_CPU_DEVICE_ADDRESS_H_
#define MINDSPORE_CCSRC_PLUGIN_RES_MANAGER_CPU_CPU_DEVICE_ADDRESS_H_

#include <string>
#include <vector>
#include "plugin/res_manager/cpu/visible.h"
#include "common/device_address.h"

namespace mindspore {
namespace device {
namespace cpu {
class CPU_RES_MANAGER_EXPORT CPUDeviceAddress : public DeviceAddress {
 public:
  CPUDeviceAddress() : DeviceAddress() { SetDevicePtrDeleter(); }

  CPUDeviceAddress(void *ptr, size_t size) : DeviceAddress(ptr, size) { SetDevicePtrDeleter(); }

  CPUDeviceAddress(void *ptr, size_t size, const string &format, TypeId type_id)
      : DeviceAddress(ptr, size, format, type_id) {
    SetDevicePtrDeleter();
  }

  CPUDeviceAddress(void *ptr, size_t size, const std::string &format, TypeId type_id, const KernelWithIndex &node_index)
      : DeviceAddress(ptr, size, format, type_id, node_index) {
    SetDevicePtrDeleter();
  }

  CPUDeviceAddress(void *ptr, size_t size, const std::string &format, TypeId type_id, const std::string &device_name,
                   uint32_t device_id)
      : DeviceAddress(ptr, size, format, type_id, device_name, device_id) {
    SetDevicePtrDeleter();
  }

  CPUDeviceAddress(void *ptr, size_t size, const ShapeVector &shape_vector, const Format &format, TypeId type_id,
                   const std::string &device_name, uint32_t device_id, uint32_t stream_id)
      : DeviceAddress(ptr, size, shape_vector, format, type_id, device_name, device_id, stream_id) {
    SetDevicePtrDeleter();
  }

  ~CPUDeviceAddress() override = default;
  DeviceAddressPtr CloneDeviceAddress() override;

  bool SyncDeviceToHost(const ShapeVector &shape, size_t size, TypeId type, void *host_ptr,
                        bool sync_on_demand = false) const override;
  bool SyncHostToDevice(const ShapeVector &shape, size_t size, TypeId type, const void *host_ptr,
                        const std::string &format) const override;
  bool AsyncHostToDevice(size_t size, TypeId type, const void *host_ptr, size_t) const override;
  bool SyncDeviceToDevice(const DeviceSync *src_device_addr) const override;
  bool AsyncDeviceToDevice(const DeviceAddress *src_device_addr, size_t) const override;
  bool AsyncHostToDevice(size_t size, TypeId type, const tensor::TensorDataPtr &tensor_data, const std::string &format,
                         size_t) const override;
  bool SyncDeviceToDevice(const ShapeVector &shape, size_t size, TypeId type, const void *src_ptr,
                          const std::string &format) const override;
  bool SyncDeviceToHost(void *host_ptr, const void *device_ptr, size_t size, const std::string &device_name,
                        uint32_t device_id, mindspore::Format format, const ShapeVector &shape, size_t stream_id,
                        const UserDataPtr &user_data = nullptr) const override;

  bool SyncHostToDevice(void *device_ptr, const void *host_ptr, size_t size, const std::string &device_name,
                        uint32_t device_id, mindspore::Format format, const ShapeVector &shape, size_t stream_id,
                        const UserDataPtr &user_data = nullptr) const override;

  void ClearDeviceMemory() override;
  void ClearUserData() override;

  // Set a device pointer destructor to kernel tensor, used to release resource reclaiming of the device pointer
  // automatically when DeviceAddress destructed.
  void SetDevicePtrDeleter();

  DeviceType GetDeviceType() const override { return DeviceType::kCPU; }
};
}  // namespace cpu
}  // namespace device
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_PLUGIN_RES_MANAGER_CPU_CPU_DEVICE_ADDRESS_H_
