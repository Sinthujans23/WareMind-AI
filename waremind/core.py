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
LOW_BATTERY = 25.0
FULL_BATTERY = 100.0
BATTERY_PER_MOVE = 0.5
CHARGE_PER_TICK = 10.0

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
    charging: bool = False
    waiting_ticks: int = 0
    stuck: bool = False

    def bid(self, order, blocked=None):
        from .navigation import astar
        from .safety_rules import evaluate_robot_safety

        # Step 1: Check robot safety using Experta
        actions = evaluate_robot_safety(
            idle=self.order_id is None,
            battery=self.battery,
            charging=self.charging,
        )

        if (
            "START_CHARGING" in actions
            or "REJECT_NEW_TASK" in actions
        ):
            return None

        # Step 2: Calculate travel distance using A*
        p1 = astar(self.pos, order.pickup, blocked)
        p2 = astar(
            order.pickup,
            order.destination,
            blocked,
        )

        if not p1 or not p2:
            return None

        travel = len(p1) + len(p2) - 2

        # Step 3: Check required battery using Experta
        actions = evaluate_robot_safety(
            idle=self.order_id is None,
            battery=self.battery,
            charging=self.charging,
            required_battery=travel + 15,
        )

        if "REJECT_NEW_TASK" in actions:
            return None

        # Step 4: Calculate battery-aware bid score
        return travel + (100 - self.battery) * 0.12

