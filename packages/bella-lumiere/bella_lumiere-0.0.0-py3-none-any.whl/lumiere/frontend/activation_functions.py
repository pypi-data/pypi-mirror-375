from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from lumiere.backend import relu, sigmoid, softplus
from lumiere.backend.typings import Array, ArrayLike

ACTIVATION_FUNCTIONS = {
    "ReLU": relu,
    "Softplus": softplus,
    "Sigmoid": sigmoid,
}

DEFAULT_KWARGS: dict[str, dict[str, float]] = defaultdict(dict)
DEFAULT_KWARGS["Sigmoid"] = {"lower": 0.0, "upper": 1.0, "shape": 1.0}


@dataclass
class ActivationFunction:
    type: str
    kwargs: dict[str, float]

    def __call__(self, x: ArrayLike) -> Array:
        return ACTIVATION_FUNCTIONS[self.type](x, **self.kwargs)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "kwargs": self.kwargs,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ActivationFunction":
        return cls(
            type=data["type"],
            kwargs=data["kwargs"],
        )
