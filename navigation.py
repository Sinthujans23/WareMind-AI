
"""A* pathfinding for WareMind AI robots."""

import heapq

from .core import WIDTH, HEIGHT, SHELVES


def heuristic(a, b):
    """Manhattan distance between two grid positions."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar(start, goal, blocked=None):
    """Return a shortest path, including start and goal."""

    blocked = set(blocked or [])

    def accessible(pos):
        x, y = pos
        return (
            0 <= x < WIDTH
            and 0 <= y < HEIGHT
            and pos not in SHELVES
        )

    if not accessible(start) or not accessible(goal):
        return []

    if start in blocked or goal in blocked:
        return []

    if start == goal:
        return [start]

    frontier = [(heuristic(start, goal), 0, start)]
    previous = {start: None}
    best_cost = {start: 0}

    while frontier:
        _, cost, current = heapq.heappop(frontier)

        if cost != best_cost.get(current):
            continue

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = previous[current]
            return list(reversed(path))

        x, y = current

        for nxt in (
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ):
            if not accessible(nxt) or nxt in blocked:
                continue

            new_cost = cost + 1

            if new_cost < best_cost.get(nxt, float("inf")):
                best_cost[nxt] = new_cost
                previous[nxt] = current

                priority = new_cost + heuristic(nxt, goal)
                heapq.heappush(
                    frontier,
                    (priority, new_cost, nxt),
                )

    return []
