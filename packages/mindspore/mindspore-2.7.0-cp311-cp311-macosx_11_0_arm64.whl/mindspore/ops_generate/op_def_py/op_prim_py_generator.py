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
Module for generating Python primitive operator definitions from specifications.
"""

import os

import common.gen_constants as K
import common.gen_utils as gen_utils
import common.template as template
from common.base_generator import BaseGenerator
from common.op_proto import OpProto
from common.template import Template
from pyboost import pyboost_utils


class OpPrimPyGenerator(BaseGenerator):
    """
    Generates Python code for primitive operators based on provided specifications.
    """

    def __init__(self):
        """
        Initializes the generator with a template for defining operator primitive classes.
        """
        self.op_prim_class_define_template = template.OP_PRIM_CLASS_DEFINE_TEMPLATE

    def generate(self, work_path, op_protos, doc_dict, file_pre):
        """
        Generates Python code for operator primitives and saves it to a file.

        Args:
            work_path (str): The directory to save the generated files.
            op_protos (list): A list of operator prototypes.
            doc_dict (dict): A dictionary containing documentation strings.
            file_pre (str): The prefix for the generated file names.
        """
        gen_py = ""
        for op_proto in op_protos:
            if op_proto.op_class.disable:
                continue

            inputs_args, inputs_default, init_args, args_assign, init_args_with_default, args_handlers = (
                self._process_args(op_proto))

            # add class description
            class_desc = self._generate_class_desc(op_proto, inputs_args, init_args, doc_dict)

            # add signature
            signature_code = self._generate_py_op_signature(op_proto, inputs_args, inputs_default)

            # add deprecated
            deprecated_code = generate_py_op_deprecated(op_proto.op_deprecated)

            # add __init__ method code
            init_method = self._generate_init_code(args_assign, init_args_with_default, op_proto)

            # add __call__ method code
            call_method = self._generate_call_code(args_handlers, init_args, inputs_args, inputs_default, op_proto)

            # generate op prim class define
            op_prim_class_define = self.op_prim_class_define_template.replace(class_name=op_proto.op_class.name,
                                                                              class_desc=class_desc,
                                                                              signature_code=signature_code,
                                                                              deprecated_code=deprecated_code,
                                                                              init_method=init_method,
                                                                              call_method=call_method)
            op_prim_class_define += "\n" if call_method.endswith("\n") else ""
            gen_py += op_prim_class_define

            # add prim_op_object
            if not init_args:
                gen_py += f"\n\n{op_proto.op_name}_op={op_proto.op_class.name}()\n"

        pyboost_import_header = self.generate_pyboost_import_header(op_protos)
        res_str = template.PY_LICENSE_STR + \
            template.OPS_PY_PRIM_HEADER + pyboost_import_header + gen_py

        save_path = os.path.join(work_path, K.PY_AUTO_GEN_PATH)
        file_name = f"{file_pre}_ops_prim.py"
        gen_utils.save_file(save_path, file_name, res_str)

    def generate_pyboost_import_header(self, op_protos) -> str:
        """
        Generates import statements for PyBoost primitives.

        Args:
            op_protos (list): A list of operator prototypes.

        Returns:
            str: A string containing import statements.
        """
        pyboost_import_header = ''
        import_pyboost = Template("from mindspore._c_expression import $var\n")
        for op_proto in op_protos:
            if op_proto.op_dispatch and op_proto.op_dispatch.enable:
                header = import_pyboost.replace(var=pyboost_utils.get_pyboost_name(op_proto.op_name))
                pyboost_import_header += header
        return pyboost_import_header

    def _process_args(self, op_proto: OpProto):
        """
        Processes operator arguments to categorize them for code generation.

        Args:
            op_proto (OpProto): The operator prototype.

        Returns:
            tuple: A tuple containing processed arguments.
        """
        inputs_name = []
        args_name = []
        args_assign = []
        inputs_default = {}
        init_args_with_default = []
        args_handlers = {}

        for arg in op_proto.op_args:
            # step1: get args infos:
            if arg.is_prim_init:
                # step1.1: get args name:
                args_name.append(arg.arg_name)
                # step1.2: get args assign with default value:
                if arg.default is not None:
                    init_args_with_default.append(f"""{arg.arg_name}={arg.default}""")
                else:
                    init_args_with_default.append(f"""{arg.arg_name}""")

                # step1.3: get args set prim arg expression:
                assign_str = self._get_assign_str_by_type_it(op_proto.op_class.name, arg)
                if arg.arg_handler:
                    assign_str = (
                        f'        self._set_prim_arg_with_handler('
                        f'"{arg.arg_name}", {assign_str}, {arg.arg_handler})'
                    )
                else:
                    assign_str = f"""        self._set_prim_arg("{arg.arg_name}", {assign_str})"""
                args_assign.append(assign_str)
            # step2: get inputs infos:
            else:
                # step2.1: get inputs name:
                inputs_name.append(arg.arg_name)

                # step2.2: get default value of inputs:
                if arg.default is not None:
                    inputs_default[arg.arg_name] = arg.default

                # step2.3: get args_handler functions for inputs
                if arg.arg_handler:
                    args_handlers[arg.arg_name] = arg.arg_handler

        return inputs_name, inputs_default, args_name, args_assign, init_args_with_default, args_handlers

    def _get_assign_str_by_type_it(self, class_name, arg):
        """
        Generates assignment string with type casting.

        Args:
            class_name (str): The name of the class.
            arg (OpArg): The operator argument.

        Returns:
            str: A string representing the assignment.
        """
        assign_str = ""
        type_cast = arg.type_cast
        if type_cast:
            assign_str += f"type_it('{class_name}', '{arg.arg_name}', {arg.arg_name}, "
            if len(type_cast) == 1:
                assign_str += gen_utils.get_type_str(type_cast[0]) + ', '
            else:
                assign_str += '(' + ', '.join(gen_utils.get_type_str(ct) for ct in type_cast) + '), '
            assign_str += gen_utils.get_type_str(arg.arg_dtype) + ')'
        else:
            assign_str = arg.arg_name
        return assign_str

    def _generate_class_desc(self, op_proto: OpProto, input_args, init_args, doc_dic):
        """
        Generates a class description based on the operator prototype.

        Args:
            op_proto (OpProto): The operator prototype.
            input_args (list): List of input argument names.
            init_args (list): List of initialization argument names.
            doc_dic (dict): Documentation dictionary.

        Returns:
            str: A string containing the class description.
        """
        if op_proto.op_function and op_proto.op_function.disable:
            # if function disabled, function name is equal to operator_name
            return gen_utils.get_op_description(op_proto.op_name, doc_dic)

        # If function is a released API, refer to the function doc.
        init_args_str = ", ".join(init_args)
        input_args_str = ", ".join(input_args)
        args_str = ", ".join(input_args + init_args)

        description_template = Template(template.PRIMITIVE_CLASS_DESC)
        description_str = description_template.replace(class_name=op_proto.op_class.name,
                                                       init_args_str=init_args_str,
                                                       input_args_str=input_args_str,
                                                       func_name=op_proto.op_function.name,
                                                       args_str=args_str)
        return description_str

    def _generate_init_code(self, args_assign, init_args_with_default, op_proto: OpProto):
        """
        Generates the __init__ method code for the operator primitive class.

        Args:
            args_assign (list): List of argument assignment strings.
            init_args_with_default (list): List of initialization arguments with default values.
            op_proto (OpProto): The operator prototype.

        Returns:
            str: A string containing the __init__ method code.
        """
        init_code_str = ""
        init_args_list_str = ""
        if init_args_with_default:
            init_args_list_str += ", " + f"""{", ".join(init_args_with_default) if init_args_with_default else ""}"""
        init_code = "\n".join(args_assign)
        init_code = self._get_init_code(init_code, op_proto)
        init_code_str += f"    @prim_arg_register\n"
        init_code_str += f"    def __init__(self{init_args_list_str}):\n"
        init_code_str += f"{init_code}\n"
        init_code_str += f"\n"
        return init_code_str

    def _get_init_code(self, init_code, op_proto: OpProto):
        """
        Generates additional initialization code for the operator primitive class.

        Args:
            init_code (str): Existing initialization code.
            op_proto (OpProto): The operator prototype.

        Returns:
            str: A string containing additional initialization code.
        """
        labels_dic = op_proto.op_labels
        if labels_dic:
            if init_code:
                init_code += "\n"
            init_code += "\n".join([f"""        self.add_prim_attr("{k}", {v})""" for k, v in labels_dic.items()])

        return init_code if init_code else f"""        pass"""

    def _generate_call_code(self, args_handlers, init_args, inputs_args, inputs_default, op_proto: OpProto):
        """
        Generates the __call__ method code for the operator primitive class.

        Args:
            args_handlers (dict): Dictionary of argument handlers.
            init_args (list): List of initialization argument names.
            inputs_args (list): List of input argument names.
            inputs_default (dict): Dictionary of default input values.
            op_proto (OpProto): The operator prototype.

        Returns:
            str: A string containing the __call__ method code.
        """
        call_code_str = ""
        call_args = []
        for name in inputs_args:
            call_args.append(f"{name}={inputs_default[name]}" if name in inputs_default else name)
        call_method_args_str = ", ".join(call_args)
        call_method_body_str = self._get_call_method_body_str(args_handlers, init_args, inputs_args, inputs_default,
                                                              op_proto)
        call_code_str += f"""    def __call__(self, {call_method_args_str}):"""
        call_code_str += f"""{call_method_body_str}"""
        return call_code_str

    def _get_call_method_body_str(self, args_handlers, init_args, inputs_args, inputs_default, op_proto: OpProto):
        """
        Generates the body of the __call__ method.

        Args:
            args_handlers (dict): Dictionary of argument handlers.
            init_args (list): List of initialization argument names.
            inputs_args (list): List of input argument names.
            inputs_default (dict): Dictionary of default input values.
            op_proto (OpProto): The operator prototype.

        Returns:
            str: A string containing the body of the call method.
        """
        call_args_list_str = ""
        if inputs_args:
            args_with_handler = []
            for arg in inputs_args:
                if arg in args_handlers:
                    is_optional = inputs_default.get(arg) == "None"
                    args_with_handler.append(
                        _generate_arg_handler(op_proto.op_class.name, arg, args_handlers[arg], is_optional))
                else:
                    args_with_handler.append(arg)
            call_args_list_str += ", ".join(args_with_handler)
        if init_args:
            call_args_list_str += ", "
            call_args_list_str += ", ".join([f'self.{arg}' for arg in init_args])

        call_method_body_str = ""
        is_pyboost = op_proto.op_dispatch and op_proto.op_dispatch.enable
        if is_pyboost:
            call_method_body_str += f"""
        # Add for jit context.
        if jit_context() and jit_context().compiled:
            return jit_context().default_output()"""
            pyboost_func_name = pyboost_utils.get_pyboost_name(op_proto.op_name)
            call_method_body_str += f"""
        res = {pyboost_func_name}(self, [{call_args_list_str}])"""
            call_method_body_str += f"""
        # Add for jit context.
        if jit_context():
            return jit_context().run_op(self, res, {call_args_list_str})
        return res\n"""
        else:
            call_method_body_str += f"""
        return super().__call__({call_args_list_str})\n"""
        return call_method_body_str

    def _generate_py_op_signature(self, op_proto: OpProto, args_name, args_default):
        """
        Generates the __mindspore_signature__ for the operator.

        Args:
            op_proto (OpProto): The operator prototype.
            args_name (list): List of argument names.
            args_default (dict): Dictionary of default argument values.

        Returns:
            str: A string containing the __mindspore_signature__ code.
        """
        op_name = op_proto.op_name
        args_signature = op_proto.op_args_signature

        if args_signature is None and not args_default:
            return ''

        signature_code = f"""\n    __mindspore_signature__ = """

        # Init rw.
        read_list, ref_list, write_list = gen_utils.init_args_signature_rw(args_signature)
        _check_signature_arg_valid(op_name, write_list, args_name)
        _check_signature_arg_valid(op_name, read_list, args_name)
        _check_signature_arg_valid(op_name, ref_list, args_name)

        # Init dtype group.
        same_dtype_groups, dtype_count = gen_utils.get_same_dtype_groups(args_signature, args_name)
        _check_signature_arg_valid(op_name, list(same_dtype_groups.keys()), args_name)

        # Only one dtype_group is set.
        if dtype_count == 1 and not any([write_list, read_list, ref_list, args_default]):
            signature_code += '('
            for _ in range(len(args_name) - 1):
                signature_code += 'sig.sig_dtype.T, '
            signature_code += 'sig.sig_dtype.T)\n'
            return signature_code

        # Set sig.make_sig.
        signature_code += f""" (\n"""
        for arg_name in args_name:
            signature_code += f"""        sig.make_sig('{arg_name}'"""
            signature_code += signature_get_rw_label(arg_name, write_list, read_list, ref_list)
            if arg_name in same_dtype_groups:
                signature_code += f""", """ + signature_get_dtype_label(same_dtype_groups[arg_name])
            if arg_name in args_default:
                signature_code += f""", default=""" + str(args_default[arg_name])
            signature_code += f"""),\n"""
        signature_code += f"""    )\n"""
        return signature_code


def _check_signature_arg_valid(op_name, sig_arg_names, args_names):
    """
    Validates that all signature arguments are present in the list of argument names.

    Args:
        op_name (str): The name of the operator.
        sig_arg_names (list): List of signature argument names.
        args_names (list): List of actual argument names.

    Raises:
        ValueError: If a signature argument is not found in the list of argument names.
    """
    for sig_arg_name in sig_arg_names:
        if sig_arg_name not in args_names:
            raise ValueError(f"Op {op_name} has no input arg named '{sig_arg_name}'!")


def signature_get_dtype_label(index):
    """
    Generates the label for the data type in the signature.

    Args:
        index (int): The index of the data type.

    Returns:
        str: The label string for the data type.
    """
    dtype_index = ''
    if index > 0:
        dtype_index = f"""{index}"""
    return f"""dtype=sig.sig_dtype.T{dtype_index}"""


def signature_get_rw_label(arg_name, write_list, read_list, ref_list):
    """
    Determines the read-write label for an argument in the signature.

    Args:
        arg_name (str): The name of the argument.
        write_list (list): List of arguments that are writable.
        read_list (list): List of arguments that are readable.
        ref_list (list): List of arguments that are references.

    Returns:
        str: The read-write label for the argument.
    """
    for rw_arg_name in write_list:
        if rw_arg_name == arg_name:
            return ', sig.sig_rw.RW_WRITE'
    for read_arg_name in read_list:
        if read_arg_name == arg_name:
            return ', sig.sig_rw.RW_READ'
    for ref_arg_name in ref_list:
        if ref_arg_name == arg_name:
            return ', sig.sig_rw.RW_REF'
    return ''


def generate_py_op_deprecated(deprecated):
    """
    Generates the deprecated decorator for an operator.

    Args:
        deprecated (dict): The deprecation information.

    Returns:
        str: A string containing the deprecated decorator.
    """
    if deprecated is None:
        return ''
    version = deprecated.get("version")
    if version is None:
        raise ValueError("The version of deprecated can't be None.")
    substitute = deprecated.get("substitute")
    if substitute is None:
        raise ValueError("The substitute of deprecated can't be None.")
    use_substitute = deprecated.get("use_substitute")
    if use_substitute is None:
        raise ValueError("The use_substitute of deprecated can't be None.")
    if use_substitute is not True and use_substitute is not False:
        raise ValueError(f"The use_substitute must be True or False, but got {use_substitute}")

    deprecated = f"""    @deprecated("{version}", "{substitute}", {use_substitute})\n"""
    return deprecated


def _generate_arg_handler(class_name, arg, arg_handler, is_optional):
    """
    Generates the argument handler call for an argument.

    Args:
        class_name (str): The name of the class.
        arg (str): The name of the argument.
        arg_handler (str): The handler function for the argument.
        is_optional (bool): Indicates whether the argument is optional.

    Returns:
        str: The argument handler call string.
    """
    arg_handler_call = f"""{arg_handler}('{class_name}', '{arg}', {arg})"""
    if is_optional:
        arg_handler_call = f"""{arg} if {arg} is None else {arg_handler_call}"""
    return arg_handler_call
