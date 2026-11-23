
"""Compare WareMind task allocation strategies across seeds."""

import csv
from pathlib import Path
from statistics import mean, stdev

from waremind.mesa_model import WarehouseMesaModel


STRATEGIES = ("random", "nearest", "battery_aware")
SEEDS = range(10)
PICKUPS = [(7, 2), (13, 8), (2, 9)]
MAX_TICKS = 150

OUTPUT = Path("results/strategy_comparison.csv")


def run_experiment(strategy, seed):
    model = WarehouseMesaModel(
        strategy=strategy,
        seed=seed,
    )

    for pickup in PICKUPS:
        model.add_order(pickup)

    for _ in range(MAX_TICKS):
        if model.warehouse.completed_count == len(PICKUPS):
            break
        model.step()

    completed = model.warehouse.completed_count

    return {
        "strategy": strategy,
        "seed": seed,
        "completed": completed,
        "total_orders": len(PICKUPS),
        "completion_rate": completed / len(PICKUPS),
        "ticks": model.warehouse.tick,
        "messages": len(model.bus.history),
        "recoveries": model.warehouse.recovery_count,
    }


def main():
    results = []

    for seed in SEEDS:
        for strategy in STRATEGIES:
            result = run_experiment(strategy, seed)
            results.append(result)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"Saved: {OUTPUT}")
    print()

    for strategy in STRATEGIES:
        subset = [
            row for row in results
            if row["strategy"] == strategy
        ]

        ticks = [row["ticks"] for row in subset]

        print(
            f"{strategy:15s}"
            f" | Mean ticks: {mean(ticks):6.2f}"
            f" | Std: {stdev(ticks):6.2f}"
            f" | Mean completion: "
            f"{mean(row['completion_rate'] for row in subset):.1%}"
            f" | Mean messages: "
            f"{mean(row['messages'] for row in subset):.1f}"
        )


if __name__ == "__main__":
    main()
