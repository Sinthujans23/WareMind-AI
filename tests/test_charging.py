
from waremind.core import Warehouse, CHARGER, FULL_BATTERY


def test_low_battery_robot_starts_charging():
    world = Warehouse()
    robot = world.robots[0]

    robot.battery = 15.0
    world.step()

    assert robot.charging is True
    assert robot.order_id is None


def test_charging_robot_does_not_bid():
    world = Warehouse()
    robot = world.robots[0]

    robot.battery = 15.0
    robot.charging = True

    order = world.add_order((3, 2))

    assert robot.bid(order) is None


def test_robot_reaches_charger():
    world = Warehouse()
    robot = world.robots[0]

    robot.battery = 20.0

    for _ in range(100):
        world.step()
        if robot.pos == CHARGER:
            break

    assert robot.pos == CHARGER


def test_robot_recharges():
    world = Warehouse()
    robot = world.robots[0]

    robot.pos = CHARGER
    robot.battery = 20.0

    for _ in range(20):
        world.step()

    assert robot.battery == FULL_BATTERY
    assert robot.charging is False
