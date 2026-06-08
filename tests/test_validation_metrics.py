import numpy as np
import pytest

from tlmpy.validation.metrics import assert_close_relative, max_abs_error, relative_l2_error


def test_metrics():
    a = np.array([1.0, 2.0])
    assert relative_l2_error(a, a) == 0.0
    assert max_abs_error(a, a) == 0.0
    assert relative_l2_error(a * 2, a) == 1.0
    with pytest.raises(AssertionError):
        assert_close_relative(a * 2, a, 0.5)

