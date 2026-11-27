"""Generate reusable before-versus-after performance graphs."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS = Path("results")
GRAPHS = RESULTS / "graphs"


def read_csv(name):
    with (RESULTS / name).open("r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def grouped_bar(categories, baseline, optimized, title, ylabel, filename, fmt=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    x = range(len(categories))
    width = 0.38
    ax.bar([i - width / 2 for i in x], baseline, width, label="Baseline")
    ax.bar([i + width / 2 for i in x], optimized, width, label="Optimized")
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(list(x), categories, rotation=30, ha="right")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(GRAPHS / filename, dpi=180)
    plt.close(fig)


def main():
    GRAPHS.mkdir(parents=True, exist_ok=True)
    summary = read_csv("optimization_summary.csv")
    baseline_summary = summary[0] if summary[0]["version"] == "baseline" else summary[1]
    optimized_summary = summary[1] if summary[1]["version"] == "optimized" else summary[0]

    grouped_bar(
        ["Full-run success"],
        [float(baseline_summary["success_rate"]) * 100],
        [float(optimized_summary["success_rate"]) * 100],
        "Full-Run Success Rate",
        "Experiments completing every order (%)",
        "optimization_success_rate.png",
    )

    paired = read_csv("optimization_paired_comparison.csv")

    for dimension in ("scenario", "strategy"):
        by = read_csv(f"optimization_by_{dimension}.csv")
        categories = sorted({row[dimension] for row in by})
        before_completion = []
        after_completion = []
        before_ticks = []
        after_ticks = []
        before_energy = []
        after_energy = []
        for category in categories:
            subset = [row for row in by if row[dimension] == category]
            before = next(row for row in subset if row["version"] == "baseline")
            after = next(row for row in subset if row["version"] == "optimized")
            before_completion.append(float(before["order_completion_rate"]) * 100)
            after_completion.append(float(after["order_completion_rate"]) * 100)
            before_ticks.append(float(before["mean_ticks"]))
            after_ticks.append(float(after["mean_ticks"]))
            before_energy.append(float(before["estimated_energy"]))
            after_energy.append(float(after["estimated_energy"]))

        grouped_bar(
            categories,
            before_completion,
            after_completion,
            f"Order Completion Rate by {dimension.title()}",
            "Orders completed (%)",
            f"optimization_completion_by_{dimension}.png",
        )
        grouped_bar(
            categories,
            before_ticks,
            after_ticks,
            f"Mean Simulation Ticks by {dimension.title()}",
            "Ticks",
            f"optimization_ticks_by_{dimension}.png",
        )
        grouped_bar(
            categories,
            before_energy,
            after_energy,
            f"Estimated Energy by {dimension.title()}",
            "Estimated energy",
            f"optimization_energy_by_{dimension}.png",
        )

    successful_before = [int(r["baseline_ticks"]) for r in paired if r["baseline_all_completed"] == "True"]
    successful_after = [int(r["optimized_ticks"]) for r in paired if r["optimized_all_completed"] == "True"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(successful_before, bins=20, alpha=0.65, label="Baseline")
    ax.hist(successful_after, bins=20, alpha=0.65, label="Optimized")
    ax.set_title("Successful-Run Completion Time Distribution")
    ax.set_xlabel("Simulation ticks")
    ax.set_ylabel("Number of experiments")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(GRAPHS / "successful_run_ticks.png", dpi=180)
    plt.close(fig)

    print(f"Graphs saved: {GRAPHS}")


if __name__ == "__main__":
    main()
