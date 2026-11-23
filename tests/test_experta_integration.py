
from waremind.mesa_model import WarehouseMesaModel


def test_low_battery_robot_starts_charging():
    model = WarehouseMesaModel()

    robot = model.warehouse.robots[0]
    robot.battery = 20

    model.add_order((7, 2))
    model.step()

    assert robot.charging is True
    assert robot.order_id is None


def test_healthy_robot_can_receive_order():
    model = WarehouseMesaModel()

    model.add_order((7, 2))
    model.step()

    assert any(
        robot.order_id is not None
        for robot in model.warehouse.robots
    )


def test_low_battery_robot_not_awarded_task():
    model = WarehouseMesaModel()

    robot = model.warehouse.robots[0]
    robot.battery = 20

    order = model.add_order((7, 2))
    model.step()

    assert order.assigned_to != robot.id
