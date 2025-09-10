# Copyright 2025 Huawei Technologies Co., Ltd
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
"""ms operator details viewer"""
import os
import struct
from abc import ABC
from enum import Enum
from typing import Dict, Any

from mindspore.profiler.common.file_manager import FileManager
from mindspore.profiler.analysis.viewer.base_viewer import BaseViewer
from mindspore.profiler.common.tlv_decoder import TLVDecoder
from mindspore.profiler.common.log import ProfilerLogger


class OperatorDetailsIndexEnum(Enum):
    """Operator details index defining."""

    NAME = 0
    INPUT_SHAPES = 1
    INPUT_TYPE = 2


class BaseEvent(ABC):
    """Base class for all event types."""

    def __init__(self, data: Dict):
        if not isinstance(data, dict):
            raise TypeError("Input data must be dict.")
        self._origin_data = data


class OperatorDetailsEvent(BaseEvent):
    """Operator details event."""

    FIX_DATA_FORMAT = ""
    FIX_DATA_SIZE = struct.calcsize(FIX_DATA_FORMAT)

    @property
    def name(self):
        """Get name."""
        return self._origin_data.get(OperatorDetailsIndexEnum.NAME.value, "")

    @property
    def input_shapes(self):
        """Get input_shapes."""
        return self._origin_data.get(OperatorDetailsIndexEnum.INPUT_SHAPES.value, "")

    @property
    def input_type(self):
        """Get input_type."""
        return self._origin_data.get(OperatorDetailsIndexEnum.INPUT_TYPE.value, "")


class MsOperatorDetailsViewer(BaseViewer):
    """Viewer for MindSpore operator_details profiling data."""

    FWK_BINARY_FILE_NAME = "mindspore.record_shapes"
    _OPERATOR_DETAILS_FILE_NAME = 'operator_details.csv'
    _COL_NAMES = ['Name', 'Input Shapes']

    def __init__(self, **kwargs):
        super().__init__()
        self._save_path = os.path.join(
            kwargs.get("ascend_profiler_output_path"),
            self._OPERATOR_DETAILS_FILE_NAME
        )
        self._ascend_ms_dir = kwargs.get("ascend_ms_dir")
        self._framework_path = kwargs.get("framework_path")
        ProfilerLogger.init(self._ascend_ms_dir)
        self._logger = ProfilerLogger.get_instance()

    def save(self, data: Dict[str, Any]) -> None:
        """Process and save operator_details profiling data."""
        self._logger.info("MsOperatorDetailsViewer start")
        try:
            file_exist = self._read_fwk_binary_file()
            if not file_exist:
                return
            self._calculate_operator_details_data()
            self._write_data()
        except Exception as e: # pylint: disable=W0703
            self._logger.error("Failed to save operator_details.csv: %s", e, exc_info=True)
        self._logger.info("MsOperatorDetailsViewer end")

    def _read_fwk_binary_file(self):
        """
        Read fwk binary file
        """
        self._logger.info("Read fwk binary file start")
        fwk_file_path = os.path.join(self._framework_path, self.FWK_BINARY_FILE_NAME)
        if not os.path.isfile(fwk_file_path):
            self._logger.warning("Fwk binary file %s does not exist.", fwk_file_path)
            return False
        raw_bin_data = FileManager.read_file_content(fwk_file_path, mode="rb")
        operator_details_decode_data = TLVDecoder.decode(
            raw_bin_data, OperatorDetailsEvent.FIX_DATA_FORMAT, OperatorDetailsEvent.FIX_DATA_SIZE
        )
        self._operator_details_events = [OperatorDetailsEvent(data) for data in operator_details_decode_data]
        self._logger.info("Read fwk binary file done, %d events", len(self._operator_details_events))
        return True

    def _calculate_operator_details_data(self):
        """
        Calculate operator details data
        """
        self._operator_details_data = [
            [event.name, event.input_shapes]
            for event in self._operator_details_events
        ]

    def _write_data(self) -> None:
        """
        Save operator statistics to a CSV file
        """
        if not self._operator_details_data:
            return
        self._logger.info("Save operator statistics start")
        FileManager.create_csv_file(self._save_path, self._operator_details_data, self._COL_NAMES)
        self._logger.info("Save operator statistics done")
