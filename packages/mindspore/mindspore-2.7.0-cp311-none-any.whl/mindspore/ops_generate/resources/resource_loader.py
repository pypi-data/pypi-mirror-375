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

"""Module of base class for resource loader."""

from abc import ABC, abstractmethod
from typing import Dict

from .resource_list import ResourceType


class ResourceLoader(ABC):
    """
    Abstract class for resource loader.
    """
    @abstractmethod
    def load(self) -> Dict[ResourceType, object]:
        """
        Load resource.

        Returns:
            Dict[ResourceType, object]: The resource type and resource object map.
        """
        raise NotImplementedError
