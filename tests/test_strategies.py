
from waremind.core import Warehouse
from waremind.strategies import choose_robot


def test_random_strategy_returns_eligible_robot():
    world = Warehouse()
    order = world.add_order((7, 2))

    winner = choose_robot(
        world.robots,
        order,
        strategy="random",
        seed=42,
    )

    assert winner in world.robots


def test_nearest_strategy():
    world = Warehouse()
    order = world.add_order((3, 2))

    winner = choose_robot(
        world.robots,
        order,
        strategy="nearest",
    )

    assert winner.id == 1


def test_battery_aware_strategy():
    world = Warehouse()
    order = world.add_order((7, 2))

    winner = choose_robot(
        world.robots,
        order,
        strategy="battery_aware",
    )

    eligible = [
        robot for robot in world.robots
        if robot.bid(order) is not None
    ]

    expected = min(
        eligible,
        key=lambda robot: (
            robot.bid(order),
            robot.id,
        ),
    )

    assert winner.id == expected.id


def test_busy_robot_is_not_selected():
    world = Warehouse()
    order = world.add_order((7, 2))

    world.robots[0].order_id = 999

    for strategy in ("random", "nearest", "battery_aware"):
        winner = choose_robot(
            world.robots,
            order,
            strategy=strategy,
        )

        assert winner is None or winner.id != 1


def test_unknown_strategy():
    world = Warehouse()
    order = world.add_order((7, 2))

    try:
        choose_robot(
            world.robots,
            order,
            strategy="invalid",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")
