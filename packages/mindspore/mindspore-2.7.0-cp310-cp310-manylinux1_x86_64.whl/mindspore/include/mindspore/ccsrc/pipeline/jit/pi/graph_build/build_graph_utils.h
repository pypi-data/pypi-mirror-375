/**
 * Copyright 2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_PI_JIT_GRAPH_BUILD_BUILD_UTILS_H_
#define MINDSPORE_PI_JIT_GRAPH_BUILD_BUILD_UTILS_H_
#include <utility>
#include <optional>
#include <string>
#include "pybind11/pybind11.h"
#include "ir/anf.h"
#include "ir/primitive.h"

namespace py = pybind11;

namespace mindspore {
namespace pijit {
std::pair<AbstractBasePtr, bool> InferAndCheck(const ValuePtr &value, const AbstractBasePtrList &input_abs_list);
AbstractBasePtr BuildNodeAbstract(const AnfNodePtr &node);

bool IsObjectCallable(const py::object &obj);
bool IsSideEffectPrimitive(const PrimitivePtr &prim);
bool IsValidOutputAbstractScalar(const AbstractBasePtr &abs);
bool IsValidOutputAbstractTensor(const AbstractBasePtr &abs);
bool IsPrimitiveCallable(const PrimitivePtr &prim, const AbstractBasePtr &abs);
bool IsParameterSequence(const py::object &object);
ParameterPtr AddParameter(const FuncGraphPtr &fg);
std::string GetParameterName(const AnfNodePtr &node);

py::tuple GetMethodInfo(const py::object &obj);
std::string GetTensorMethodName(const py::object &obj);
bool IsTensorMethod(const py::object &obj);
bool IsTensorOverloadMethod(const py::object &obj);
bool EnableTensorOverload();
void SyncTensor(const py::handle &obj);

ValuePtr ConvertPyObjToValue(const py::handle &handle);

void PrintConstantAbstract(const AbstractBasePtr &abs);
void AttachCustomBPropToGraph(const FuncGraphPtr &graph, const py::object &obj);

// Check whether it is an nn.CellList.
bool IsCellList(const py::object &obj);
bool IsConvertToInterpretedObject(const py::object &obj);
}  // namespace pijit
}  // namespace mindspore
#endif  // MINDSPORE_PI_JIT_GRAPH_BUILD_BUILD_UTILS_H_
