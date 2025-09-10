from collections.abc import Sequence
from functools import partial
from itertools import product

import numpy as np
from p_tqdm import p_map  # pyright: ignore

from lumiere.backend import mlp
from lumiere.backend.activation_functions import sigmoid
from lumiere.backend.typings import ActivationFunction, Weights


def get_partial_dependence_values(
    weights: Weights,
    features_grid: Sequence[Sequence[float]],
    hidden_activation: ActivationFunction = sigmoid,
    output_activation: ActivationFunction = sigmoid,
) -> list[list[float]]:  # shape: (n_features, n_grid_points)
    inputs = np.array(list(product(*features_grid)), dtype=np.float64)
    all_pdvalues: list[list[float]] = []
    for feature_idx in range(len(features_grid)):
        pdvalues: list[float] = []
        grid_points = features_grid[feature_idx]
        for feature_value in grid_points:
            x = np.copy(inputs)
            x[:, feature_idx] = feature_value
            pdvalue = np.mean(
                mlp.forward(weights, x, hidden_activation, output_activation)
            )
            pdvalues.append(float(pdvalue))
        all_pdvalues.append(pdvalues)
    return all_pdvalues


def get_partial_dependence_values_distribution(
    weights: Sequence[Weights],
    features_grid: Sequence[Sequence[float]],
    hidden_activation: ActivationFunction = sigmoid,
    output_activation: ActivationFunction = sigmoid,
) -> list[list[list[float]]]:  # shape: (n_models,n_features, n_grid_points)
    return p_map(
        partial(
            get_partial_dependence_values,
            features_grid=features_grid,
            hidden_activation=hidden_activation,
            output_activation=output_activation,
        ),
        weights,
    )
