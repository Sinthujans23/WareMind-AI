from waremind.core import Warehouse, pathfind, SHELVES


def test_path_avoids_shelves():
    path = pathfind((2, 2), (7, 2))
    assert path and all(p not in SHELVES for p in path)


def test_negotiation_assigns_order():
    w = Warehouse()
    order = w.add_order((7, 2))
    w.allocate()
    assert order.assigned_to is not None
    assert sum(r.order_id == order.id for r in w.robots) == 1


def test_single_order_delivery():
    w = Warehouse()
    w.add_order((7, 2))
    for _ in range(120):
        w.step()
        if w.completed_count:
            break
    assert w.completed_count == 1


def test_no_robot_overlap():
    w = Warehouse()
    for pickup in [(7, 2), (13, 8), (2, 9)]:
        w.add_order(pickup)
    for _ in range(150):
        w.step()
        positions = [r.pos for r in w.robots]
        assert len(positions) == len(set(positions))
