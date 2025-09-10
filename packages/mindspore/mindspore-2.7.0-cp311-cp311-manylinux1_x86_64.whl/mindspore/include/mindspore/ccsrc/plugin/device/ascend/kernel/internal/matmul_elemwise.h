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
#ifndef MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_INTERNAL_INTERNAL_MATMUL_ELEMWISE_H_
#define MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_INTERNAL_INTERNAL_MATMUL_ELEMWISE_H_

#include <string>
#include <utility>
#include <vector>

#include "plugin/device/ascend/kernel/internal/internal_kernel_mod.h"
#include "include/internal.h"

namespace mindspore {
namespace kernel {
class InternalFusedMatmulElemBase : public InternalKernelMod {
 public:
  InternalFusedMatmulElemBase() : InternalKernelMod() {}
  ~InternalFusedMatmulElemBase() = default;

 protected:
  internal::InternalOpPtr CreateKernel(const internal::InputsImmutableInfoList &inputs,
                                       const internal::OutputsImmutableInfoList &outputs,
                                       const std::vector<KernelTensor *> &ms_inputs,
                                       const std::vector<KernelTensor *> &ms_outputs) override;
  uint64_t GenerateTilingKey(const std::vector<KernelTensor *> &inputs) override;

 private:
  internal::MatmulParam param_;
};

class InternalFusedMatmulElemUnary : public InternalFusedMatmulElemBase {
 public:
  InternalFusedMatmulElemUnary() : InternalFusedMatmulElemBase() {}
  ~InternalFusedMatmulElemUnary() = default;
};

class InternalFusedMatmulElemBinary : public InternalFusedMatmulElemBase {
 public:
  InternalFusedMatmulElemBinary() : InternalFusedMatmulElemBase() {}
  ~InternalFusedMatmulElemBinary() = default;
};
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_PLUGIN_DEVICE_ASCEND_KERNEL_INTERNAL_INTERNAL_MATMUL_ELEMWISE_H_
