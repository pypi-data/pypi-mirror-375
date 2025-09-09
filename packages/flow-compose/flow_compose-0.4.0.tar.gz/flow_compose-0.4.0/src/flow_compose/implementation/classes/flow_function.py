# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Generic, Any

from flow_compose.implementation.classes import base
from flow_compose.types import ReturnType


class FlowFunction(base.FlowFunction[ReturnType], Generic[ReturnType]):
    def __call__(self, *args: Any, **kwargs: Any) -> ReturnType:
        return self._flow_function(*args, **kwargs)
