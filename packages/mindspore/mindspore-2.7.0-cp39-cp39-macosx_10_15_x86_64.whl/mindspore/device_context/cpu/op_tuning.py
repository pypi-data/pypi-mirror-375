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

"""Op tuning interfaces."""

from mindspore._c_expression import RuntimeConf
from mindspore import _checkparam as Validator
from mindspore._checkparam import args_type_check


@args_type_check(num=int)
def threads_num(num):
    """
    Set the threads number of CPU kernel used.

    The framework set the threads number of CPU kernel used are ``25`` by default.

    Args:
        num (int): The threads number of CPU kernel used.

    Examples:
        >>> import mindspore as ms
        >>> ms.set_device("Ascend", 1)
        >>> ms.device_context.cpu.op_tuning.threads_num(10)
    """
    if RuntimeConf.get_instance().is_op_threads_num_configured():
        raise RuntimeError("The 'threads_num' can not be set repeatedly.")

    num = Validator.check_positive_int(num, "num")

    return RuntimeConf.get_instance().set_op_threads_num(num)
