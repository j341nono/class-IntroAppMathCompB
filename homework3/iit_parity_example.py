#!/usr/bin/env python3
"""Visualize a small Integrated Information Theory toy example.

This example is intentionally different from the lecture-note examples:
three binary units form a parity relation in the next state.  Every single
unit still looks like a fair coin, but the whole system rules out half of the
possible future states.
"""

from __future__ import annotations

from itertools import product
from math import log2
from pathlib import Path


STATES = list(product([0, 1], repeat=3))
STATE_LABELS = ["".join(map(str, state)) for state in STATES]


def kl_divergence_bits(p: list[float], q: list[float]) -> float:
    """Return D_KL(p || q) in bits, safely ignoring zero-probability p terms."""
    return sum(p_i * log2(p_i / q_i) for p_i, q_i in zip(p, q) if p_i > 0)


def parity_locked_effect_repertoire() -> list[float]:
    """Distribution where the future state must satisfy C = A xor B."""
    p = [0.0 for _ in STATES]
    allowed = []
    for index, (a_next, b_next, c_next) in enumerate(STATES):
        if c_next == (a_next ^ b_next):
            allowed.append(index)
    for index in allowed:
        p[index] = 1.0 / len(allowed)
    return p


def marginal_distribution(p: list[float], unit_indices: tuple[int, ...]) -> dict[tuple[int, ...], float]:
    """Marginalize a distribution over the selected unit indices."""
    marginal: dict[tuple[int, ...], float] = {}
    for state, probability in zip(STATES, p):
        key = tuple(state[i] for i in unit_indices)
        marginal[key] = marginal.get(key, 0.0) + float(probability)
    return marginal


def partitioned_repertoire(
    p: list[float], partition: tuple[tuple[int, ...], ...]
) -> list[float]:
    """Build the product distribution obtained after cutting a partition."""
    marginals = [marginal_distribution(p, part) for part in partition]
    q = [1.0 for _ in STATES]
    for state_index, state in enumerate(STATES):
        for part, marginal in zip(partition, marginals):
            key = tuple(state[i] for i in part)
            q[state_index] *= marginal[key]
    return q


def analyze_example() -> tuple[list[float], list[float], dict[str, float], float]:
    whole = parity_locked_effect_repertoire()
    uniform = [1.0 / len(STATES) for _ in STATES]

    partitions = {
        "A | BC": ((0,), (1, 2)),
        "B | AC": ((1,), (0, 2)),
        "C | AB": ((2,), (0, 1)),
        "A | B | C": ((0,), (1,), (2,)),
    }
    partitioned = {name: partitioned_repertoire(whole, part) for name, part in partitions.items()}
    phi_values = {
        name: kl_divergence_bits(whole, q)
        for name, q in partitioned.items()
    }
    phi_mip = min(phi_values.values())
    return whole, uniform, phi_values, phi_mip


def make_matplotlib_plot(output_path: Path) -> None:
    import matplotlib.pyplot as plt

    whole, uniform, phi_values, phi_mip = analyze_example()

    x = list(range(len(STATES)))
    width = 0.36

    fig, (ax_dist, ax_phi) = plt.subplots(
        2,
        1,
        figsize=(10, 8),
        gridspec_kw={"height_ratios": [2.2, 1.0]},
        constrained_layout=True,
    )

    ax_dist.bar(
        [value - width / 2 for value in x],
        whole,
        width,
        label="Whole repertoire: C = A xor B",
        color="#2f6f73",
    )
    ax_dist.bar(
        [value + width / 2 for value in x],
        uniform,
        width,
        label="After a cut: independent-looking repertoire",
        color="#d88c4a",
        alpha=0.82,
    )
    ax_dist.set_title("IIT toy example: a hidden parity constraint")
    ax_dist.set_ylabel("Probability")
    ax_dist.set_xticks(x)
    ax_dist.set_xticklabels(STATE_LABELS)
    ax_dist.set_ylim(0, 0.32)
    ax_dist.legend(loc="upper right")
    ax_dist.grid(axis="y", alpha=0.25)

    names = list(phi_values.keys())
    values = [phi_values[name] for name in names]
    colors = ["#4f7cac", "#6f9f5f", "#b35c44", "#7a5ea8"]
    ax_phi.bar(names, values, color=colors)
    ax_phi.axhline(phi_mip, color="#333333", linewidth=1.2, linestyle="--")
    ax_phi.text(
        0.02,
        phi_mip + 0.04,
        f"minimum information partition: phi = {phi_mip:.2f} bit",
        transform=ax_phi.get_yaxis_transform(),
        ha="left",
        va="bottom",
        fontsize=10,
    )
    ax_phi.set_ylabel("D_KL(whole || cut) [bits]")
    ax_phi.set_ylim(0, max(values) + 0.35)
    ax_phi.grid(axis="y", alpha=0.25)

    fig.suptitle(
        "A whole can specify a relation that none of its parts specify alone",
        fontsize=14,
        fontweight="bold",
    )
    fig.savefig(output_path, dpi=180)
    plt.show()


