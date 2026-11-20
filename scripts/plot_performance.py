
import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "performance_metrics.csv"
OUTPUT = ROOT / "results" / "graphs"

OUTPUT.mkdir(parents=True, exist_ok=True)

with INPUT.open("r", encoding="utf-8", newline="") as file:
    rows = list(csv.DictReader(file))

if not rows:
    raise ValueError("Performance CSV is empty.")

ticks = [int(row["tick"]) for row in rows]
completed = [int(row["completed_orders"]) for row in rows]
battery = [float(row["average_battery"]) for row in rows]
messages = [int(row["messages_sent"]) for row in rows]
completion_rate = [
    float(row["completion_rate"])
    for row in rows
]

graphs = [
    (
        "order_completion.png",
        completed,
        "Completed Orders",
        "Order Completion Progress",
    ),
    (
        "completion_rate.png",
        completion_rate,
        "Completion Rate (%)",
        "Order Completion Rate",
    ),
    (
        "average_battery.png",
        battery,
        "Average Battery (%)",
        "Robot Battery Consumption",
    ),
    (
        "communication_overhead.png",
        messages,
        "Messages Sent",
        "Multi-Agent Communication",
    ),
]

for filename, values, ylabel, title in graphs:
    fig, ax = plt.subplots(figsize=(8, 4.5))

    ax.plot(
        ticks,
        values,
        marker="o",
        markersize=3,
        linewidth=2,
    )

    ax.set_title(title)
    ax.set_xlabel("Simulation Tick")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(
        OUTPUT / filename,
        dpi=180,
        bbox_inches="tight",
    )

    plt.close(fig)

    print("Saved:", OUTPUT / filename)

print("\nAll 4 performance graphs generated.")
