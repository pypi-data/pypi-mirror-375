from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import ArrayLike

Array = np.typing.NDArray[np.float64]
Weights = Sequence[Array]
ActivationFunction = Callable[[ArrayLike], Array]
