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

#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_ZEROS_CPU_KERNEL_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_ZEROS_CPU_KERNEL_H_

#include <complex>
#include <vector>
#include <utility>
#include "plugin/device/cpu/kernel/cpu_kernel.h"
#include "common/ms_factory.h"

namespace mindspore {
namespace kernel {
namespace zeros_cpu {
using complex64 = std::complex<float>;
using complex128 = std::complex<double>;

class ZerosCpuKernelMod : public NativeCpuKernelMod {
 public:
  ZerosCpuKernelMod() = default;
  ~ZerosCpuKernelMod() override = default;

  bool Init(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

  int Resize(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs) override {
    return kernel_func_(this, inputs, workspace, outputs);
  }

  std::vector<KernelAttr> GetOpSupport() override;

 private:
  void SelectKernelFunc(const std::vector<kernel::KernelTensor *> &inputs,
                        const std::vector<kernel::KernelTensor *> &outputs) {
    auto kernel_attr = GetKernelAttrFromTensors(inputs, outputs);
    auto pair = MatchKernelAttr(kernel_attr, GetOpSupport());
    if (!pair.first) {
      MS_LOG(EXCEPTION) << "'" << kernel_name_ << "' does not support this kernel data type: " << kernel_attr;
    }
    kernel_func_ = func_list_[pair.second].second;
  }

  template <typename T>
  bool LaunchKernel(const std::vector<kernel::KernelTensor *> &inputs,
                    const std::vector<kernel::KernelTensor *> &workspace,
                    const std::vector<kernel::KernelTensor *> &outputs);
  using ZerosFunc =
    std::function<bool(ZerosCpuKernelMod *, const std::vector<kernel::KernelTensor *> &,
                       const std::vector<kernel::KernelTensor *> &, const std::vector<kernel::KernelTensor *> &)>;
  static std::vector<std::pair<KernelAttr, ZerosFunc>> func_list_;
  ZerosFunc kernel_func_;
};
}  // namespace zeros_cpu
}  // namespace kernel
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_CPU_ZEROS_CPU_KERNEL_H_
