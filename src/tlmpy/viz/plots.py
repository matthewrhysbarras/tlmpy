"""Matplotlib plotting helpers."""

from __future__ import annotations


def _plt():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            'This example requires matplotlib. Install with: pip install -e ".[viz]"'
        ) from exc
    return plt


def plot_field(field, title=None, save_path=None):
    plt = _plt()
    fig, ax = plt.subplots()
    im = ax.imshow(field.T, origin="lower", aspect="equal")
    fig.colorbar(im, ax=ax)
    if title:
        ax.set_title(title)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig, ax


def plot_probe(time, values, title=None, save_path=None):
    plt = _plt()
    fig, ax = plt.subplots()
    ax.plot(time, values)
    ax.set_xlabel("time [s]")
    if title:
        ax.set_title(title)
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig, ax

