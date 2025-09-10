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
#ifndef MINDSPORE_PI_JIT_RUNTIME_H
#define MINDSPORE_PI_JIT_RUNTIME_H

#include <vector>
#include "pipeline/jit/pi/python_adapter/pydef.h"
#include "pipeline/jit/pi/jit_compile_results.h"

namespace mindspore {
namespace pijit {
namespace py = pybind11;

PyObject *CallCodeHook(PyThreadState *tstate, PyFrameWrapper f, JitCompileResults *c);

}  // namespace pijit
}  // namespace mindspore

#endif  // MINDSPORE_PI_JIT_COMMON_H
