# Copyright 2024 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
"""
This module defines the PyboostInnerPrimGenerator class, which is responsible for generating Python primitive
wrappers for Pyboost operations. The generator constructs Python function definitions based on operator prototypes,
generates necessary import statements, and writes the generated content into Python source files.

The primary functionality is to take operator prototypes, extract relevant fields, and create Python function wrappers
that can be used to call the Pyboost primitive implementations.
"""

import os

import common.template as template
import common.gen_constants as K
from common.template import Template
from common.gen_utils import save_file
from common.base_generator import BaseGenerator
from common.op_proto import OpProto
from pyboost.op_template_parser import OpTemplateParser
from pyboost import pyboost_utils
import api.op_api_proto as op_api_proto


class TensorFuncRegCppGenerator(BaseGenerator):
    """
    Generates C++ tensor function registration code for different backends (Ascend, CPU, GPU).

    This class is responsible for generating header and implementation files required to register
    tensor functions, including device-specific dispatchers and function definitions.
    """

    def __init__(self):
        self.TENSOR_FUNC_CC_REG = template.TENSOR_FUNC_CC_REG
        self.TENSOR_FUNC_CALL_BODY = template.TENSOR_FUNC_CALL_BODY
        self.TENSOR_FUNC_OVERLOAD_CALL_BODY = template.TENSOR_FUNC_OVERLOAD_CALL_BODY
        self.TENSOR_API_HEADER = template.TENSOR_API_HEADER
        self.TENSOR_API_SOURCE = template.TENSOR_API_SOURCE
        self.TENSOR_FUNC_UTILS = template.TENSOR_FUNC_UTILS
        self.TENSOR_FUNC_UT_BODY = template.TENSOR_FUNC_UT_BODY
        self.TENSOR_FUNC_UT_OVERLOAD_BODY = template.TENSOR_FUNC_UT_OVERLOAD_BODY
        self.TENSOR_CPP_METHOD = template.TENSOR_CPP_METHOD

        self.func_def_reg = Template(
            "tensor_class->def(\"${func_name}\", TensorMethod${cpp_func_name});\n")
        self.single_case_template = Template(
            'case ${case_id}:\n'
            '  ${device_dispatcher}\n'
            '  break;\n'
        )
        self.single_case_in_ut_template = Template(
            'case ${case_id}:\n'
            '  ${device_dispatcher}\n'
        )
        self.device_dispatcher_template = Template(
            'if (backend == kAscendDevice || backend == kDavinciDevice) {\n'
            '  ${ascend_dispatcher}\n'
            '} else if (backend == kCPUDevice) {\n'
            '  ${cpu_dispatcher}\n'
            '} else if (backend == kGPUDevice) {\n'
            '  ${gpu_dispatcher}\n'
            '} else {\n'
            '  MS_LOG(ERROR) << "Device target is not supported!";\n'
            '  return py::none();\n'
            '}'
        )
        self.pyboost_return_template = Template(
            '${arg_handler_processor}\n'
            'MS_LOG(INFO) << "Call Tensor${class_name}";\n'
            'auto res = mindspore::pynative::'
            '${pyboost_function}(mindspore::prim::kPrim${class_name}, parse_args.src_types_, ${convert_args});\n'
            'trace::Capture(parse_args.arg_list_, mindspore::prim::kPrim${class_name}, &res);\n'
            'return res;\n'
        )
        self.callback_python_template = Template(
            'MS_LOG(INFO) << "Callback python method: ${py_method}";\n'
            'py::function fn = python_adapter::GetPyFn(\"mindspore.ops.tensor_method\", \"${py_method}\");\n'
            'py::object res = fn(self, *py_args, **py_kwargs);\n'
            'return res;\n'
        )
        self.callback_python_in_ut_template = Template(
            'MS_LOG(INFO) << "Callback python method in UT: ${py_method}";\n'
            'fn = python_adapter::GetPyFn(\"mindspore.ops.tensor_method\", \"${py_method}\");\n'
            'res = fn(self, *py_args, **py_kwargs);\n'
            'break;\n'
        )
        self.header_func_header_template = Template(
            "py::object TensorMethod${cpp_func_name}"
            "(const py::object &self, const py::args &py_args, const py::kwargs &py_kwargs);\n"
        )

    def generate(self, work_path, op_protos, func_protos_data, alias_func_mapping):
        """
        Generates C++ header and source files for tensor function registrations.

        Args:
            work_path (str): The directory where the generated files will be saved.
            op_protos (list): A list of tensor op prototypes.
            func_protos_data (dict): Dictionary mapping function names to lists of TensorFuncProto objects.
            alias_func_mapping (dict): A dictionary mapping function name to its alias function names.
        """

        all_op_func_data, single_op_func_data, overload_op_func_data, op_class_name_set = \
            op_api_proto.categorize_func_data(func_protos_data)

        tensor_method_list = self._get_op_enum_name_list(op_protos)
        func_call_body_list = []
        self._create_single_op_source_files(
            single_op_func_data, func_call_body_list)
        self._create_overload_op_source_files(
            overload_op_func_data, func_call_body_list)
        merge_func_call_body = pyboost_utils.merge_strings_by_chunk_size(
            func_call_body_list)
        ops_inc_head_set = set()
        for op_class_name in op_class_name_set:
            ops_inc_head_set.add(template.OP_DEF_INC_HEAD_TEMPLATE.replace(prefix_char=op_class_name[0].lower()))
        for i, func_body_chunk_str in enumerate(merge_func_call_body):
            tensor_api_source = self.TENSOR_API_SOURCE.replace(
                ops_inc=list(sorted(ops_inc_head_set)),
                tenosr_func_call_body=func_body_chunk_str)
            save_file(os.path.join(work_path, K.TENSOR_API_PATH), f"tensor_api_{i}.cc",
                      tensor_api_source)

        func_def_body_list, tensor_cpp_methods_list, tensor_api_declaration_list = self._get_sorted_func_def_body(
            all_op_func_data, alias_func_mapping)
        tensor_api_header = self.TENSOR_API_HEADER.replace(
            tensor_api_declaration_list=tensor_api_declaration_list)
        save_file(os.path.join(work_path, K.TENSOR_API_PATH), f"tensor_api.h",
                  tensor_api_header)
        self._generate_func_name_for_stub_tensor(
            work_path, tensor_cpp_methods_list)
        func_cc_reg = self.TENSOR_FUNC_CC_REG.replace(
            func_def_body=func_def_body_list)
        tensor_methods = self.TENSOR_FUNC_UTILS.replace(
            tensor_methods=tensor_method_list)

        save_file(os.path.join(work_path, K.TENSOR_FUNC_REGISTER_PATH),
                  "tensor_func_utils.h", tensor_methods)
        save_file(os.path.join(work_path, K.TENSOR_API_PATH),
                  "tensor_func_reg.cc", func_cc_reg)

    def _get_op_enum_name_list(self, op_protos):
        """
        Extracts operation class names and returns them as a formatted list.

        Args:
            op_protos (list): A list of operation prototype objects, where each object has an `op_class`
                              with a `name` attribute.

        Returns:
            str: A list of formatted strings, where each string is of the form 'k<name>,\n', where <name>
                  is the class name from the `op_class` attribute.

        """
        tensor_method_list = ""
        for op_proto in op_protos:
            if op_proto.op_dispatch is None or not op_proto.op_dispatch.enable:
                continue
            class_name = op_proto.op_class.name
            tensor_method_list += f"k{class_name}Reg,\n"
        return tensor_method_list

    def _generate_func_name_for_stub_tensor(self, work_path, tensor_cpp_methods_list):
        """
        Generates a Python file containing tensor C++ function methods list and saves it to the specified path.

        This function takes a list of C++ tensor methods, formats them into a Python script as a string,
        and writes this script to a file named `_tensor_cpp_method.py` under the provided working path.

        Args:
            work_path (str): The base directory where the generated file will be saved.
            tensor_cpp_methods_list (list): A list of tensor C++ method definitions to be included in the Python file.
        """
        tensor_cpp_methods_str = self.TENSOR_CPP_METHOD.replace(
            tensor_cpp_methods_list_str=str(tensor_cpp_methods_list))
        save_file(os.path.join(work_path, K.ADD_TENSOR_DOCS_PY_PATH),
                  "_tensor_cpp_method.py", tensor_cpp_methods_str)

    def _get_sorted_func_def_body(self, all_op_func_data, alias_func_mapping):
        """
        Generate sorted function definitions and headers for operations.

        This function processes a dictionary of operation function data and an alias mapping,
        producing two lists: one containing function definition bodies and another containing
        function header definitions.

        Args:
            all_op_func_data (dict): A dictionary where keys are function API names (str), and
                values are lists of function prototypes.
            alias_func_mapping (dict): A mapping of function names to a list of their alias names.

        Returns:
            tuple: A tuple containing two lists:
                - func_def_body_list (list of str): A list of formatted function definition strings.
                - tensor_cpp_methods_list (list of str): A list of formatted function header strings.
        """
        func_def_body_list = []
        tensor_cpp_methods_list = []
        tensor_api_declaration_list = ""
        for func_api_name, func_protos in all_op_func_data.items():
            cpp_func_name = pyboost_utils.format_func_api_name(func_api_name)
            if len(func_protos) == 1:
                func_proto = func_protos[0]
                func_name = func_proto.func_name
                func_def_body_list.append(self.func_def_reg.replace(
                    func_name=func_name, cpp_func_name=cpp_func_name))
                tensor_cpp_methods_list.append(func_name)
                tensor_api_declaration_list += self.header_func_header_template.replace(
                    cpp_func_name=cpp_func_name)
                if func_name in alias_func_mapping:
                    for alias_func_name in alias_func_mapping[func_name]:
                        func_def_body_list.append(
                            self.func_def_reg.replace(func_name=alias_func_name, cpp_func_name=cpp_func_name))
                        tensor_cpp_methods_list.append(alias_func_name)
            elif len(func_protos) > 1:
                func_def_body_list.append(
                    self.func_def_reg.replace(func_name=func_api_name, cpp_func_name=cpp_func_name))
                tensor_cpp_methods_list.append(func_api_name)
                tensor_api_declaration_list += self.header_func_header_template.replace(
                    cpp_func_name=cpp_func_name)
                if func_api_name in alias_func_mapping:
                    for alias_func_name in alias_func_mapping[func_api_name]:
                        func_def_body_list.append(self.func_def_reg.replace(func_name=alias_func_name,
                                                                            cpp_func_name=cpp_func_name))
                        tensor_cpp_methods_list.append(alias_func_name)
        return func_def_body_list, tensor_cpp_methods_list, tensor_api_declaration_list

    def _create_single_op_source_files(self, single_op_func_data, func_call_body_list):
        """
        Generates the list of call body strings for single operation functions.

        Args:
            single_op_func_data (dict): Dictionary of tensor function prototypes with only one definition.

        Returns:
            list: Updated str list for generating C++ function call bodies.
        """
        for func_api_name, func_proto in single_op_func_data.items():
            func_name = func_proto.func_name
            cpp_func_name = pyboost_utils.format_func_api_name(func_api_name)
            device_dispatcher_str = self._get_device_dispatchers_str(
                func_proto)
            signature_str = self._generate_single_signature_str(
                func_proto.op_proto, func_proto.kw_only_args, func_proto.varargs
            )
            op_args = func_proto.op_proto.op_args
            max_size = len(op_args)
            self_index = self._get_input_tensor_index(func_proto)
            ut_body = self.TENSOR_FUNC_UT_BODY.replace(
                py_method=func_proto.py_method)
            tensor_func_single_call_body = self.TENSOR_FUNC_CALL_BODY.replace(cpp_func_name=cpp_func_name,
                                                                              func_name=func_name,
                                                                              device_dispatcher=device_dispatcher_str,
                                                                              signatures=signature_str,
                                                                              max_args=max_size,
                                                                              self_index=self_index,
                                                                              ut_body=ut_body)
            func_call_body_list.append(tensor_func_single_call_body)

    def _create_overload_op_source_files(self, overload_op_func_data, func_call_body_list):
        """
        Generates the list of call body strings for overloaded operation functions.

        Args:
            overload_op_func_data (dict): Dictionary of tensor function prototypes with overloaded definitions.

        Returns:
            list: Updated str list for generating C++ function call bodies.
        """
        for func_api_name, func_protos in overload_op_func_data.items():
            tensor_func_overload_call_body = self._get_overload_func_call_str(
                func_api_name, func_protos)
            func_call_body_list.append(tensor_func_overload_call_body)

    def _get_overload_func_call_str(self, func_api_name, func_protos):
        """
        Generates C++ call body string for overloaded tensor functions.

        Args:
            func_api_name (str): Name of the function API.
            func_protos (list): List of TensorFuncProto objects representing the function prototypes.

        Returns:
            str: Generated call body string for the overloaded functions.
        """
        signatures_str = self._generate_func_signatures_list_str(func_protos)
        dispatch_cases = self._get_dispatch_cases(func_protos)
        ut_dispatch_cases = self._get_ut_dispatch_cases(func_protos)
        ut_overload_body = self.TENSOR_FUNC_UT_OVERLOAD_BODY.replace(
            ut_dispatch_cases=ut_dispatch_cases)

        max_size = 0
        self_index = 0
        for tensor_proto in func_protos:
            op_proto = tensor_proto.op_proto
            op_args = op_proto.op_args
            max_size = max(len(op_args), max_size)
            self_index = self._get_input_tensor_index(tensor_proto)
        cpp_func_name = pyboost_utils.format_func_api_name(func_api_name)
        overload_func_call_str = self.TENSOR_FUNC_OVERLOAD_CALL_BODY.replace(cpp_func_name=cpp_func_name,
                                                                             func_name=func_api_name,
                                                                             signatures=signatures_str,
                                                                             dispatch_cases=dispatch_cases,
                                                                             max_args=max_size,
                                                                             self_index=self_index,
                                                                             ut_overload_body=ut_overload_body)
        return overload_func_call_str

    def _generate_func_signatures_list_str(self, func_protos) -> str:
        """
        Generates function signatures as a string from the given prototypes.

        Args:
            func_protos (list): List of TensorFuncProto objects representing the function prototypes.

        Returns:
            str: Generated function signatures string.
        """
        sig_str = ''
        first_sig = True
        for tensor_proto in func_protos:
            op_proto = tensor_proto.op_proto
            if not first_sig:
                sig_str += ',\n'
            first_sig = False
            sig_str += self._generate_single_signature_str(
                op_proto, tensor_proto.kw_only_args, tensor_proto.varargs)
        return sig_str

    def _generate_single_signature_str(self, op_proto: OpProto, kw_only_args, varargs) -> str:
        op_parser = OpTemplateParser(op_proto)
        return op_parser.generate_signature_str(kw_only_args, varargs, is_tensor_api=True)

    def _get_input_tensor_index(self, func_proto):
        """
        Get index of input.

        Args:
            func_proto (TensorFuncProto): Function prototype to generate dispatch strings for.

        Returns:
            int: Index of input.
        """
        op_name = func_proto.op_proto.op_class.name
        op_args = func_proto.op_proto.op_args
        if op_name in K.INPUT_NAME_MAP:
            self_index = [i for i in range(
                len(op_args)) if op_args[i].arg_name == K.INPUT_NAME_MAP[op_name]]
        else:
            self_index = [i for i in range(
                len(op_args)) if op_args[i].arg_name in K.INPUT_ARGS_NAME]
        if len(self_index) != 1:
            raise ValueError(
                f'There must be only one field named \'input\'. But got {len(self_index)} in {op_name}')
        return self_index

    def _get_dispatch_cases(self, func_protos):
        """
        Generates C++ switch-case statements for dispatching tensor function calls.

        Args:
            func_protos (list): List of TensorFuncProto objects representing the function prototypes.

        Returns:
            str: Generated switch-case dispatch statements.
        """
        dispatch_cases_str = ''
        for idx, func_proto in enumerate(func_protos):
            device_dispatcher_str = self._get_device_dispatchers_str(
                func_proto)
            dispatch_cases_str += self.single_case_template.replace(case_id=idx,
                                                                    device_dispatcher=device_dispatcher_str)
        dispatch_cases_str += 'default:\n'
        dispatch_cases_str += '  return py::none();'
        return dispatch_cases_str

    def _get_ut_dispatch_cases(self, func_protos):
        """
        Generates C++ switch-case statements for dispatching tensor function calls.

        Args:
            func_protos (list): List of TensorFuncProto objects representing the function prototypes.

        Returns:
            str: Generated switch-case dispatch statements.
        """
        dispatch_cases_str = ''
        for idx, func_proto in enumerate(func_protos):
            device_dispatcher_str = self.callback_python_in_ut_template.replace(
                py_method=func_proto.py_method)
            dispatch_cases_str += self.single_case_in_ut_template.replace(case_id=idx,
                                                                          device_dispatcher=device_dispatcher_str)
        dispatch_cases_str += 'default:\n'
        dispatch_cases_str += '  res = py::none();'
        return dispatch_cases_str

    def _get_device_dispatchers_str(self, func_proto):
        """
        Generates device-specific dispatch strings for the given function prototype.

        Args:
            func_proto (TensorFuncProto): Function prototype to generate dispatch strings for.

        Returns:
            str: Generated device-specific dispatch string.
        """
        ascend_dispatcher_str = self._get_single_device_dispatcher_str(
            func_proto, 'ascend')
        cpu_dispatcher_str = self._get_single_device_dispatcher_str(
            func_proto, 'cpu')
        gpu_dispatcher_str = self._get_single_device_dispatcher_str(
            func_proto, 'gpu')
        device_dispatcher_str = self.device_dispatcher_template.replace(ascend_dispatcher=ascend_dispatcher_str,
                                                                        cpu_dispatcher=cpu_dispatcher_str,
                                                                        gpu_dispatcher=gpu_dispatcher_str)
        return device_dispatcher_str

    def _get_single_device_dispatcher_str(self, func_proto, device):
        """
        Generates the dispatch string for a specific device.

        Args:
            func_proto (TensorFuncProto): Function prototype to generate the dispatcher for.
            device (str): Device type ('ascend', 'cpu', 'gpu').

        Returns:
            str: Generated device dispatcher string.
        """
        func_proto_device = getattr(func_proto, device)
        if func_proto_device == 'pyboost':
            arg_handler_processor_str = self._get_arg_handler_processor(func_proto.func_name, func_proto.op_proto)
            op_parser = OpTemplateParser(func_proto.op_proto)
            op_pyboost_func_name = op_parser.get_pyboost_func_name() + "_OP"
            convert_args_str = op_parser.get_convert_args_str(func_proto.op_proto, is_tensor_api=True)
            self_index = op_parser.get_input_tensor_index(func_proto.op_proto)
            return self.pyboost_return_template.replace(arg_handler_processor=arg_handler_processor_str,
                                                        class_name=func_proto.op_proto.op_class.name,
                                                        pyboost_function=op_pyboost_func_name,
                                                        self_index=self_index,
                                                        convert_args=convert_args_str)

        if func_proto_device == 'py_method':
            return self.callback_python_template.replace(py_method=func_proto.py_method)

        raise TypeError("Only support pyboost or python_method.")

    def _get_arg_handler_processor(self, func_name, op_proto):
        op_parser = OpTemplateParser(op_proto)
        return op_parser.get_arg_handler_processor(func_name, op_proto, is_tensor_api=True)
