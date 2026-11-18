
from waremind.core import Warehouse


def test_robot_waiting_attributes():
    world = Warehouse()
    robot = world.robots[0]

    assert robot.waiting_ticks == 0
    assert robot.stuck is False


def test_robot_waiting_detection():
    world = Warehouse()
    robot = world.robots[0]

    # Create a real order
    order = world.add_order((7, 2))

    # Assign order to Robot 1
    robot.order_id = order.id
    order.assigned_to = robot.id

    # Block all four exits around Robot 1
    assert world.add_obstacle((3, 2))
    assert world.add_obstacle((2, 3))
    assert world.add_obstacle((1, 2))
    assert world.add_obstacle((2, 1))

    # Run simulation
    for _ in range(6):
        world.step()

    assert robot.stuck is True
    assert robot.waiting_ticks >= 5
