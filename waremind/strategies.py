
"""Task allocation strategies for WareMind AI."""

import random

from .navigation import astar


def choose_robot(robots, order, strategy="battery_aware", seed=42,
                 blocked=None):
    """
    Select a robot using one of three strategies.

    random:
        Random eligible robot.

    nearest:
        Robot with shortest A* distance to pickup.

    battery_aware:
        Robot with lowest battery-aware bid.
    """

    if strategy not in {"random", "nearest", "battery_aware"}:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Reuse existing bid() for eligibility and reachable routes.
    eligible = []

    for robot in robots:
        cost = robot.bid(order, blocked)

        if cost is not None:
            eligible.append(robot)

    if not eligible:
        return None

    if strategy == "random":
        rng = random.Random(seed)
        return rng.choice(eligible)

    if strategy == "nearest":
        return min(
            eligible,
            key=lambda robot: (
                len(astar(robot.pos, order.pickup, blocked)) - 1,
                robot.id,
            ),
        )

    return min(
        eligible,
        key=lambda robot: (
            robot.bid(order, blocked),
            robot.id,
        ),
    )
