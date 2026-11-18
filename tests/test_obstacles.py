
from waremind.core import Warehouse, SHELVES, DEPOT, CHARGER
from waremind.navigation import astar


def test_add_dynamic_obstacle():
    world = Warehouse()

    assert world.add_obstacle((3, 2)) is True
    assert (3, 2) in world.dynamic_obstacles


def test_obstacle_cannot_overlap_robot():
    world = Warehouse()

    assert world.add_obstacle((2, 2)) is False


def test_obstacle_cannot_block_special_cells():
    world = Warehouse()

    assert world.add_obstacle(DEPOT) is False
    assert world.add_obstacle(CHARGER) is False
    assert world.add_obstacle(next(iter(SHELVES))) is False


def test_astar_avoids_dynamic_obstacle():
    world = Warehouse()
    world.add_obstacle((3, 2))

    route = astar(
        (2, 2),
        (7, 2),
        world.dynamic_obstacles
    )

    assert route
    assert (3, 2) not in route


def test_remove_dynamic_obstacle():
    world = Warehouse()

    world.add_obstacle((3, 2))

    assert world.remove_obstacle((3, 2)) is True
    assert (3, 2) not in world.dynamic_obstacles


def test_robot_avoids_obstacle_during_delivery():
    world = Warehouse()

    world.add_obstacle((3, 2))
    order = world.add_order((7, 2))

    for _ in range(100):
        world.step()
        assert all(
            robot.pos not in world.dynamic_obstacles
            for robot in world.robots
        )

        if order.completed:
            break

    assert order.completed
