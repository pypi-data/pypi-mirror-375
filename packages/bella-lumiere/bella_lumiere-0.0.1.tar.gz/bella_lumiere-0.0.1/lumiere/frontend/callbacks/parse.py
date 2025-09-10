import ast
from typing import Any, TypeGuard

import dash

from lumiere.frontend.activation_functions import ActivationFunction

INPUT_ERROR_STYLE = {"border": "2px solid red"}


def _is_list(x: Any) -> TypeGuard[list[Any]]:
    return isinstance(x, list)


def _is_int_list(x: Any) -> TypeGuard[list[int]]:
    return _is_list(x) and all(isinstance(i, int) for i in x)


def parse_hidden_neurons(
    hidden_neurons: str,
) -> tuple[list[int] | dash.NoUpdate, dict[str, str]]:
    try:
        parsed = ast.literal_eval(hidden_neurons)
        if _is_int_list(parsed):
            return (parsed, {})
        raise ValueError("Invalid hidden neurons configuration")
    except:
        return (dash.no_update, INPUT_ERROR_STYLE)


def parse_activation_function(
    activation_function: str,
    kwarg_values: list[float | None],
    kwarg_ids: list[dict[str, str]],
) -> tuple[dict[str, Any] | dash.NoUpdate, list[dict[str, str]]]:
    styles: list[dict[str, str]] = []
    kwargs: dict[str, float] = {}
    is_valid = True
    for k, v in zip(kwarg_ids, kwarg_values):
        if k["activation-function"] == activation_function and v is None:
            styles.append(INPUT_ERROR_STYLE)
            is_valid = False
        else:
            styles.append({})

        if k["activation-function"] == activation_function and v is not None:
            kwargs[k["kwarg"]] = v

    if not is_valid:
        return dash.no_update, styles
    return ActivationFunction(activation_function, kwargs).to_dict(), styles
