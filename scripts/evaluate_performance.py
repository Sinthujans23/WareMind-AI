
import csv
from pathlib import Path

from waremind.mesa_model import WarehouseMesaModel


def evaluate(max_ticks=120):
    model = WarehouseMesaModel()
    world = model.warehouse

    for pickup in [(7, 2), (13, 8), (2, 9)]:
        world.add_order(pickup)

    results = []
    previous_completed = 0

    for tick in range(1, max_ticks + 1):
        model.step()

        completed = world.completed_count
        total = len(world.orders)

        average_battery = (
            sum(r.battery for r in world.robots)
            / len(world.robots)
        )

        results.append({
            "tick": tick,
            "completed_orders": completed,
            "pending_orders": total - completed,
            "completion_rate": round(
                completed / total * 100, 2
            ),
            "average_battery": round(
                average_battery, 2
            ),
            "messages_sent": len(model.bus.history),
            "stuck_robots": sum(
                r.stuck for r in world.robots
            ),
            "recoveries": world.recovery_count,
        })

        if completed > previous_completed:
            print(
                f"Tick {tick}: "
                f"{completed}/{total} orders completed"
            )

        previous_completed = completed

        if completed == total:
            break

    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)

    output_file = output_dir / "performance_metrics.csv"

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("\n=== PERFORMANCE EVALUATION ===")
    print("Total Orders:", len(world.orders))
    print("Completed Orders:", world.completed_count)
    print("Simulation Ticks:", world.tick)
    print(
        "Completion Rate:",
        f"{results[-1]['completion_rate']}%"
    )
    print("Messages Sent:", len(model.bus.history))
    print("Recoveries:", world.recovery_count)
    print("Saved:", output_file)


if __name__ == "__main__":
    evaluate()
