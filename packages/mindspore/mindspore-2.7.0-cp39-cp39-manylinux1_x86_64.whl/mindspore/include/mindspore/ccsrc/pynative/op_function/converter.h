/**
 * Copyright 2023-2024 Huawei Technologies Co., Ltd
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
#ifndef MINDSPORE_CCSRC_PIPELINE_PYNATIVE_OP_FUNCTION_CONVERTER_H
#define MINDSPORE_CCSRC_PIPELINE_PYNATIVE_OP_FUNCTION_CONVERTER_H
#include <memory>
#include <string>
#include <vector>
#include <utility>
#include <unordered_map>
#include "pynative/base.h"
#include "pynative/pynative_execute.h"
#include "include/common/utils/tensor_py.h"
#include "include/common/pybind_api/api_register.h"
#include "include/common/utils/primfunc_utils.h"
#include "ops/op_def.h"
#include "include/common/visible.h"

namespace mindspore {
namespace pynative {
using ConvertPair = std::pair<ops::OP_DTYPE, ops::OP_DTYPE>;
struct ParserArgs;

static std::unordered_map<std::string, ops::OP_DTYPE> type_str_map = {
  {"int", ops::OP_DTYPE::DT_INT},
  {"float", ops::OP_DTYPE::DT_FLOAT},
  {"bool", ops::OP_DTYPE::DT_BOOL},
  {"number", ops::OP_DTYPE::DT_NUMBER},
  {"tuple[int]", ops::OP_DTYPE::DT_TUPLE_INT},
  {"tuple[float]", ops::OP_DTYPE::DT_TUPLE_FLOAT},
  {"tuple[bool]", ops::OP_DTYPE::DT_TUPLE_BOOL},
  {"tuple[tensor]", ops::OP_DTYPE::DT_TUPLE_TENSOR},
  {"tuple[number]", ops::OP_DTYPE::DT_TUPLE_NUMBER},
  {"tuple[str]", ops::OP_DTYPE::DT_STR},
  {"list[int]", ops::OP_DTYPE::DT_LIST_INT},
  {"list[float]", ops::OP_DTYPE::DT_LIST_FLOAT},
  {"list[bool]", ops::OP_DTYPE::DT_LIST_BOOL},
  {"list[tensor]", ops::OP_DTYPE::DT_LIST_TENSOR},
  {"list[number]", ops::OP_DTYPE::DT_LIST_NUMBER},
  {"list[str]", ops::OP_DTYPE::DT_LIST_STR},
  {"tensor", ops::OP_DTYPE::DT_TENSOR},
  {"str", ops::OP_DTYPE::DT_STR},
  {"type", ops::OP_DTYPE::DT_TYPE},
};

static std::unordered_map<std::string, ops::OP_DTYPE> type_not_in_yaml_str_map = {
  {"tuple[any]", ops::OP_DTYPE::DT_TUPLE_ANY},
  {"list[any]", ops::OP_DTYPE::DT_LIST_ANY},
  {"any", ops::OP_DTYPE::DT_ANY},
};

class PYNATIVE_EXPORT ParserDefaultObjects {
 public:
  static ParserDefaultObjects &GetInstance();

  const py::object &Get(const std::string &default_str) {
    auto iter = objects_.find(default_str);
    if (iter != objects_.end()) {
      return *(iter->second);
    }
    MS_LOG(EXCEPTION) << "The default value should be initialized before being fetched.";
  }

  void Set(const ops::OP_DTYPE &type, const std::string &value, const std::string &kw_str) {
    objects_.try_emplace(kw_str, std::make_unique<py::object>(StrToPyObj(type, value)));
  }

  py::object StrToPyObj(const ops::OP_DTYPE &type, const std::string &str);

  void ClearRes() { objects_.clear(); }

 private:
  ParserDefaultObjects() {}
  ~ParserDefaultObjects() = default;
  DISABLE_COPY_AND_ASSIGN(ParserDefaultObjects);
  std::unordered_map<std::string, std::unique_ptr<py::object>> objects_;
};

// information of single parameter
struct FunctionParameter {
  explicit FunctionParameter(const std::string &fmt, bool is_kw_only);
  bool Check(const py::object &obj, ConvertPair &convert_type, int &error_idx) const;
  void SetDefaultObj(const std::string &str);
  const py::object &GetDefaultValue() { return ParserDefaultObjects::GetInstance().Get(default_str_); }

  ops::OP_DTYPE type_{ops::OP_DTYPE::DT_END};
  std::vector<ops::OP_DTYPE> cast_types_;
  std::string default_str_{""};
  bool optional_{false};
  bool allow_none_{false};
  bool kw_only_{false};
  std::string name_;
  bool is_any_{false};
  bool allow_vararg_{false};
};

// single overload
struct PYNATIVE_EXPORT FunctionSignature {
  explicit FunctionSignature(const std::string &fmt, int index, const std::string &name);
  bool CheckParamValid(const py::object &obj, const FunctionParameter &param, bool raise_error,
                       std::string *out_error_msg, ConvertPair &convert_type, int &error_idx);
  bool Parse(const py::list &args, const py::dict &kwargs, ParserArgs &parser_args, bool raise_error = false,
             std::string *out_error_msg = nullptr);
  bool RaiseParseKeywordArgsError(size_t nkwargs, bool raise_error, std::string *out_error_msg, size_t nargs,
                                  const py::dict &kwargs);
  std::string ToString();

  std::string name_;
  std::vector<FunctionParameter> params_;
  size_t max_pos_args_;
  size_t max_args_;
  size_t min_args_;
  // e.g. allow input.reshape(1, 2, 3) parse as input.reshape((1, 2, 3))
  bool allow_int_as_list_;
  int index_;
};
using FunctionSignaturePtr = std::shared_ptr<FunctionSignature>;

struct PYNATIVE_EXPORT ParserArgs {
 public:
  explicit ParserArgs(const FunctionSignaturePtr &signature) : signature_(signature) {
    arg_list_.resize(signature->params_.size());
    src_types_.resize(signature->params_.size());
    dst_types_.resize(signature->params_.size());
  }
  ValuePtr ConvertByParseDtype(size_t index);
  void InsertInputTensor(size_t index, const py::object &input);
  void SetArg(const py::object &arg, const ConvertPair &convert_type, size_t index);
  void ClearArgs();
  const int &GetOvertLoadIndex() { return signature_->index_; }
  void PrintConvertError(size_t index);
  // convert to basic type
  std::vector<int64_t> ToBasicIntVector(size_t index);
  int64_t ToBasicInt(size_t index);

  template <typename T>
  std::shared_ptr<T> Convert(size_t index) {
    if (index >= arg_list_.size()) {
      MS_LOG(EXCEPTION) << "Invalid index" << index << "for argument convert.";
    }
    auto convert = ConvertByParseDtype(index);
    if (convert != nullptr && convert->isa<T>()) {
      return convert->cast<std::shared_ptr<T>>();
    }
    PrintConvertError(index);
    return nullptr;
  }

  template <typename T>
  std::optional<std::shared_ptr<T>> ConvertOptional(size_t index) {
    if (index >= arg_list_.size()) {
      MS_LOG(EXCEPTION) << "Invalid index" << index << "for argument convert.";
    }
    const py::object &obj = arg_list_[index];
    if (py::isinstance<py::none>(obj)) {
      return std::nullopt;
    }
    return std::make_optional(Convert<T>(index));
  }

  FunctionSignaturePtr signature_;
  std::vector<py::object> arg_list_;
  // {src_type , dst_type} for convert
  std::vector<ops::OP_DTYPE> src_types_;
  std::vector<ops::OP_DTYPE> dst_types_;
};

// parser util
struct PYNATIVE_EXPORT PythonArgParser {
  explicit PythonArgParser(std::vector<std::string> fmts, const std::string &function_name);
  inline const ParserArgs Parse(const py::list &args, const py::dict &kwargs, const bool &is_method);
  const std::vector<std::string> GetParseTypeListString(const py::list &args, const py::dict &kwargs);
  std::string PrintParseError(const py::list &args, const py::dict &kwargs, const bool &is_method);

 private:
  std::vector<FunctionSignaturePtr> signatures_;
  std::string function_name_;
  size_t max_args_;
};

inline const ParserArgs PythonArgParser::Parse(const py::list &args, const py::dict &kwargs, const bool &is_method) {
  if (signatures_.size() == 1) {
    ParserArgs parser_args(signatures_[0]);
    signatures_[0]->Parse(args, kwargs, parser_args, true);
    return parser_args;
  }

  for (auto &signature : signatures_) {
    ParserArgs parser_args(signature);
    if (signature->Parse(args, kwargs, parser_args, false)) {
      return parser_args;
    }
  }
  MS_EXCEPTION(TypeError) << PrintParseError(args, kwargs, is_method);
}

PYNATIVE_EXPORT ValuePtr UnpackTensor(const py::object &input, const std::string &func_name);

class PYNATIVE_EXPORT Converter {
 public:
  explicit Converter(ops::OpDef *op_def);
  void Parse(const py::list &python_args);
  ValuePtr ToTensor(const py::list &python_args, size_t i);
  std::optional<ValuePtr> ToTensorOptional(const py::list &python_args, size_t i);
  template <typename T>
  ValueTuplePtr ToTensorList(const py::list &python_args, size_t i);
  template <typename T>
  std::optional<ValueTuplePtr> ToTensorListOptional(const py::list &python_args, size_t i);
  Int64ImmPtr ToInt(const py::list &python_args, size_t i);
  std::optional<Int64ImmPtr> ToIntOptional(const py::list &python_args, size_t i);
  template <typename T>
  ValueTuplePtr ToIntList(const py::list &python_args, size_t i);
  template <typename T>
  std::optional<ValueTuplePtr> ToIntListOptional(const py::list &python_args, size_t i);
  BoolImmPtr ToBool(const py::list &python_args, size_t i);
  std::optional<BoolImmPtr> ToBoolOptional(const py::list &python_args, size_t i);
  template <typename T>
  ValueTuplePtr ToBoolList(const py::list &python_args, size_t i);
  template <typename T>
  std::optional<ValueTuplePtr> ToBoolListOptional(const py::list &python_args, size_t i);
  FP32ImmPtr ToFloat(const py::list &python_args, size_t i);
  std::optional<FP32ImmPtr> ToFloatOptional(const py::list &python_args, size_t i);
  template <typename T>
  ValueTuplePtr ToFloatList(const py::list &python_args, size_t i);
  template <typename T>
  std::optional<ValueTuplePtr> ToFloatListOptional(const py::list &python_args, size_t i);
  ScalarPtr ToScalar(const py::list &python_args, size_t i);
  std::optional<ScalarPtr> ToScalarOptional(const py::list &python_args, size_t i);
  StringImmPtr ToString(const py::list &python_args, size_t i);
  std::optional<StringImmPtr> ToStringOptional(const py::list &python_args, size_t i);
  Int64ImmPtr ToDtype(const py::list &python_args, size_t i);
  std::optional<Int64ImmPtr> ToDtypeOptional(const py::list &python_args, size_t i);
  ValuePtr ConvertByCastDtype(const py::object &input, const ops::OpInputArg &op_arg, size_t i);
  ValueTuplePtr ConvertValueTupleByCastDtype(const py::list &python_args, const ops::OpInputArg &op_arg, size_t index);
  std::vector<int64_t> ConvertIntVectorByCastDtype(const py::list &python_args, const ops::OpInputArg &op_arg,
                                                   size_t index);
  int64_t ConvertIntByCastDtype(const py::list &python_args, const ops::OpInputArg &op_arg, size_t index);
  const std::vector<ops::OP_DTYPE> &source_type() const { return source_type_; }
  // basic type
  int64_t ToBasicInt(const py::list &python_args, size_t i);
  std::optional<int64_t> ToBasicIntOptional(const py::list &python_args, size_t i);
  std::vector<int64_t> ToBasicIntVector(const py::list &python_args, size_t i);
  std::optional<std::vector<int64_t>> ToBasicIntVectorOptional(const py::list &python_args, size_t i);

 private:
  ops::OpDefPtr op_def_;
  // If op not type cast, source_type is default type: DT_BEGIN, if op type cast, source_type is origin type.
  std::vector<ops::OP_DTYPE> source_type_;
};
}  // namespace pynative
}  // namespace mindspore
#endif  // MINDSPORE_CCSRC_PIPELINE_PYNATIVE_OP_FUNCTION_CONVERTER_H
