
from waremind.core import (
    Warehouse,
    Robot,
    DEPOT,
    BATTERY_PER_MOVE,
)

from waremind.mesa_model import WarehouseMesaModel
from scripts.advanced_experiments import setup_scenario


def create_deadlock():
    world = Warehouse()

    r1, r2, r3 = world.robots

    r1.pos = (1, 4)
    r2.pos = DEPOT

    order1 = world.add_order((7, 2))
    order2 = world.add_order((1, 4))

    r1.order_id = order1.id
    r1.carrying = True
    order1.assigned_to = r1.id

    r2.order_id = order2.id
    r2.carrying = False
    order2.assigned_to = r2.id

    r1.waiting_ticks = 5
    r2.waiting_ticks = 5

    r1.stuck = True
    r2.stuck = True

    return world, r1, r2


def test_robot_at_depot_cannot_bid():
    world = Warehouse()

    robot = Robot(99, DEPOT)
    order = world.add_order((7, 2))

    assert robot.bid(order) is None


def test_circular_deadlock_is_resolved():
    world, r1, r2 = create_deadlock()

    reserved = {r.pos for r in world.robots}

    result = world.resolve_deadlock(reserved)

    assert result is True
    assert r2.pos != DEPOT
    assert world.recovery_count == 1


def test_deadlock_preserves_task_assignment():
    world, r1, r2 = create_deadlock()

    original_order = r2.order_id
    original_battery = r2.battery

    reserved = {r.pos for r in world.robots}

    assert world.resolve_deadlock(reserved)

    assert r2.order_id == original_order
    assert r2.carrying is False
    assert r1.carrying is True

    order = next(
        o for o in world.orders
        if o.id == original_order
    )

    assert order.assigned_to == r2.id

    assert r2.battery == (
        original_battery - BATTERY_PER_MOVE
    )


def test_deadlock_recovery_avoids_overlap():
    world, r1, r2 = create_deadlock()

    reserved = {r.pos for r in world.robots}

    assert world.resolve_deadlock(reserved)

    positions = {r.pos for r in world.robots}

    assert len(positions) == len(world.robots)
    assert reserved == positions


def test_no_recovery_without_deadlock():
    world = Warehouse()

    reserved = {r.pos for r in world.robots}

    assert world.resolve_deadlock(reserved) is False
    assert world.recovery_count == 0


def test_deadlock_recovery_avoids_obstacles():
    world, r1, r2 = create_deadlock()

    world.add_obstacle((2, 1))

    reserved = {r.pos for r in world.robots}

    assert world.resolve_deadlock(reserved)

    assert r2.pos not in world.dynamic_obstacles


def test_high_workload_regression():
    model = WarehouseMesaModel(
        strategy="battery_aware",
        seed=4,
    )

    total = setup_scenario(
        model,
        "high_workload",
        4,
    )

    for _ in range(500):
        if model.warehouse.completed_count == total:
            break

        model.step()

        positions = [
            r.pos for r in model.warehouse.robots
        ]

        assert len(positions) == len(set(positions))

    assert model.warehouse.completed_count == total


def test_combined_stress_regression():
    model = WarehouseMesaModel(
        strategy="battery_aware",
        seed=4,
    )

    total = setup_scenario(
        model,
        "combined_stress",
        4,
    )

    for _ in range(500):
        if model.warehouse.completed_count == total:
            break

        model.step()

        positions = [
            r.pos for r in model.warehouse.robots
        ]

        assert len(positions) == len(set(positions))

    assert model.warehouse.completed_count == total
