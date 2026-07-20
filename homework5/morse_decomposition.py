#!/usr/bin/env python3
"""1 次元力学系 dx/dt = x - x^3 の Morse 分解を可視化する。

この例は講義ノートの Example 2.1 / Example 3.1 と同じ系である。

    dx/dt = F(x) = x - x^3 = -V'(x),   V(x) = -x^2/2 + x^4/4

平衡点は x = -1, 0, 1 の 3 点で、F'(x) = 1 - 3x^2 より
    F'(-1) = F'(1) = -2 < 0  → 安定
    F'(0)  = 1        > 0    → 不安定
となる。大域アトラクターは A = [-1, 1] であり、その内部組織は Morse 分解

    M0 = {0} (不安定, saddle 相当),  M_minus = {-1} (安定),  M_plus = {1} (安定)

で記述される。接続軌道は
    M0 --> M_minus,   M0 --> M_plus
の 2 本であり、不安定な現在状態 {0} が 2 つの可能な未来を持つことを表す
(講義ノート Figure 8)。V は Morse 集合上で一定・軌道に沿って単調非増加の
Lyapunov 関数であり、Morse グラフの矢印の向き(高い V から低い V へ)を与える。
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


# ----------------------------------------------------------------------
# 力学系の定義
# ----------------------------------------------------------------------
def F(x: np.ndarray | float) -> np.ndarray | float:
    """ベクトル場 dx/dt = x - x^3。"""
    return x - x**3


def V(x: np.ndarray | float) -> np.ndarray | float:
    """Lyapunov 関数(ポテンシャル)。 F(x) = -V'(x) を満たす。"""
    return -0.5 * x**2 + 0.25 * x**4


# Morse 集合(平衡点)とその情報。V の値が矢印の向きを決める。
MORSE_SETS = {
    "M0 = {0}\n(unstable)":       {"x": 0.0,  "stable": False},
    "M_ = {-1}\n(stable)":        {"x": -1.0, "stable": True},
    "M+ = {1}\n(stable)":         {"x": 1.0,  "stable": True},
}

# 接続軌道 (Morse グラフの有向辺): 不安定点 0 から 2 つの安定点へ
CONNECTIONS = [("M0 = {0}\n(unstable)", "M_ = {-1}\n(stable)"),
               ("M0 = {0}\n(unstable)", "M+ = {1}\n(stable)")]


