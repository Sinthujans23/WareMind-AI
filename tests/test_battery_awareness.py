
"""Regression tests for battery-aware task allocation."""

from waremind.mesa_model import WarehouseMesaModel


def assigned_robot(strategy, batteries):
    model = WarehouseMesaModel(
        strategy=strategy,
        seed=42,
    )

    for robot, battery in zip(
        model.warehouse.robots,
        batteries,
    ):
        robot.battery = battery

    order = model.add_order((7, 2))
    model.step()

    return order.assigned_to


def test_battery_aware_changes_winner_when_robot_1_low():
    batteries = [30, 100, 100]

    assert assigned_robot("nearest", batteries) == 1
    assert assigned_robot("battery_aware", batteries) == 2


def test_battery_aware_changes_winner_with_mixed_battery():
    batteries = [45, 75, 95]

    assert assigned_robot("nearest", batteries) == 1
    assert assigned_robot("battery_aware", batteries) == 2


def test_full_battery_same_winner():
    batteries = [100, 100, 100]

    assert assigned_robot("nearest", batteries) == 1
    assert assigned_robot("battery_aware", batteries) == 1
