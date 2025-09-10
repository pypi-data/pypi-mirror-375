from collections.abc import Sequence
from functools import partial

import numpy as np
import shap  # pyright: ignore[reportMissingTypeStubs]
from numpy.typing import ArrayLike
from p_tqdm import p_map  # pyright: ignore

from lumiere.backend import mlp
from lumiere.backend.activation_functions import sigmoid
from lumiere.backend.typings import ActivationFunction, Weights


def get_shap_values(
    weights: Weights,
    inputs: ArrayLike,
    hidden_activation: ActivationFunction = sigmoid,
    output_activation: ActivationFunction = sigmoid,
) -> list[float]:  # length: n_features
    inputs = np.asarray(inputs, dtype=np.float64)
    model = partial(
        mlp.forward,
        weights,
        hidden_activation=hidden_activation,
        output_activation=output_activation,
    )
    explainer = shap.Explainer(model, inputs)
    return np.mean(np.abs(explainer(inputs).values), axis=0)  # pyright: ignore


def get_shap_values_distribution(
    weights: Sequence[Weights],
    inputs: ArrayLike,
    hidden_activation: ActivationFunction = sigmoid,
    output_activation: ActivationFunction = sigmoid,
) -> list[list[float]]:  # shape: (n_models, n_features)
    return p_map(
        partial(
            get_shap_values,
            inputs=inputs,
            hidden_activation=hidden_activation,
            output_activation=output_activation,
        ),
        weights,
    )
