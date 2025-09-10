import dash_bootstrap_components as dbc  # pyright: ignore[reportMissingTypeStubs]
from dash import dcc, html

import lumiere.frontend.config as cfg

hidden_neurons = dbc.Row(
    [
        dbc.Col(
            html.Label("Hidden neurons"),
            width=cfg.LABEL_WIDTH,
            className=cfg.LABEL_CLASS,
        ),
        dbc.Col(
            dbc.Input(
                id="hidden-neurons",
                type="text",
                value="[16, 8]",
                placeholder="Enter list of integers, e.g.: [16, 8]",
                autoComplete="off",
            ),
        ),
        dcc.Store(id="hidden-neurons-store"),
    ]
)
