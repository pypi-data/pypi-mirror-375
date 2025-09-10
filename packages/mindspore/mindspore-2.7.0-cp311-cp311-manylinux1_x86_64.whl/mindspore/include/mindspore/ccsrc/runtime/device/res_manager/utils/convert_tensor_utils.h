/**
 * Copyright 2019-2020 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_CCSRC_RUNTIME_DEVICE_RES_MANAGER_UTILS_CONVERT_TENSOR_UTILS_H_
#define MINDSPORE_CCSRC_RUNTIME_DEVICE_RES_MANAGER_UTILS_CONVERT_TENSOR_UTILS_H_

#include <iostream>
#include <vector>
#include "ir/tensor.h"
#include "runtime/device/res_manager/utils/visible.h"

namespace mindspore {
namespace device {
RES_EXPORT void HalfToFloat(void *dst, const void *src, size_t elem_num);
RES_EXPORT void FloatToHalf(void *dst, const void *src, size_t elem_num);
RES_EXPORT void DoubleToFloat(void *dst, const void *src, size_t elem_num);
RES_EXPORT void FloatToDouble(void *dst, const void *src, size_t elem_num);
RES_EXPORT void ShortToInt(void *dst, const void *src, size_t elem_num);
RES_EXPORT void IntToShort(void *dst, const void *src, size_t elem_num);
RES_EXPORT void LongToInt(void *dst, const void *src, size_t elem_num);
RES_EXPORT void IntToLong(void *dst, const void *src, size_t elem_num);
RES_EXPORT void ConvertSameType(void *const dst, const void *src, size_t size, TypeId type);

template <typename T>
void ConvertSameType(T *dst, const T *src, size_t elem_num) {
  if (dst == nullptr || src == nullptr) {
    return;
  }
  for (size_t i = 0; i < elem_num; ++i) {
    dst[i] = src[i];
  }
}
}  // namespace device
}  // namespace mindspore

#endif  // MINDSPORE_CCSRC_RUNTIME_DEVICE_RES_MANAGER_UTILS_CONVERT_TENSOR_UTILS_H_
