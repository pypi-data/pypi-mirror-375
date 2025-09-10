/**
 * Copyright 2023 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_REGISTER_H_
#define MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_REGISTER_H_

#include <map>
#include <memory>
#include <string>
#include <utility>
#include "mindspore/ops/op_def/array_ops.h"
#include "mindspore/ccsrc/pyboost/op_runner.h"
#include "runtime/pynative/op_runner.h"
#include "mindspore/ccsrc/pyboost/pyboost_utils.h"

namespace mindspore {
namespace kernel {
namespace pyboost {
template <typename T>
class PYBOOST_API OpFactory {
 public:
  using OpCreator = std::function<std::shared_ptr<T>()>;
  static OpFactory<T> &Get();
  void Register(const std::string &device, OpCreator &&func) {
    MS_LOG(DEBUG) << "Reg for op " << typeid(T).name() << " on device " << device;
    auto ret = op_creator_.try_emplace(device, func);
    if (!ret.second) {
      MS_LOG(WARNING) << "Duplicate op creator for " << typeid(T).name() << " on device " << device;
    }
  }

  std::shared_ptr<T> Create(const std::string &device, uint32_t stream_id);

  bool IsRegistered(const std::string &device) const { return op_creator_.find(device) != op_creator_.end(); }
  std::map<std::string, OpCreator> &op_creator() { return op_creator_; }

 private:
  OpFactory() = default;
  ~OpFactory() = default;
  DISABLE_COPY_AND_ASSIGN(OpFactory);
  std::map<std::string, OpCreator> op_creator_;
};

template <typename T>
class OpRegister {
 public:
  using OpCreator = std::function<std::shared_ptr<T>()>;
  OpRegister(const std::string &device, OpCreator &&fun) { OpFactory<T>::Get().Register(device, std::move(fun)); }
  ~OpRegister() = default;
};

#define MS_REG_PYBOOST_OP(DEVICE, clazz)                                                                      \
  static_assert(std::is_base_of<OpRunner, clazz>::value, " must be base of OpRunner");                        \
  static const OpRegister<clazz> g_##clazz##DEVICE##_##_PyBoost_reg(#DEVICE, []() {                           \
    return std::make_shared<clazz##DEVICE>(prim::kPrim##clazz, runtime::OpRunner::GetDeviceContext(#DEVICE)); \
  });

#define CREATE_PYBOOST_OP(NAME, DEVICE)                                                  \
  mindspore::kernel::pyboost::OpFactory<mindspore::kernel::pyboost::NAME>::Get().Create( \
    DEVICE, kernel::pyboost::PyBoostUtils::cur_stream_id());

// for internal op
template <typename T>
class PYBOOST_API InternalOpFactory {
 public:
  using OpCreator = std::function<std::shared_ptr<T>()>;
  static InternalOpFactory<T> &Get();

  void Register(const std::string &device, OpCreator &&func) {
    MS_LOG(DEBUG) << "Reg for internal op " << typeid(T).name() << " on device " << device;
    auto ret = op_creator_.try_emplace(device, func);
    if (!ret.second) {
      MS_LOG(WARNING) << "Duplicate op creator for " << typeid(T).name() << " on device " << device;
    }
  }

  std::shared_ptr<T> Create(const std::string &device, uint32_t stream_id);

  bool IsRegistered(const std::string &device) const { return op_creator_.find(device) != op_creator_.end(); }
  std::map<std::string, OpCreator> &op_creator() { return op_creator_; }

 private:
  InternalOpFactory() = default;
  ~InternalOpFactory() = default;
  DISABLE_COPY_AND_ASSIGN(InternalOpFactory);
  std::map<std::string, OpCreator> op_creator_;
};

template <typename T>
class InternalOpRegister {
 public:
  using OpCreator = std::function<std::shared_ptr<T>()>;
  InternalOpRegister(const std::string &device, OpCreator &&fun) {
    InternalOpFactory<T>::Get().Register(device, std::move(fun));
  }
  ~InternalOpRegister() = default;
};

#define MS_REG_PYBOOST_INTERNAL_OP(DEVICE, clazz)                                                   \
  static_assert(std::is_base_of<OpRunner, clazz>::value, " must be base of OpRunner");              \
  static const InternalOpRegister<clazz> g_internal##clazz##DEVICE##_##_PyBoost_reg(#DEVICE, []() { \
    return std::make_shared<Internal##clazz##DEVICE>(prim::kPrim##clazz,                            \
                                                     runtime::OpRunner::GetDeviceContext(#DEVICE)); \
  });

#define CREATE_PYBOOST_INTERNAL_OP(NAME, DEVICE)                                                 \
  mindspore::kernel::pyboost::InternalOpFactory<mindspore::kernel::pyboost::NAME>::Get().Create( \
    DEVICE, kernel::pyboost::PyBoostUtils::cur_stream_id())

#define CREATE_PYBOOST_SELECTED_OP(NAME, DEVICE)                                                          \
  kernel::pyboost::PyBoostUtils::IsEnableInternalKernel(#NAME) ? CREATE_PYBOOST_INTERNAL_OP(NAME, DEVICE) \
                                                               : CREATE_PYBOOST_OP(NAME, DEVICE)
}  // namespace pyboost
}  // namespace kernel
}  // namespace mindspore
#endif  // MINDSPORE_MINDSPORE_CCSRC_PIPELINE_PYNATIVE_FORWARD_PYBOOST_OP_REGISTER_H_
