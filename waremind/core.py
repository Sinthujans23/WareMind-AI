"""Deterministic, testable warehouse multi-agent simulation core.

Agents negotiate tasks using a simplified Contract Net Protocol (CFP -> bids -> award).
This is an educational prototype, not a production warehouse controller.
"""
from dataclasses import dataclass, field
from collections import deque
from typing import Optional

WIDTH, HEIGHT = 16, 12
SHELVES = {(x, y) for x in (4, 5, 10, 11) for y in (3, 4, 5, 7, 8)}
DEPOT = (1, 1)
CHARGER = (14, 10)


def neighbors(pos):
    x, y = pos
    for nxt in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
        if 0 <= nxt[0] < WIDTH and 0 <= nxt[1] < HEIGHT and nxt not in SHELVES:
            yield nxt


def pathfind(start, goal, blocked=frozenset()):
    """Shortest unweighted grid path using BFS; includes start, returns [] if unreachable."""
    if start == goal:
        return [start]
    queue = deque([start]); previous = {start: None}
    while queue:
        current = queue.popleft()
        for nxt in neighbors(current):
            if nxt in previous or (nxt in blocked and nxt != goal):
                continue
            previous[nxt] = current
            if nxt == goal:
                path = [goal]
                while previous[path[-1]] is not None:
                    path.append(previous[path[-1]])
                return list(reversed(path))
            queue.append(nxt)
    return []


@dataclass
class Order:
    id: int
    pickup: tuple[int, int]
    destination: tuple[int, int] = DEPOT
    assigned_to: Optional[int] = None
    completed: bool = False


@dataclass
class Robot:
    id: int
    pos: tuple[int, int]
    battery: float = 100.0
    order_id: Optional[int] = None
    carrying: bool = False
    delivered: int = 0
    messages: list[str] = field(default_factory=list)

    def bid(self, order):
        if self.order_id is not None or self.battery < 20:
            return None
        from .navigation import astar

        p1 = astar(self.pos, order.pickup)
        p2 = astar(order.pickup, order.destination)
        if not p1 or not p2:
            return None
        travel = len(p1) + len(p2) - 2
        if self.battery < travel + 15:
            return None
        return travel + (100 - self.battery) * 0.12


class Warehouse:
    def __init__(self):
        self.robots = [Robot(1, (2, 2)), Robot(2, (13, 2)), Robot(3, (8, 10))]
        self.orders = []
        self.tick = 0
        self.events = []
        self._next_order_id = 1

    def add_order(self, pickup):
        if pickup in SHELVES or not (0 <= pickup[0] < WIDTH and 0 <= pickup[1] < HEIGHT):
            raise ValueError('Pickup must be an accessible grid cell')
        order = Order(self._next_order_id, pickup)
        self._next_order_id += 1
        self.orders.append(order)
        self.events.append(f'Order {order.id} created at {pickup}')
        return order

    def allocate(self):
        for order in self.orders:
            if order.assigned_to is not None or order.completed:
                continue
            bids = [(bid, robot.id, robot) for robot in self.robots if (bid := robot.bid(order)) is not None]
            if not bids:
                continue
            _, _, winner = min(bids)
            winner.order_id = order.id
            order.assigned_to = winner.id
            self.events.append(f'CFP order {order.id}: robot {winner.id} won task auction')

    def step(self):
        self.tick += 1
        self.allocate()
        reserved = {robot.pos for robot in self.robots}
        for robot in self.robots:
            if robot.order_id is None:
                continue
            order = next(o for o in self.orders if o.id == robot.order_id)
            goal = order.destination if robot.carrying else order.pickup
            if robot.pos == goal:
                if robot.carrying:
                    order.completed = True
                    robot.delivered += 1
                    robot.order_id = None
                    robot.carrying = False
                    self.events.append(f'Order {order.id} delivered by robot {robot.id}')
                else:
                    robot.carrying = True
                    self.events.append(f'Robot {robot.id} picked up order {order.id}')
                continue
            from .navigation import astar

            route = astar(robot.pos, goal, reserved - {robot.pos})
            if len(route) > 1 and route[1] not in reserved:
                reserved.remove(robot.pos)
                robot.pos = route[1]
                reserved.add(robot.pos)
                robot.battery = max(0.0, robot.battery - 0.5)
        self.events = self.events[-12:]

    @property
    def completed_count(self):
        return sum(o.completed for o in self.orders)
