
"""Mesa 3.x integration for WareMind AI.

The existing Warehouse remains the source of truth.
Mesa agents wrap its robots without duplicating movement logic.
"""

import mesa
from .core import Warehouse


class WarehouseRobotAgent(mesa.Agent):
    def __init__(self, model, robot):
        super().__init__(model)
        self.robot = robot

    @property
    def robot_id(self):
        return self.robot.id

    def step(self):
        # Core warehouse handles coordinated movement.
        # Agent observes its robot's current state.
        return {
            "robot_id": self.robot.id,
            "position": self.robot.pos,
            "battery": self.robot.battery,
            "order_id": self.robot.order_id,
        }


class WarehouseMesaModel(mesa.Model):
    def __init__(self):
        super().__init__()
        self.warehouse = Warehouse()

        self.robot_agents = [
            WarehouseRobotAgent(self, robot)
            for robot in self.warehouse.robots
        ]

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Completed Orders": lambda m: m.warehouse.completed_count,
                "Active Orders": lambda m: sum(
                    1
                    for order in m.warehouse.orders
                    if not order.completed
                ),
                "Average Battery": lambda m: sum(
                    robot.battery
                    for robot in m.warehouse.robots
                ) / len(m.warehouse.robots),
            }
        )

    def add_order(self, pickup):
        return self.warehouse.add_order(pickup)

    def step(self):
        self.warehouse.step()
        self.agents.do("step")
        self.datacollector.collect(self)
