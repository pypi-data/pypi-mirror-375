# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
import inspect
from collections.abc import Callable
from typing import Any

from flow_compose.extensions.makefun_extension import with_signature
from flow_compose.implementation.classes.flow_argument import FlowArgument
from flow_compose.implementation.classes.flow_function import FlowFunction
from flow_compose.implementation.classes.flow_function_invoker import (
    FlowFunctionInvoker,
)
from flow_compose.implementation.decorators.base.flow import (
    get_flow_parameters,
    flow_invoker_common,
)
from flow_compose.types import (
    ReturnType,
)


def decorator(
    **flow_functions_configuration: FlowFunction[Any],
) -> Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]:
    def wrapper(wrapped_flow: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        flow_parameters = get_flow_parameters(
            flow_functions_configuration=flow_functions_configuration,
            wrapped_flow=wrapped_flow,
        )

        @with_signature(
            func_name=wrapped_flow.__name__,
            func_signature=inspect.Signature(flow_parameters.flow_signature_parameters),
        )
        def flow_invoker(**kwargs: Any) -> ReturnType:
            flow_invoker_common(
                flow_functions_configuration=flow_functions_configuration,
                flow_parameters=flow_parameters,
                wrapped_flow=wrapped_flow,
                flow_function_invoker_class=FlowFunctionInvoker,
                flow_argument_class=FlowArgument,
                kwargs=kwargs,
            )

            return wrapped_flow(**kwargs)

        return flow_invoker

    return wrapper
