
"""Experta-based robot safety decision rules."""

from .experta_compat import Fact, KnowledgeEngine, Rule


class RobotSafetyEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.actions = []

    @Rule(Fact(idle=True, low_battery=True))
    def start_charging(self):
        self.actions.append("START_CHARGING")

    @Rule(Fact(busy=True))
    def reject_busy_robot(self):
        self.actions.append("REJECT_NEW_TASK")

    @Rule(Fact(charging=True))
    def reject_charging_robot(self):
        self.actions.append("REJECT_NEW_TASK")

    @Rule(Fact(insufficient_battery=True))
    def reject_insufficient_battery(self):
        self.actions.append("REJECT_NEW_TASK")


def evaluate_robot_safety(
    *,
    idle,
    battery,
    charging,
    required_battery=0,
):
    """Return safety actions for a robot's current state."""

    engine = RobotSafetyEngine()
    engine.reset()

    engine.declare(
        Fact(
            idle=idle,
            busy=not idle,
            low_battery=battery < 25,
            charging=charging,
            insufficient_battery=battery < required_battery,
        )
    )

    engine.run()
    return set(engine.actions)
