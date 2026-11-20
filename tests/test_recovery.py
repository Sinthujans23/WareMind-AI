
from waremind.core import Warehouse


def test_recovery_moves_idle_blocker():
    world = Warehouse()

    robot = world.robots[0]
    blocker = world.robots[1]

    # Place idle blocker directly in the route.
    blocker.pos = (3, 2)

    order = world.add_order((7, 2))
    robot.order_id = order.id
    order.assigned_to = robot.id
    robot.stuck = True

    reserved = {r.pos for r in world.robots}

    result = world.recover_blocked_robot(robot, reserved)

    assert result is True
    assert blocker.pos != (3, 2)
    assert len({r.pos for r in world.robots}) == len(world.robots)


def test_recovery_does_not_move_busy_robot():
    world = Warehouse()

    robot = world.robots[0]
    blocker = world.robots[1]

    blocker.pos = (3, 2)
    blocker.order_id = 999

    order = world.add_order((7, 2))
    robot.order_id = order.id
    order.assigned_to = robot.id
    robot.stuck = True

    reserved = {r.pos for r in world.robots}

    result = world.recover_blocked_robot(robot, reserved)

    assert result is False
    assert blocker.pos == (3, 2)


def test_recovery_does_not_move_charging_robot():
    world = Warehouse()

    robot = world.robots[0]
    blocker = world.robots[1]

    blocker.pos = (3, 2)
    blocker.charging = True

    order = world.add_order((7, 2))
    robot.order_id = order.id
    order.assigned_to = robot.id
    robot.stuck = True

    reserved = {r.pos for r in world.robots}

    result = world.recover_blocked_robot(robot, reserved)

    assert result is False
    assert blocker.pos == (3, 2)
