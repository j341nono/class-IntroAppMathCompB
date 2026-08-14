#!/usr/bin/env python3
"""Run the illustrative experiments for Heritable Prompt Information."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from hpi import compute_hpi, exponential_trajectory


ROOT_DIR = Path(__file__).resolve().parents[1]
FIGURES_DIR = ROOT_DIR / "figures"
RESULTS_DIR = ROOT_DIR / "results"
DEFAULT_GAMMA = 0.9

# Each value is Delta_t: the expected score difference between a lineage that
# receives the revision and a paired control lineage at the same generation.
REVISION_DELTAS = {
    "Specific Patch": np.array([0.20, 0.05, 0.00, -0.02, -0.03]),
    "General Rule": np.array([0.10, 0.09, 0.08, 0.08, 0.07]),
    "Harmful Rule": np.array([-0.02, -0.03, -0.04, -0.05, -0.05]),
}

PERSISTENCE_FACTORS = {
    "Fast decay": 0.25,
    "Medium decay": 0.60,
    "Slow decay": 0.90,
}

GAMMA_VALUES = np.array([0.5, 0.7, 0.9, 1.0])

COLORS = {
    "Specific Patch": "#2878B5",
    "General Rule": "#2A9D68",
    "Harmful Rule": "#D1495B",
    "Fast decay": "#D1495B",
    "Medium decay": "#E9A23B",
    "Slow decay": "#2A9D68",
}


def configure_plot_style() -> None:
    """Apply a small, consistent style to all assignment figures."""
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#333333",
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linewidth": 0.8,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 11,
            "axes.titleweight": "bold",
            "legend.frameon": False,
        }
    )


def save_figure(fig: plt.Figure, filename: str) -> None:
    """Save a figure in the repository's figures directory."""
    output_path = FIGURES_DIR / filename
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def experiment_1() -> list[dict[str, object]]:
    """Compare immediate gain with HPI for three prompt revisions."""
    rows: list[dict[str, object]] = []
    for revision, deltas in REVISION_DELTAS.items():
        rows.append(
            {
                "experiment": "Immediate Gain vs HPI",
                "series": revision,
                "gamma": DEFAULT_GAMMA,
                "immediate_gain": float(deltas[0]),
                "hpi": compute_hpi(deltas, DEFAULT_GAMMA),
                "deltas": ";".join(f"{value:.3f}" for value in deltas),
            }
        )

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    for revision, deltas in REVISION_DELTAS.items():
        ax.plot(
            np.arange(deltas.size),
            deltas,
            marker="o",
            linewidth=2.4,
            markersize=6,
            color=COLORS[revision],
            label=revision,
        )
    ax.axhline(0.0, color="#555555", linewidth=1.0)
    ax.set(
        title="Revision effects across prompt generations",
        xlabel="Generation",
        ylabel=r"Performance Difference $\Delta_t$",
        xticks=np.arange(5),
    )
    ax.legend()
    save_figure(fig, "generation_effect.png")

    labels = list(REVISION_DELTAS)
    immediate = [float(REVISION_DELTAS[label][0]) for label in labels]
    hpi_values = [compute_hpi(REVISION_DELTAS[label], DEFAULT_GAMMA) for label in labels]
    x_positions = np.arange(len(labels))
    width = 0.34

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    immediate_bars = ax.bar(
        x_positions - width / 2,
        immediate,
        width,
        color="#8DB7D5",
        label="Immediate Gain",
    )
    hpi_bars = ax.bar(
        x_positions + width / 2,
        hpi_values,
        width,
        color="#F0A45D",
        label=f"HPI ($\\gamma={DEFAULT_GAMMA}$)",
    )
    ax.axhline(0.0, color="#555555", linewidth=1.0)
    ax.set(
        title="Immediate improvement and inherited value are different",
        ylabel="Dimensionless score",
        xticks=x_positions,
        xticklabels=labels,
    )
    ax.legend()
    ax.bar_label(immediate_bars, fmt="%.3f", padding=3, fontsize=9)
    ax.bar_label(hpi_bars, fmt="%.3f", padding=3, fontsize=9)
    save_figure(fig, "immediate_vs_hpi.png")

    return rows


