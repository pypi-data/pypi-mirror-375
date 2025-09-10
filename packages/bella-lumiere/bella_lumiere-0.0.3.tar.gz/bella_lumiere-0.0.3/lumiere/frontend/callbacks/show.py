def show_activation_function_kwargs(
    selected_activation: str, kwargs_ids: list[dict[str, str]]
) -> list[dict[str, str]]:
    return [
        {
            "display": (
                "block"
                if kwargs_id["activation-function"] == selected_activation
                else "none"
            )
        }
        for kwargs_id in kwargs_ids
    ]
