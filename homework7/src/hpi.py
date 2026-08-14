"""Core calculations for Heritable Prompt Information (HPI)."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def compute_hpi(deltas: Sequence[float], gamma: float) -> float:
    """Return the discounted mean of performance differences across generations.

    ``deltas[t]`` is the expected performance difference between a prompt
    lineage with a revision and its paired control lineage at generation t.
    HPI is dimensionless; it is not measured in bits.
    """
    values = np.asarray(deltas, dtype=float)

    if values.ndim != 1 or values.size == 0:
        raise ValueError("deltas must be a non-empty one-dimensional sequence")
    if not np.all(np.isfinite(values)):
        raise ValueError("deltas must contain only finite values")
    if not 0.0 < gamma <= 1.0:
        raise ValueError("gamma must satisfy 0 < gamma <= 1")

    weights = gamma ** np.arange(values.size)
    return float(np.dot(weights, values) / weights.sum())


def exponential_trajectory(
    initial_gain: float,
    persistence: float,
    generations: int,
) -> np.ndarray:
    """Create a trajectory with a fixed initial gain and exponential decay."""
    if not 0.0 <= persistence <= 1.0:
        raise ValueError("persistence must satisfy 0 <= persistence <= 1")
    if generations < 1:
        raise ValueError("generations must be at least 1")

    return initial_gain * persistence ** np.arange(generations)

