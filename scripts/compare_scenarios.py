
import csv
from pathlib import Path

from waremind.mesa_model import WarehouseMesaModel


SCENARIOS = {
    "3_orders": [
        (7, 2), (13, 8), (2, 9)
    ],
    "5_orders": [
        (7, 2), (13, 8), (2, 9),
        (12, 2), (6, 9)
    ],
    "10_orders": [
        (7, 2), (13, 8), (2, 9),
        (12, 2), (6, 9), (14, 6),
        (3, 9), (11, 9), (2, 6),
        (14, 9)
    ],
}


def run_scenario(name, pickups, max_ticks=500):
    model = WarehouseMesaModel()
    world = model.warehouse

    for pickup in pickups:
        world.add_order(pickup)

    total = len(world.orders)
    completion_ticks = {}

    for tick in range(1, max_ticks + 1):
        model.step()

        for order in world.orders:
            if order.completed and order.id not in completion_ticks:
                completion_ticks[order.id] = tick

        if world.completed_count == total:
            break

    completed = world.completed_count

    average_delivery_tick = (
        sum(completion_ticks.values())
        / len(completion_ticks)
        if completion_ticks else 0.0
    )

    return {
        "scenario": name,
        "total_orders": total,
        "completed_orders": completed,
        "completion_rate": round(
            completed / total * 100, 2
        ) if total else 0.0,
        "simulation_ticks": world.tick,
        "average_completion_tick": round(
            average_delivery_tick, 2
        ),
        "messages_sent": len(model.bus.history),
        "recoveries": world.recovery_count,
        "stuck_robots": sum(
            robot.stuck for robot in world.robots
        ),
    }


def main():
    results = []

    for name, pickups in SCENARIOS.items():
        result = run_scenario(name, pickups)
        results.append(result)

        print(
            f"{name}: "
            f"{result['completed_orders']}/"
            f"{result['total_orders']} completed | "
            f"{result['simulation_ticks']} ticks | "
            f"{result['messages_sent']} messages"
        )

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "scenario_comparison.csv"

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("\nSaved:", output_file)


if __name__ == "__main__":
    main()