def experiment_2() -> list[dict[str, object]]:
    """Show that equal initial gains can have different HPI values."""
    rows: list[dict[str, object]] = []
    trajectories: dict[str, np.ndarray] = {}

    for label, persistence in PERSISTENCE_FACTORS.items():
        deltas = exponential_trajectory(0.1, persistence, generations=9)
        trajectories[label] = deltas
        rows.append(
            {
                "experiment": "Persistence",
                "series": label,
                "gamma": DEFAULT_GAMMA,
                "immediate_gain": float(deltas[0]),
                "hpi": compute_hpi(deltas, DEFAULT_GAMMA),
                "deltas": ";".join(f"{value:.5f}" for value in deltas),
            }
        )

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    for label, deltas in trajectories.items():
        hpi_value = compute_hpi(deltas, DEFAULT_GAMMA)
        ax.plot(
            np.arange(deltas.size),
            deltas,
            marker="o",
            linewidth=2.4,
            markersize=5,
            color=COLORS[label],
            label=f"{label} (HPI={hpi_value:.3f})",
        )
    ax.set(
        title="Equal initial gains, different persistence",
        xlabel="Generation",
        ylabel=r"Performance Difference $\Delta_t$",
        xticks=np.arange(9),
    )
    ax.set_ylim(bottom=-0.004)
    ax.legend()
    save_figure(fig, "persistence_effect.png")

    return rows


def experiment_3() -> list[dict[str, object]]:
    """Measure HPI sensitivity to the future-generation discount factor."""
    rows: list[dict[str, object]] = []

    fig, ax = plt.subplots(figsize=(9.5, 5.6))
    for revision, deltas in REVISION_DELTAS.items():
        hpi_values = [compute_hpi(deltas, gamma) for gamma in GAMMA_VALUES]
        ax.plot(
            GAMMA_VALUES,
            hpi_values,
            marker="o",
            linewidth=2.4,
            markersize=6,
            color=COLORS[revision],
            label=revision,
        )
        for gamma, hpi_value in zip(GAMMA_VALUES, hpi_values, strict=True):
            rows.append(
                {
                    "experiment": "Gamma Sensitivity",
                    "series": revision,
                    "gamma": float(gamma),
                    "immediate_gain": float(deltas[0]),
                    "hpi": hpi_value,
                    "deltas": ";".join(f"{value:.3f}" for value in deltas),
                }
            )

    ax.axhline(0.0, color="#555555", linewidth=1.0)
    ax.set(
        title="HPI sensitivity to the discount factor",
        xlabel=r"Discount factor $\gamma$",
        ylabel="HPI (dimensionless)",
        xticks=GAMMA_VALUES,
    )
    ax.legend()
    save_figure(fig, "gamma_sensitivity.png")

    return rows


def write_results(rows: list[dict[str, object]]) -> Path:
    """Write all numerical summaries to one reproducible CSV file."""
    output_path = RESULTS_DIR / "results.csv"
    fieldnames = ["experiment", "series", "gamma", "immediate_gain", "hpi", "deltas"]
    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            formatted_row = dict(row)
            formatted_row["gamma"] = f"{float(row['gamma']):.2f}"
            formatted_row["immediate_gain"] = f"{float(row['immediate_gain']):.6f}"
            formatted_row["hpi"] = f"{float(row['hpi']):.6f}"
            writer.writerow(formatted_row)
    return output_path


def print_summary(rows: list[dict[str, object]], results_path: Path) -> None:
    """Print the central comparison and generated output locations."""
    experiment_1_rows = [
        row for row in rows if row["experiment"] == "Immediate Gain vs HPI"
    ]
    print("Heritable Prompt Information")
    print("=" * 58)
    print(f"{'Revision':<22}{'Immediate Gain':>16}{'HPI':>12}")
    print("-" * 58)
    for row in experiment_1_rows:
        print(
            f"{str(row['series']):<22}"
            f"{float(row['immediate_gain']):>16.3f}"
            f"{float(row['hpi']):>12.3f}"
        )
    print()
    print(f"Figures saved to {FIGURES_DIR.relative_to(ROOT_DIR)}/")
    print(f"Results saved to {results_path.relative_to(ROOT_DIR)}")


def main() -> None:
    """Run every experiment and save its figures and numerical results."""
    np.random.seed(0)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    configure_plot_style()

    rows = experiment_1() + experiment_2() + experiment_3()
    results_path = write_results(rows)
    print_summary(rows, results_path)


if __name__ == "__main__":
    main()
