import dash
import dash_bootstrap_components as dbc  # pyright: ignore[reportMissingTypeStubs]
from dash import ALL, MATCH, Input, Output, State

from lumiere.frontend import callbacks, layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = layout

app.callback(  # pyright: ignore[reportUnknownMemberType]
    Output("features-grid-upload", "contents"),
    Output("features-grid-store", "data"),
    Output("features-grid-upload-container", "style"),
    Output("features-grid-uploaded", "style"),
    Output("features-grid-filename", "children"),
    Output("features-grid-remove", "n_clicks"),
    Input("features-grid-upload", "contents"),
    Input("features-grid-remove", "n_clicks"),
    State("features-grid-upload", "filename"),
    prevent_initial_call=True,
)(callbacks.upload_features_grid)

app.callback(  # pyright: ignore[reportUnknownMemberType]
    Output("hidden-neurons-store", "data"),
    Output("hidden-neurons", "style"),
    Input("hidden-neurons", "value"),
)(callbacks.parse_hidden_neurons)

app.callback(  # pyright: ignore[reportUnknownMemberType]
    Output(
        {"layer-type": MATCH, "element": "kwargs", "activation-function": ALL},
        "style",
    ),
    Input({"layer-type": MATCH, "element": "activation-function"}, "value"),
    State({"layer-type": MATCH, "element": "kwargs", "activation-function": ALL}, "id"),
)(callbacks.show_activation_function_kwargs)

app.callback(  # pyright: ignore[reportUnknownMemberType]
    Output(({"layer-type": MATCH, "element": "activation-function-store"}), "data"),
    Output({"layer-type": MATCH, "activation-function": ALL, "kwarg": ALL}, "style"),
    Input({"layer-type": MATCH, "element": "activation-function"}, "value"),
    Input({"layer-type": MATCH, "activation-function": ALL, "kwarg": ALL}, "value"),
    State({"layer-type": MATCH, "activation-function": ALL, "kwarg": ALL}, "id"),
)(callbacks.parse_activation_function)

app.callback(  # pyright: ignore[reportUnknownMemberType]
    Output("effective-prior", "figure"),
    Input("features-grid-store", "data"),
    Input("hidden-neurons-store", "data"),
    Input({"layer-type": "hidden", "element": "activation-function-store"}, "data"),
    Input({"layer-type": "output", "element": "activation-function-store"}, "data"),
    prevent_initial_call=True,
)(callbacks.update_effective_prior)
