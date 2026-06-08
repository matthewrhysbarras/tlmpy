import pytest

from tlmpy import Grid2D


def test_valid_grid():
    g = Grid2D((4, 5), (0.1, 0.2))
    assert g.nx == 4
    assert g.extent == (0.4, 1.0)


def test_invalid_shape():
    with pytest.raises(ValueError):
        Grid2D((0, 5), (1.0, 1.0))


def test_invalid_spacing():
    with pytest.raises(ValueError):
        Grid2D((4, 5), (0.0, 1.0))