def make_pillow_plot(output_path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    whole, uniform, phi_values, phi_mip = analyze_example()

    width, height = 1600, 1200
    margin = 110
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = ImageFont.truetype("Arial.ttf", 38) if Path("/System/Library/Fonts/Supplemental/Arial.ttf").exists() else ImageFont.load_default()
    font = ImageFont.truetype("Arial.ttf", 24) if Path("/System/Library/Fonts/Supplemental/Arial.ttf").exists() else ImageFont.load_default()

    draw.text((margin, 38), "IIT toy example: a hidden parity constraint", fill=(20, 20, 20), font=title_font)
    draw.text((margin, 95), "A whole can specify C = A xor B even when the parts look independent.", fill=(50, 50, 50), font=font)

    chart_left, chart_top = margin, 175
    chart_width, chart_height = width - 2 * margin, 470
    draw.rectangle((chart_left, chart_top, chart_left + chart_width, chart_top + chart_height), outline=(210, 210, 210), width=2)
    max_prob = 0.32
    group_width = chart_width / len(STATES)
    bar_width = group_width * 0.28
    for i, label in enumerate(STATE_LABELS):
        base_x = chart_left + i * group_width + group_width / 2
        for offset, value, color in [
            (-bar_width * 0.65, whole[i], (47, 111, 115)),
            (bar_width * 0.65, uniform[i], (216, 140, 74)),
        ]:
            bar_h = chart_height * value / max_prob
            x0 = base_x + offset - bar_width / 2
            y0 = chart_top + chart_height - bar_h
            x1 = base_x + offset + bar_width / 2
            y1 = chart_top + chart_height
            draw.rectangle((x0, y0, x1, y1), fill=color)
        draw.text((base_x - 18, chart_top + chart_height + 16), label, fill=(30, 30, 30), font=font)
    draw.text((chart_left, chart_top - 34), "Effect repertoire probabilities", fill=(30, 30, 30), font=font)
    draw.rectangle((chart_left + chart_width - 520, chart_top + 20, chart_left + chart_width - 490, chart_top + 50), fill=(47, 111, 115))
    draw.text((chart_left + chart_width - 480, chart_top + 20), "Whole repertoire", fill=(30, 30, 30), font=font)
    draw.rectangle((chart_left + chart_width - 520, chart_top + 60, chart_left + chart_width - 490, chart_top + 90), fill=(216, 140, 74))
    draw.text((chart_left + chart_width - 480, chart_top + 60), "Partitioned repertoire", fill=(30, 30, 30), font=font)

    phi_left, phi_top = margin, 780
    phi_width, phi_height = width - 2 * margin, 250
    draw.rectangle((phi_left, phi_top, phi_left + phi_width, phi_top + phi_height), outline=(210, 210, 210), width=2)
    names = list(phi_values.keys())
    values = [phi_values[name] for name in names]
    max_phi = max(values) + 0.35
    colors = [(79, 124, 172), (111, 159, 95), (179, 92, 68), (122, 94, 168)]
    group_width = phi_width / len(names)
    bar_width = group_width * 0.42
    for i, (name, value) in enumerate(zip(names, values)):
        base_x = phi_left + i * group_width + group_width / 2
        bar_h = phi_height * value / max_phi
        draw.rectangle(
            (
                base_x - bar_width / 2,
                phi_top + phi_height - bar_h,
                base_x + bar_width / 2,
                phi_top + phi_height,
            ),
            fill=colors[i],
        )
        draw.text((base_x - 48, phi_top + phi_height + 16), name, fill=(30, 30, 30), font=font)
    y_phi = phi_top + phi_height - phi_height * phi_mip / max_phi
    draw.line((phi_left, y_phi, phi_left + phi_width, y_phi), fill=(45, 45, 45), width=3)
    draw.text((phi_left, phi_top - 38), f"Partition loss: minimum phi = {phi_mip:.2f} bit", fill=(30, 30, 30), font=font)

    img.save(output_path)


def make_plot(output_path: Path) -> None:
    try:
        make_matplotlib_plot(output_path)
    except ModuleNotFoundError as error:
        if error.name != "matplotlib":
            raise
        print("matplotlib is not installed; using the Pillow fallback renderer.")
        make_pillow_plot(output_path)

    _, _, _, phi_mip = analyze_example()
    print(f"Saved plot to {output_path}")
    print(f"Integrated information for this simplified example: phi = {phi_mip:.2f} bit")


def main() -> None:
    output_path = Path(__file__).with_name("iit_parity_example.png")
    make_plot(output_path)


if __name__ == "__main__":
    main()