class Warehouse:
    def __init__(self):
        self.robots = [Robot(1, (2, 2)), Robot(2, (13, 2)), Robot(3, (8, 10))]
        self.orders = []
        self.dynamic_obstacles = set()
        self.tick = 0
        self.events = []
        self._next_order_id = 1
        self.recovery_count = 0
    
    def add_obstacle(self, pos):
        """Add a temporary obstacle to an accessible, empty cell."""
        x, y = pos

        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return False

        if pos in SHELVES or pos in (DEPOT, CHARGER):
            return False

        if any(robot.pos == pos for robot in self.robots):
            return False

        if any(
            order.pickup == pos and not order.completed
            for order in self.orders
        ):
            return False

        self.dynamic_obstacles.add(pos)
        self.events.append(f"Obstacle added at {pos}")
        return True

    def remove_obstacle(self, pos):
        """Remove an existing temporary obstacle."""
        if pos not in self.dynamic_obstacles:
            return False

        self.dynamic_obstacles.remove(pos)
        self.events.append(f"Obstacle removed at {pos}")
        return True

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
            bids = [(bid, robot.id, robot) for robot in self.robots if (bid := robot.bid(order, self.dynamic_obstacles)) is not None]
            if not bids:
                continue
            _, _, winner = min(bids)
            winner.order_id = order.id
            order.assigned_to = winner.id
            self.events.append(f'CFP order {order.id}: robot {winner.id} won task auction')
    
    def manage_charging(self, robot, reserved):
        """Handle charging for an idle robot."""

        from .navigation import astar

        if robot.order_id is not None:
            return False

        if robot.battery < LOW_BATTERY:
            robot.charging = True

        if not robot.charging:
            return False

        if robot.pos == CHARGER:
            robot.battery = min(
                FULL_BATTERY,
                robot.battery + CHARGE_PER_TICK
            )

            if robot.battery >= FULL_BATTERY:
                robot.charging = False
                self.events.append(
                    f"Robot {robot.id} fully charged"
                )
            return True

        route = astar(
            robot.pos,
            CHARGER,
            reserved - {robot.pos}
        )

        if len(route) > 1 and route[1] not in reserved:
            reserved.remove(robot.pos)
            robot.pos = route[1]
            reserved.add(robot.pos)

            robot.battery = max(
                0.0,
                robot.battery - BATTERY_PER_MOVE
            )

        return True

    
    def recover_blocked_robot(self, robot, reserved):
        """Move one idle blocking robot aside when a task robot is stuck."""
        from .navigation import astar

        if robot.order_id is None or not robot.stuck:
            return False

        order = next(
            (o for o in self.orders if o.id == robot.order_id),
            None
        )

        if order is None:
            return False

        goal = order.destination if robot.carrying else order.pickup

        # Find a route ignoring other robots, but not obstacles.
        ideal_route = astar(
            robot.pos,
            goal,
            self.dynamic_obstacles
        )

        if len(ideal_route) < 2:
            return False

        next_cell = ideal_route[1]

        blocker = next(
            (
                other for other in self.robots
                if other.id != robot.id and other.pos == next_cell
            ),
            None
        )

        # Only move idle robots that are not charging.
        if blocker is None or blocker.order_id is not None or blocker.charging:
            return False

        for candidate in neighbors(blocker.pos):
            if candidate in reserved:
                continue

            if candidate in self.dynamic_obstacles:
                continue

            if candidate == robot.pos:
                continue

            if candidate in (DEPOT, CHARGER):
                continue

            # Move blocker to an empty adjacent cell.
            reserved.remove(blocker.pos)
            blocker.pos = candidate
            reserved.add(candidate)

            blocker.battery = max(
                0.0,
                blocker.battery - BATTERY_PER_MOVE
            )
            self.recovery_count += 1
            self.events.append(
                f"Robot {blocker.id} yielded to Robot {robot.id}"
            )

            return True

        return False
    
    def clear_depot(self, reserved):
        """Move an idle robot away from the depot to allow deliveries."""
        from .navigation import astar

        depot_robot = next(
            (
                robot
                for robot in self.robots
                if robot.pos == DEPOT
                and robot.order_id is None
                and not robot.charging
            ),
            None
        )

        if depot_robot is None:
            return False

        # Search for a safe parking cell.
        candidates = []

        for x in range(WIDTH):
            for y in range(HEIGHT):
                pos = (x, y)

                if pos in SHELVES:
                    continue

                if pos in self.dynamic_obstacles:
                    continue

                if pos in reserved:
                    continue

                if pos in (DEPOT, CHARGER):
                    continue

                if any(
                    not order.completed and order.pickup == pos
                    for order in self.orders
                ):
                    continue

                candidates.append(pos)

        # Prefer nearby parking locations.
        candidates.sort(
            key=lambda pos: (
                abs(pos[0] - DEPOT[0])
                + abs(pos[1] - DEPOT[1])
            )
        )

        for target in candidates:
            route = astar(
                depot_robot.pos,
                target,
                (reserved - {depot_robot.pos})
                | self.dynamic_obstacles
            )

            if len(route) < 2:
                continue

            next_cell = route[1]

            if next_cell in reserved:
                continue

            reserved.remove(depot_robot.pos)
            depot_robot.pos = next_cell
            reserved.add(next_cell)

            depot_robot.battery = max(
                0.0,
                depot_robot.battery - BATTERY_PER_MOVE
            )

            self.events.append(
                f"Robot {depot_robot.id} cleared depot"
            )

            return True

        return False

    
    def step(self):
        self.tick += 1

        reserved = {robot.pos for robot in self.robots}
        self.clear_depot(reserved)

        # Mark low-battery idle robots for charging.
        for robot in self.robots:
            if robot.order_id is None and robot.battery < LOW_BATTERY:
                robot.charging = True

        # Allocate available orders.
        self.allocate()

        for robot in self.robots:

            # Charging logic for idle robots.
            if self.manage_charging(robot, reserved):
                continue

            if robot.order_id is None:
                continue

            order = next(
                (o for o in self.orders if o.id == robot.order_id),
                None
            )

            if order is None:
                self.events.append(
                    f"Robot {robot.id}: invalid order"
                )
                robot.order_id = None
                robot.carrying = False
                robot.waiting_ticks = 0
                robot.stuck = False
                continue

            goal = (
                order.destination
                if robot.carrying
                else order.pickup
            )

            # Robot has reached pickup or delivery destination.
            if robot.pos == goal:

                if robot.carrying:
                    order.completed = True
                    robot.delivered += 1
                    robot.order_id = None
                    robot.carrying = False

                    self.events.append(
                        f"Order {order.id} delivered by robot {robot.id}"
                    )

                else:
                    robot.carrying = True

                    self.events.append(
                        f"Robot {robot.id} picked up order {order.id}"
                    )

                robot.waiting_ticks = 0
                robot.stuck = False
                continue

            # A* pathfinding with dynamic obstacle avoidance.
            from .navigation import astar

            route = astar(
                robot.pos,
                goal,
                (reserved - {robot.pos}) | self.dynamic_obstacles
            )

            if len(route) > 1 and route[1] not in reserved:

                reserved.remove(robot.pos)
                robot.pos = route[1]
                reserved.add(robot.pos)

                robot.battery = max(
                    0.0,
                    robot.battery - BATTERY_PER_MOVE
                )

                robot.waiting_ticks = 0
                robot.stuck = False

            else:
                # Robot cannot move this tick.
                robot.waiting_ticks += 1

                if robot.waiting_ticks >= 5:

                    if not robot.stuck:
                        robot.stuck = True

                        self.events.append(
                            f"Robot {robot.id} blocked for 5 ticks"
                        )

                    # Attempt safe idle-robot repositioning.
                    self.recover_blocked_robot(robot, reserved)

        # Keep only recent events.
        self.events = self.events[-12:]



    @property
    def completed_count(self):
        return sum(o.completed for o in self.orders)
