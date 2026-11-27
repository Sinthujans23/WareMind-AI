
"""Diagnose incomplete WareMind simulation runs."""

import argparse

from waremind.mesa_model import WarehouseMesaModel
from waremind.navigation import astar
from waremind.core import CHARGER, DEPOT

from scripts.advanced_experiments import (
    setup_scenario,
    MAX_TICKS,
)


def diagnose(strategy, scenario, seed):

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

    for _ in range(MAX_TICKS):

        if warehouse.completed_count == total_orders:
            break

        model.step()

    print("\n" + "=" * 65)
    print("WAREMIND FAILURE DIAGNOSIS")
    print("=" * 65)

    print(f"Scenario: {scenario}")
    print(f"Strategy: {strategy}")
    print(f"Seed: {seed}")
    print(f"Ticks: {warehouse.tick}")

    print(
        f"Completed: "
        f"{warehouse.completed_count}/{total_orders}"
    )

    print("\n--- ROBOT STATES ---")

    for robot in warehouse.robots:

        print(f"\nRobot {robot.id}")
        print(f"Position: {robot.pos}")
        print(f"Battery: {robot.battery}")
        print(f"Order ID: {robot.order_id}")
        print(f"Charging: {robot.charging}")
        print(f"Carrying: {robot.carrying}")
        print(f"Waiting ticks: {robot.waiting_ticks}")
        print(f"Stuck: {robot.stuck}")
        print(f"Delivered: {robot.delivered}")

        if robot.order_id is not None:

            order = model.get_order(robot.order_id)

            goal = (
                order.destination
                if robot.carrying
                else order.pickup
            )

            other_robots = {
                r.pos
                for r in warehouse.robots
                if r.id != robot.id
            }

            ideal_route = astar(
                robot.pos,
                goal,
                warehouse.dynamic_obstacles,
            )

            actual_route = astar(
                robot.pos,
                goal,
                warehouse.dynamic_obstacles
                | other_robots,
            )

            print(f"Current goal: {goal}")
            print(f"Ideal route: {ideal_route}")
            print(f"Actual route: {actual_route}")

    print("\n--- INCOMPLETE ORDERS ---")

    for order in warehouse.orders:

        if order.completed:
            continue

        print(f"\nOrder {order.id}")
        print(f"Pickup: {order.pickup}")
        print(f"Destination: {order.destination}")
        print(f"Assigned to: {order.assigned_to}")

        if order.assigned_to is None:

            print("Available robot bids:")

            for robot in warehouse.robots:

                cost = robot.bid(
                    order,
                    warehouse.dynamic_obstacles,
                )

                print(
                    f"Robot {robot.id}: "
                    f"Bid={cost}, "
                    f"Battery={robot.battery}"
                )

    print("\n--- WAREHOUSE INFORMATION ---")
    print(f"Depot: {DEPOT}")
    print(f"Charger: {CHARGER}")
    print(f"Obstacles: {warehouse.dynamic_obstacles}")
    print(f"Recoveries: {warehouse.recovery_count}")

    print("\n--- RECENT EVENTS ---")

    for event in warehouse.events:
        print(event)

    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Diagnose a WareMind simulation run.",
    )
    parser.add_argument("--scenario", choices=(
        "normal",
        "low_battery",
        "mixed_battery",
        "high_workload",
        "obstacles",
        "combined_stress",
    ))
    parser.add_argument("--strategy", choices=("random", "nearest", "battery_aware"), default="battery_aware")
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    if args.scenario is not None and args.seed is not None:
        diagnose(args.strategy, args.scenario, args.seed)
    else:
        diagnose("battery_aware", "high_workload", 4)
        diagnose("battery_aware", "combined_stress", 4)
