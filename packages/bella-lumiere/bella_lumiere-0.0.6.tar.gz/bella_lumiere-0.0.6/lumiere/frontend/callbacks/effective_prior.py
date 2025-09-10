from typing import Any

import dash
import numpy as np
import plotly.graph_objects as go

from lumiere.backend import get_effective_prior
from lumiere.frontend.activation_functions import ActivationFunction
from lumiere.frontend.callbacks.figures import plot_effective_prior


def update_effective_prior(
    features_grid: list[list[float]] | None,
    hidden_neurons: list[int],
    hidden_activation_data: dict[str, Any],
    output_activation_data: dict[str, Any],
) -> go.Figure | dash.NoUpdate:
    if features_grid is None:
        return plot_effective_prior([])
    hidden_activation = ActivationFunction.from_dict(hidden_activation_data)
    output_activation = ActivationFunction.from_dict(output_activation_data)

    effective_prior = get_effective_prior(
        features_grid=np.array(features_grid),
        hidden_neurons=hidden_neurons,
        hidden_activation=hidden_activation,
        output_activation=output_activation,
    )
    return plot_effective_prior(effective_prior)
