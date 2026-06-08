"""Array IO helpers."""

from __future__ import annotations

import numpy as np


def save_array(path, array) -> None:
    np.save(path, np.asarray(array))


def load_array(path):
    return np.load(path)

