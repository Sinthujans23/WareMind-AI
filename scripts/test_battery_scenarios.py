
"""Compare allocation decisions under different battery levels."""

from waremind.mesa_model import WarehouseMesaModel


SCENARIOS = {
    "full_battery": [100, 100, 100],
    "robot_1_low": [30, 100, 100],
    "robot_1_very_low": [20, 100, 100],
    "robot_2_low": [100, 30, 100],
    "robot_3_low": [100, 100, 30],
    "mixed_battery": [45, 75, 95],
}

PICKUP = (7, 2)


def run_scenario(strategy, batteries):
    model = WarehouseMesaModel(strategy=strategy, seed=42)

    for robot, battery in zip(
        model.warehouse.robots,
        batteries,
    ):
        robot.battery = battery

    order = model.add_order(PICKUP)

    model.step()

    return {
        "assigned_robot": order.assigned_to,
        "messages": len(model.bus.history),
    }


def main():
    for name, batteries in SCENARIOS.items():
        print(f"\nScenario: {name}")
        print(f"Battery levels: {batteries}")

        for strategy in (
            "random",
            "nearest",
            "battery_aware",
        ):
            result = run_scenario(strategy, batteries)

            print(
                f"{strategy:15s}"
                f" | Assigned robot: "
                f"{result['assigned_robot']}"
                f" | Messages: {result['messages']}"
            )


if __name__ == "__main__":
    main()
