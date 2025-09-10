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

#ifndef MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_GPU_ROUND_KERNEL_H_
#define MINDSPORE_CCSRC_BACKEND_KERNEL_COMPILER_GPU_ROUND_KERNEL_H_

#include <functional>
#include <vector>
#include <string>
#include <utility>
#include <algorithm>
#include "kernel/gpu/gpu_kernel.h"
#include "common/ms_factory.h"
#include "kernel/gpu/cuda_impl/cuda_ops/elementwise/eltwise_ops_impl.cuh"
#include "kernel/gpu/cuda_impl/cuda_ops/elementwise/eltwise_ops_type.cuh"

namespace mindspore {
namespace kernel {
class RoundGpuKernelMod : public NativeGpuKernelMod {
 public:
  RoundGpuKernelMod() = default;
  ~RoundGpuKernelMod() override = default;

  bool Init(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

  int Resize(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs) override;

  bool Launch(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &workspace,
              const std::vector<KernelTensor *> &outputs, void *cuda_stream) override {
    if (is_null_input_) {
      return true;
    }
    cuda_stream_ = cuda_stream;
    return kernel_func_(this, inputs, outputs);
  }

  std::vector<KernelAttr> GetOpSupport() override;

 private:
  template <ElwiseOpType Op, typename Inp_t, typename Out_t>
  bool LaunchKernel(const std::vector<KernelTensor *> &inputs, const std::vector<KernelTensor *> &outputs);

  using RoundFunc = std::function<bool(RoundGpuKernelMod *, const std::vector<kernel::KernelTensor *> &,
                                       const std::vector<kernel::KernelTensor *> &)>;
  static std::vector<std::pair<KernelAttr, RoundFunc>> func_list_;
  size_t ele_num_{0};
  bool is_null_input_{true};
  void *cuda_stream_{nullptr};
  RoundFunc kernel_func_;
};
}  // namespace kernel
}  // namespace mindspore

#endif
