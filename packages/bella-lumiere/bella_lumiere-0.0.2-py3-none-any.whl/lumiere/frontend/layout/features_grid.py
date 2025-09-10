import dash_bootstrap_components as dbc  # pyright: ignore[reportMissingTypeStubs]
from dash import dcc, html

import lumiere.frontend.config as cfg

features_grid = dbc.Row(
    [
        dbc.Col(
            html.Label("Input features grid"),
            width=cfg.LABEL_WIDTH,
            className=cfg.LABEL_CLASS,
        ),
        dbc.Col(
            [
                html.Div(
                    dcc.Upload(
                        html.Label(["Drag and Drop or ", html.A("Select a File")]),
                        id="features-grid-upload",
                    ),
                    id="features-grid-upload-container",
                ),
                dbc.Row(
                    [
                        dbc.Col(html.Label(id="features-grid-filename")),
                        dbc.Col(dbc.Button("X", id="features-grid-remove", n_clicks=0)),
                    ],
                    id="features-grid-uploaded",
                    style={"display": "none"},
                ),
            ],
            width=12 - cfg.LABEL_WIDTH,
        ),
        dbc.Modal(
            [
                dbc.ModalHeader("CSV Parsing Error"),
                dbc.ModalBody(""),
                dbc.ModalFooter(dbc.Button("Close", id="features-grid-error-close")),
            ],
            id="features-grid-error",
        ),
        dcc.Store(id="features-grid-store"),
    ]
)
