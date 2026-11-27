
"""Advanced performance evaluation for WareMind AI."""

import csv
import argparse
import random
from pathlib import Path
from statistics import mean, stdev

from waremind.mesa_model import WarehouseMesaModel
from waremind.core import (
    WIDTH,
    HEIGHT,
    SHELVES,
    DEPOT,
    CHARGER,
    BATTERY_PER_MOVE,
)


STRATEGIES = ("random", "nearest", "battery_aware")
SEEDS = range(10)
MAX_TICKS = 500

DEFAULT_OUTPUT = Path("results/advanced_comparison.csv")

NORMAL_PICKUPS = [(7, 2), (13, 8), (2, 9)]

SCENARIOS = {
    "normal": {
        "batteries": [100, 100, 100],
        "orders": 3,
        "obstacles": 0,
    },
    "low_battery": {
        "batteries": [20, 100, 100],
        "orders": 3,
        "obstacles": 0,
    },
    "mixed_battery": {
        "batteries": [30, 65, 100],
        "orders": 3,
        "obstacles": 0,
    },
    "high_workload": {
        "batteries": [100, 100, 100],
        "orders": 15,
        "obstacles": 0,
    },
    "obstacles": {
        "batteries": [100, 100, 100],
        "orders": 6,
        "obstacles": 8,
    },
    "combined_stress": {
        "batteries": [20, 65, 100],
        "orders": 15,
        "obstacles": 8,
    },
}


def setup_scenario(model, scenario, seed):
    """Create reproducible initial conditions."""

    config = SCENARIOS[scenario]
    rng = random.Random(seed)
    warehouse = model.warehouse

    for robot, battery in zip(
        warehouse.robots,
        config["batteries"],
    ):
        robot.battery = float(battery)

    excluded = set(SHELVES)
    excluded.update([DEPOT, CHARGER])
    excluded.update(r.pos for r in warehouse.robots)

    available = [
        (x, y)
        for x in range(WIDTH)
        for y in range(HEIGHT)
        if (x, y) not in excluded
    ]

    if config["orders"] == 3:
        pickups = NORMAL_PICKUPS.copy()
    else:
        pickups = rng.sample(
            available,
            config["orders"],
        )

    for pickup in pickups:
        model.add_order(pickup)

    obstacle_candidates = [
        pos for pos in available
        if pos not in pickups
    ]

    obstacles = rng.sample(
        obstacle_candidates,
        config["obstacles"],
    )

    for obstacle in obstacles:
        warehouse.add_obstacle(obstacle)

    return len(pickups)


def run_experiment(strategy, scenario, seed):
    """Run one simulation and collect metrics."""

    model = WarehouseMesaModel(
        strategy=strategy,
        seed=seed,
    )

    total_orders = setup_scenario(
        model,
        scenario,
        seed,
    )

    warehouse = model.warehouse

    total_distance = 0
    energy_consumed = 0.0
    charging_sessions = 0
    overlap_ticks = 0

    completion_times = {}

    initial_battery = sum(
        r.battery for r in warehouse.robots
    )

    for _ in range(MAX_TICKS):

        if warehouse.completed_count == total_orders:
            break

        old_positions = {
            r.id: r.pos
            for r in warehouse.robots
        }

        old_charging = {
            r.id: r.charging
            for r in warehouse.robots
        }

        model.step()

        for robot in warehouse.robots:

            old_x, old_y = old_positions[robot.id]
            new_x, new_y = robot.pos

            distance = (
                abs(new_x - old_x)
                + abs(new_y - old_y)
            )

            total_distance += distance

            energy_consumed += (
                distance * BATTERY_PER_MOVE
            )

            if (
                robot.charging
                and not old_charging[robot.id]
            ):
                charging_sessions += 1

        positions = [
            robot.pos
            for robot in warehouse.robots
        ]

        if len(positions) != len(set(positions)):
            overlap_ticks += 1

        for order in warehouse.orders:
            if (
                order.completed
                and order.id not in completion_times
            ):
                completion_times[order.id] = (
                    warehouse.tick
                )

    completed = warehouse.completed_count

    workloads = [
        robot.delivered
        for robot in warehouse.robots
    ]

    final_battery = sum(
        r.battery for r in warehouse.robots
    )

    return {
        "scenario": scenario,
        "strategy": strategy,
        "seed": seed,
        "completed": completed,
        "total_orders": total_orders,
        "completion_rate": completed / total_orders,
        "ticks": warehouse.tick,
        "messages": len(model.bus.history),
        "recoveries": warehouse.recovery_count,
        "observed_distance": total_distance,
        "estimated_energy_consumed": round(
            energy_consumed, 2
        ),
        "charging_sessions": charging_sessions,
        "overlap_ticks": overlap_ticks,
        "mean_order_completion_ticks": (
            round(mean(completion_times.values()), 2)
            if completion_times else ""
        ),
        "initial_total_battery": initial_battery,
        "final_total_battery": round(
            final_battery, 2
        ),
        "robot_1_deliveries": workloads[0],
        "robot_2_deliveries": workloads[1],
        "robot_3_deliveries": workloads[2],
        "workload_std": round(
            stdev(workloads), 2
        ),
        "all_completed": completed == total_orders,
    }


def main():

    parser = argparse.ArgumentParser(
        description="Run WareMind advanced performance experiments.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="CSV output path (default: results/advanced_comparison.csv)",
    )
    args = parser.parse_args()
    output = args.output

    results = []

    total_runs = (
        len(SCENARIOS)
        * len(STRATEGIES)
        * len(SEEDS)
    )

    print("=" * 70)
    print("WAREMIND AI - ADVANCED PERFORMANCE EVALUATION")
    print("=" * 70)
    print(f"Total experiments: {total_runs}")

    run_number = 0

    for scenario in SCENARIOS:
        for seed in SEEDS:
            for strategy in STRATEGIES:

                result = run_experiment(
                    strategy,
                    scenario,
                    seed,
                )

                results.append(result)
                run_number += 1

                print(
                    f"[{run_number}/{total_runs}] "
                    f"{scenario:18s} "
                    f"{strategy:15s} "
                    f"Seed: {seed} | "
                    f"Completed: "
                    f"{result['completed']}/"
                    f"{result['total_orders']} | "
                    f"Ticks: {result['ticks']}"
                )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
        )

        writer.writeheader()
        writer.writerows(results)

    print("\n" + "=" * 70)
    print("EXPERIMENT SUMMARY")
    print("=" * 70)

    for scenario in SCENARIOS:

        print(f"\nScenario: {scenario}")

        for strategy in STRATEGIES:

            subset = [
                row for row in results
                if row["scenario"] == scenario
                and row["strategy"] == strategy
            ]

            print(
                f"{strategy:15s}"
                f" | Completion: "
                f"{mean(r['completion_rate'] for r in subset):.1%}"
                f" | Ticks: "
                f"{mean(r['ticks'] for r in subset):.2f}"
                f" | Distance: "
                f"{mean(r['observed_distance'] for r in subset):.2f}"
                f" | Energy: "
                f"{mean(r['estimated_energy_consumed'] for r in subset):.2f}"
                f" | Overlap ticks: "
                f"{sum(r['overlap_ticks'] for r in subset)}"
            )

    print(f"\nResults saved: {output}")
    print(f"Total completed runs: {len(results)}")


if __name__ == "__main__":
    main()
