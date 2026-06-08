"""Validation metrics."""

from __future__ import annotations

import numpy as np


def relative_l2_error(a, b) -> float:
    a = np.asarray(a)
    b = np.asarray(b)
    denom = np.linalg.norm(b.ravel())
    return float(np.linalg.norm((a - b).ravel()) / denom) if denom else float(np.linalg.norm(a.ravel()))


def max_abs_error(a, b) -> float:
    return float(np.max(np.abs(np.asarray(a) - np.asarray(b))))


def assert_close_relative(a, b, tol: float) -> None:
    err = relative_l2_error(a, b)
    if err > tol:
        raise AssertionError(f"relative L2 error {err:g} exceeds tolerance {tol:g}")

