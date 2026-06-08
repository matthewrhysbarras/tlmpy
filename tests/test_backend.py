import importlib.util

import pytest

from tlmpy.array_backend import get_array_module


def test_numpy_backend():
    assert get_array_module("numpy").__name__ == "numpy"


def test_cupy_missing_message():
    if importlib.util.find_spec("cupy") is not None:
        pytest.skip("CuPy installed")
    with pytest.raises(ImportError, match=r"CuPy backend requested.*tlmpy\[cuda\]"):
        get_array_module("cupy")

