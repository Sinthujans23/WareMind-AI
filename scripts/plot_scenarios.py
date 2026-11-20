
import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "scenario_comparison.csv"
OUTPUT = ROOT / "results" / "graphs"

OUTPUT.mkdir(parents=True, exist_ok=True)

with INPUT.open("r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

if not rows:
    raise ValueError("Scenario comparison CSV is empty.")

labels = [
    f"{row['total_orders']} Orders"
    for row in rows
]

metrics = [
    (
        "scenario_ticks.png",
        "simulation_ticks",
        "Simulation Ticks",
        "Workload vs Simulation Duration",
    ),
    (
        "scenario_messages.png",
        "messages_sent",
        "Messages",
        "Workload vs Communication Overhead",
    ),
    (
        "scenario_completion.png",
        "completion_rate",
        "Completion Rate (%)",
        "Order Completion by Scenario",
    ),
    (
        "scenario_average_completion.png",
        "average_completion_tick",
        "Average Completion Tick",
        "Average Order Completion Tick",
    ),
]

for filename, key, ylabel, title in metrics:
    values = [float(row[key]) for row in rows]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, values)

    ax.set_title(title)
    ax.set_xlabel("Workload")
    ax.set_ylabel(ylabel)

    ax.bar_label(bars, fmt="%.1f", padding=3)
    ax.set_ylim(0, max(values) * 1.2 if max(values) else 1)

    fig.tight_layout()
    fig.savefig(
        OUTPUT / filename,
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(fig)

    print("Saved:", OUTPUT / filename)

print("\nAll scenario comparison graphs generated.")
