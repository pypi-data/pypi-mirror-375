/**
 * Copyright 2022-2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_OPS_KERNEL_COMMON_KERNEL_FACTORY_H_
#define MINDSPORE_OPS_KERNEL_COMMON_KERNEL_FACTORY_H_

#include <functional>
#include <map>
#include <memory>
#include <string>
#include "common/kernel_visible.h"

namespace mindspore {
namespace kernel {
class OPS_KERNEL_COMMON_API FactoryBase {
 public:
  virtual ~FactoryBase() = default;

 protected:
  static FactoryBase *GetInstance(const std::string &name);
  static void CreateFactory(const std::string &name, std::unique_ptr<FactoryBase> &&factory);

 private:
  static std::map<std::string, std::unique_ptr<FactoryBase>> &Map();
};
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_OPS_KERNEL_COMMON_KERNEL_FACTORY_H_
