
"""Generate strategy comparison graphs."""

import csv
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt


INPUT = Path("results/strategy_comparison.csv")
OUTPUT = Path("results/graphs")
OUTPUT.mkdir(parents=True, exist_ok=True)

strategies = ("random", "nearest", "battery_aware")
labels = ("Random", "Nearest-First", "Battery-Aware")

with INPUT.open(newline="", encoding="utf-8") as file:
    rows = list(csv.DictReader(file))

groups = {
    strategy: [
        row for row in rows
        if row["strategy"] == strategy
    ]
    for strategy in strategies
}


def save_bar_chart(values, ylabel, title, filename, errors=None):
    fig, ax = plt.subplots(figsize=(8, 5))

    ax.bar(
        labels,
        values,
        yerr=errors,
        capsize=5 if errors is not None else 0,
    )

    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(OUTPUT / filename, dpi=180)
    plt.close(fig)

    print(f"Saved: {OUTPUT / filename}")


ticks = [
    [float(row["ticks"]) for row in groups[s]]
    for s in strategies
]

save_bar_chart(
    [mean(values) for values in ticks],
    "Simulation ticks",
    "Mean Completion Time by Strategy",
    "strategy_mean_ticks.png",
    errors=[stdev(values) for values in ticks],
)

save_bar_chart(
    [
        mean(float(row["completion_rate"]) * 100
             for row in groups[s])
        for s in strategies
    ],
    "Completion rate (%)",
    "Order Completion Rate by Strategy",
    "strategy_completion_rate.png",
)

save_bar_chart(
    [
        mean(float(row["messages"]) for row in groups[s])
        for s in strategies
    ],
    "Messages sent",
    "Communication Overhead by Strategy",
    "strategy_messages.png",
)

print("All strategy graphs generated successfully.")
