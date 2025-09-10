import dash_bootstrap_components as dbc  # pyright: ignore[reportMissingTypeStubs]
from dash import dcc, html

import lumiere.frontend.config as cfg
from lumiere.frontend.activation_functions import ACTIVATION_FUNCTIONS, DEFAULT_KWARGS


def _get_args(layer_type: str, activation_function: str) -> list[dbc.Row]:
    default_kwargs = DEFAULT_KWARGS[activation_function]
    return [
        dbc.Row(
            [
                dbc.Col(
                    html.Label(kwarg.capitalize()),
                    className="text-end",
                    width=6,
                ),
                dbc.Col(
                    dbc.Input(
                        id={
                            "layer-type": layer_type,
                            "activation-function": activation_function,
                            "kwarg": kwarg,
                        },
                        placeholder=default,
                        value=default,
                        type="number",
                        autoComplete="off",
                    ),
                    width=6,
                ),
            ],
        )
        for kwarg, default in default_kwargs.items()
    ]


def get_activation_function(layer_type: str) -> dbc.Row:
    return dbc.Row(
        [
            dbc.Col(
                html.Label(f"{layer_type.capitalize()} activation"),
                width=cfg.LABEL_WIDTH,
                className=cfg.LABEL_CLASS,
            ),
            dbc.Col(
                [
                    dcc.Dropdown(
                        id={"layer-type": layer_type, "element": "activation-function"},
                        options={f: f for f in ACTIVATION_FUNCTIONS},
                        value="Sigmoid",
                        clearable=False,
                    ),
                    *[
                        dbc.Row(
                            _get_args(layer_type, activation_function),
                            id={
                                "layer-type": layer_type,
                                "element": "kwargs",
                                "activation-function": activation_function,
                            },
                        )
                        for activation_function in ACTIVATION_FUNCTIONS
                    ],
                ],
                width=12 - cfg.LABEL_WIDTH,
            ),
            dcc.Store(
                id={"layer-type": layer_type, "element": "activation-function-store"}
            ),
        ]
    )