# ----------------------------------------------------------------------
# 描画
# ----------------------------------------------------------------------
def make_plot(output_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, (ax_phase, ax_graph) = plt.subplots(
        1, 2, figsize=(13, 6), constrained_layout=True
    )

    # --- 左: 位相線図(phase line)とベクトル場 ---
    xs = np.linspace(-1.6, 1.6, 400)
    ax_phase.axhline(0.0, color="#444444", linewidth=1.0, zorder=1)
    ax_phase.plot(xs, F(xs), color="#1f77b4", linewidth=2.2,
                  label=r"$F(x)=x-x^3$", zorder=2)

    # 大域アトラクター A = [-1, 1] を網掛け
    ax_phase.axvspan(-1.0, 1.0, color="#8ecae6", alpha=0.25,
                     label=r"global attractor $\mathcal{A}=[-1,1]$")

    # 平衡点と安定性 (塗りつぶし=安定, 白抜き=不安定)
    for info in MORSE_SETS.values():
        x0 = info["x"]
        if info["stable"]:
            ax_phase.plot(x0, 0.0, "o", markersize=13, color="#2a9d8f",
                          markeredgecolor="black", zorder=5)
            ax_phase.annotate("stable", (x0, 0.0), textcoords="offset points",
                              xytext=(0, -26), ha="center", fontsize=10)
        else:
            ax_phase.plot(x0, 0.0, "o", markersize=13, color="white",
                          markeredgecolor="black", zorder=5)
            ax_phase.annotate("unstable", (x0, 0.0), textcoords="offset points",
                              xytext=(0, 14), ha="center", fontsize=10)

    # 相線上の流れの向き (F>0 で右向き, F<0 で左向き)
    for xa in [-1.35, -0.5, 0.5, 1.35]:
        direction = np.sign(F(xa))
        ax_phase.annotate(
            "", xy=(xa + 0.14 * direction, 0.0), xytext=(xa, 0.0),
            arrowprops=dict(arrowstyle="-|>", color="#e76f51", lw=2.2), zorder=4,
        )

    ax_phase.set_title("Phase line of  dx/dt = x - x$^3$", fontsize=13)
    ax_phase.set_xlabel("x")
    ax_phase.set_ylabel(r"$\dot{x}=F(x)$")
    ax_phase.set_xlim(-1.6, 1.6)
    ax_phase.set_ylim(-1.1, 1.1)
    ax_phase.legend(loc="upper center", fontsize=9)
    ax_phase.grid(alpha=0.2)

    # --- 右: Morse グラフ (不変集合の有向グラフ) ---
    # 縦位置 = Lyapunov 関数 V の値 (下ほど V が小さい = より安定)
    positions = {
        "M0 = {0}\n(unstable)": (0.0,  V(0.0)),   # V = 0    (上, saddle)
        "M_ = {-1}\n(stable)":  (-1.0, V(-1.0)),  # V = -1/4 (下, sink)
        "M+ = {1}\n(stable)":   (1.0,  V(1.0)),   # V = -1/4 (下, sink)
    }
    colors = {
        "M0 = {0}\n(unstable)": "#f4a3a3",
        "M_ = {-1}\n(stable)":  "#a8d5a2",
        "M+ = {1}\n(stable)":   "#a8d5a2",
    }

    # 接続軌道(辺)を先に描く
    for src, dst in CONNECTIONS:
        x0, y0 = positions[src]
        x1, y1 = positions[dst]
        ax_graph.annotate(
            "", xy=(x1, y1 + 0.05), xytext=(x0, y0 - 0.05),
            arrowprops=dict(arrowstyle="-|>", color="#333333", lw=2.2,
                            shrinkA=22, shrinkB=22),
        )

    # ノード(Morse 集合)を描く
    for name, (x, y) in positions.items():
        ax_graph.scatter([x], [y], s=4200, c=colors[name],
                         edgecolors="black", zorder=3)
        ax_graph.text(x, y, name, ha="center", va="center",
                      fontsize=9.5, zorder=4)

    # Lyapunov レベルの補助線
    for level, label in [(V(0.0), "higher V (saddle)"),
                         (V(1.0), "lower V (sinks)")]:
        ax_graph.axhline(level, color="#4f9fd6", ls="--", alpha=0.6, lw=1.2)
        ax_graph.text(1.72, level, label, va="center", fontsize=9,
                      color="#2a6f97")

    ax_graph.set_title("Morse graph:  M0 → M-,  M0 → M+", fontsize=13)
    ax_graph.set_xlabel("state x")
    ax_graph.set_ylabel("Lyapunov function  V(x)  (decreases downward)")
    ax_graph.set_xlim(-1.9, 2.7)
    ax_graph.set_ylim(V(1.0) - 0.15, V(0.0) + 0.15)
    ax_graph.grid(alpha=0.2)

    fig.suptitle(
        "Morse decomposition of a 1D dynamical system  (attractor as a directed graph of invariant sets)",
        fontsize=14, fontweight="bold",
    )
    fig.savefig(output_path, dpi=180)
    print(f"Saved plot to {output_path}")
    try:
        plt.show()
    except Exception:
        pass


def main() -> None:
    output_path = Path(__file__).with_name("morse_decomposition.png")
    make_plot(output_path)
    print("Equilibria: x = -1, 0, 1")
    print(f"  V(-1) = {V(-1.0):.3f}, V(0) = {V(0.0):.3f}, V(1) = {V(1.0):.3f}")
    print("Morse sets: M0={0} (unstable), M-={-1} (stable), M+={1} (stable)")
    print("Connections: M0 -> M-,  M0 -> M+")


if __name__ == "__main__":
    main()
