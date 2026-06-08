"""Simulation result containers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class SimulationResult:
    probes: dict[str, np.ndarray]
    time: np.ndarray
    dt: float
    metadata: dict = field(default_factory=dict)
    final_field: np.ndarray | None = None

    def save_npz(self, path) -> None:
        arrays = {"time": self.time, "dt": np.asarray(self.dt), "metadata": np.asarray(self.metadata)}
        for name, values in self.probes.items():
            arrays[f"probe__{name}"] = values
        if self.final_field is not None:
            arrays["final_field"] = self.final_field
        np.savez(Path(path), **arrays)

    @classmethod
    def load_npz(cls, path):
        data = np.load(Path(path), allow_pickle=True)
        probes = {k.removeprefix("probe__"): data[k] for k in data.files if k.startswith("probe__")}
        metadata = data["metadata"].item() if "metadata" in data.files else {}
        final_field = data["final_field"] if "final_field" in data.files else None
        return cls(probes=probes, time=data["time"], dt=float(data["dt"]), metadata=metadata, final_field=final_field)

