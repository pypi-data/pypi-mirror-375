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

#ifndef MINDSPORE_CCSRC_UTILS_DLOPEN_MACRO_H
#define MINDSPORE_CCSRC_UTILS_DLOPEN_MACRO_H

#ifndef _WIN32
#include <dlfcn.h>
#else
#include <windows.h>
#undef ERROR
#undef SM_DEBUG
#undef Yield
#endif
#include <string>
#include <functional>
#include "utils/log_adapter.h"

#ifndef _WIN32
#define PORTABLE_EXPORT __attribute__((visibility("default")))
#else
#define PORTABLE_EXPORT __declspec(dllexport)
#endif

template <typename T>
struct SimuDataFactory {
  static T Data() {
    static T data{};
    return data;
  }
};

template <typename T>
struct SimuDataFactory<T *> {
  static T *Data() {
    static int data{};
    return reinterpret_cast<T *>(&data);
  }
};

template <typename T>
struct SimuDataFactory<T **> {
  static T **Data() {
    static int data{};
    static T *data_ptr = reinterpret_cast<T *>(&data);
    return &data_ptr;
  }
};

template <typename T>
struct SimuCreateTypeGetter {
  typedef T type;
};

template <typename T>
struct SimuCreateTypeGetter<T *> {
  typedef T type;
};

template <typename T>
struct SimuCreateTypeGetter<T **> {
  typedef T *type;
};

#define PLUGIN_METHOD(name, return_type, ...)                   \
  extern "C" {                                                  \
  PORTABLE_EXPORT return_type Plugin##name(__VA_ARGS__);        \
  }                                                             \
  constexpr const char *k##name##Name = "Plugin" #name;         \
  using name##FunObj = std::function<return_type(__VA_ARGS__)>; \
  using name##FunPtr = return_type (*)(__VA_ARGS__);

#define ORIGIN_METHOD(name, return_type, ...)                   \
  extern "C" {                                                  \
  return_type name(__VA_ARGS__);                                \
  }                                                             \
  constexpr const char *k##name##Name = #name;                  \
  using name##FunObj = std::function<return_type(__VA_ARGS__)>; \
  using name##FunPtr = return_type (*)(__VA_ARGS__);

#define ORIGIN_METHOD_WITH_SIMU(name, return_type, ...) \
  ORIGIN_METHOD(name, return_type, __VA_ARGS__)         \
  template <typename T>                                 \
  inline T SimuFuncI##name(__VA_ARGS__) {               \
    return SimuDataFactory<T>::Data();                  \
  }                                                     \
                                                        \
  template <>                                           \
  inline void SimuFuncI##name(__VA_ARGS__) {}           \
  extern name##FunObj name##_;                          \
  inline void SimuAssignI##name() { name##_ = SimuFuncI##name<return_type>; }

#define ORIGIN_METHOD_WITH_SIMU_CREATE(name, return_type, create_type_ptr, ...)          \
  ORIGIN_METHOD(name, return_type, create_type_ptr, ##__VA_ARGS__)                       \
  template <typename T, typename U>                                                      \
  inline T SimuFuncI##name(U *in_ret, ##__VA_ARGS__) {                                   \
    static U st##name{};                                                                 \
    *in_ret = st##name;                                                                  \
    T ret{};                                                                             \
    return ret;                                                                          \
  }                                                                                      \
                                                                                         \
  template <>                                                                            \
  inline aclError SimuFuncI##name(void **in_ret, ##__VA_ARGS__) {                        \
    static uintptr_t currentPointer = 0;                                                 \
    currentPointer += sizeof(void *);                                                    \
    *in_ret = reinterpret_cast<void *>(currentPointer);                                  \
    return ACL_SUCCESS;                                                                  \
  }                                                                                      \
                                                                                         \
  template <>                                                                            \
  inline void SimuFuncI##name(void **in_ret, ##__VA_ARGS__) {                            \
    static uintptr_t currentPointer = 0;                                                 \
    currentPointer += sizeof(void *);                                                    \
    *in_ret = reinterpret_cast<void *>(currentPointer);                                  \
  }                                                                                      \
  extern name##FunObj name##_;                                                           \
  inline void SimuAssignI##name() {                                                      \
    name##_ = SimuFuncI##name<return_type, SimuCreateTypeGetter<create_type_ptr>::type>; \
  }

#define ASSIGN_SIMU(name) SimuAssignI##name();

inline static std::string GetDlErrorMsg() {
#ifndef _WIN32
  const char *result = dlerror();
  return (result == nullptr) ? "Unknown" : result;
#else
  return std::to_string(GetLastError());
#endif
}

template <class T>
static T DlsymWithCast(void *handle, const char *symbol_name) {
#ifndef _WIN32
  T symbol = reinterpret_cast<T>(reinterpret_cast<intptr_t>(dlsym(handle, symbol_name)));
#else
  T symbol = reinterpret_cast<T>(GetProcAddress(reinterpret_cast<HINSTANCE__ *>(handle), symbol_name));
#endif
  if (symbol == nullptr) {
    MS_LOG(EXCEPTION) << "Dynamically load symbol " << symbol_name << " failed, result = " << GetDlErrorMsg();
  }
  return symbol;
}

#define DlsymFuncObj(func_name, plugin_handle) DlsymWithCast<func_name##FunPtr>(plugin_handle, k##func_name##Name);

template <class T>
static T DlsymAscend(void *handle, const char *symbol_name) {
  T symbol = reinterpret_cast<T>(reinterpret_cast<intptr_t>(dlsym(handle, symbol_name)));
  if (symbol == nullptr) {
    MS_LOG(WARNING) << "Dynamically load symbol " << symbol_name << " failed, result = " << GetDlErrorMsg();
  }
  return symbol;
}

#define DlsymAscendFuncObj(func_name, plugin_handle) DlsymAscend<func_name##FunPtr>(plugin_handle, k##func_name##Name)
#endif  // MINDSPORE_CCSRC_UTILS_DLOPEN_MACRO_H
