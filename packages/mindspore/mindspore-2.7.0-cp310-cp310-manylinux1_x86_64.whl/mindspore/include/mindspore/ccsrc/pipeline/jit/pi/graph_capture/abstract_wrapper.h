/**
 * Copyright 2024-2025 Huawei Technologies Co., Ltd
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

#ifndef MINDSPORE_PI_JIT_GRAPH_CAPTURE_ABSTRACT_WRAPPER_H
#define MINDSPORE_PI_JIT_GRAPH_CAPTURE_ABSTRACT_WRAPPER_H

#include <string>
#include <memory>
#include <vector>

#include "pybind11/pybind11.h"
#include "ir/value.h"
#include "abstract/abstract_value.h"
#include "pipeline/jit/pi/graph_capture/graph_build_helper.h"

namespace py = pybind11;

namespace mindspore {
namespace pijit {
constexpr auto kPijitNamedtupleType = "pijit_namedtuple_type";
constexpr auto kPijitBuildHelper = "pijit_build_helper";

class AbstractWrapper;
using AbstractWrapperPtr = std::shared_ptr<AbstractWrapper>;
using AbstractWrapperPtrList = std::vector<AbstractWrapperPtr>;

class AbstractWrapper {
 public:
  explicit AbstractWrapper(const AbstractBasePtr &abstract) : abstract_(abstract) {}
  std::string ToString() const;
  AbstractBasePtr abstract() const { return abstract_; }
  bool IsConstant() const;
  bool IsDict() const;

  // Throw exception when abstract in wrapper has no size.
  size_t size() const;

  // return -1 when abstract in wrapper has no size.
  int TryToGetSize() const;

  std::vector<py::object> GetDictKeysObject() const;
  std::vector<py::object> GetSliceInputsPyObject() const;

  static py::object ConvertToPyObject(const AbstractWrapperPtr &wrapper);
  static py::object ConvertToPyObject(const AbstractBasePtr &abstract);
  static py::object FetchPythonObject(const AbstractWrapperPtr &wrapper);
  static bool MarkObjectPiJItShouldCompile(const py::object &object);

  GraphBuildHelperPtr graph_builder_helper() const {
    if (!abstract_->has_user_data(kPijitBuildHelper)) {
      return nullptr;
    }
    return abstract_->user_data<GraphBuildHelper>(kPijitBuildHelper);
  }
  void set_graph_builder_helper(const GraphBuildHelperPtr &graph_builder_helper) {
    abstract_->set_user_data(kPijitBuildHelper, graph_builder_helper);
  }

 private:
  AbstractBasePtr abstract_;
};

inline std::string ToString(const AbstractWrapperPtr &wrapper) {
  return wrapper != nullptr ? wrapper->ToString() : "NULL";
}
}  // namespace pijit
}  // namespace mindspore

#endif  // MINDSPORE_PI_JIT_GRAPH_CAPTURE_ABSTRACT_WRAPPER_H
