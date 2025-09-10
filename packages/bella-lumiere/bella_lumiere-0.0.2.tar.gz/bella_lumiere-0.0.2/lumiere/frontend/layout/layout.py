import dash_bootstrap_components as dbc  # pyright: ignore[reportMissingTypeStubs]
from dash import dcc, html

from lumiere.frontend.layout.activation_functions import get_activation_function
from lumiere.frontend.layout.features_grid import features_grid
from lumiere.frontend.layout.hidden_neurons import hidden_neurons

left_column = dbc.Col(
    [
        html.Img(id="logo", src="/assets/logo.png"),
        features_grid,
        html.Hr(),
        hidden_neurons,
        html.Hr(),
        get_activation_function("hidden"),
        html.Hr(),
        get_activation_function("output"),
    ],
    id="left-column",
    className="column",
    width=4,
)

right_column = dbc.Col(
    [
        dcc.Graph(
            id="effective-prior",
            config={"modeBarButtonsToRemove": ["select2d", "lasso2d"]},
        )
    ],
    id="right-column",
    className="column",
)

layout = dbc.Container(dbc.Row([left_column, right_column]), fluid=True)
