
"""Mesa 3.x multi-agent warehouse with message-based negotiation."""

import mesa

from .core import Warehouse
from .messages import Message, MessageType
from .negotiation import MessageBus, choose_winner


class NegotiatedWarehouse(Warehouse):
    """Movement uses the original core; allocation uses messages."""

    def allocate(self):
        # Allocation is performed by the Mesa agents instead.
        pass


class WarehouseRobotAgent(mesa.Agent):
    def __init__(self, model, robot):
        super().__init__(model)
        self.robot = robot

    @property
    def robot_id(self):
        return self.robot.id

    def step(self):
        for msg in self.model.bus.receive(self.robot_id):
            if msg.type == MessageType.CFP:
                order = self.model.get_order(msg.order_id)
                cost = self.robot.bid(order)

                if cost is not None:
                    self.model.bus.send(
                        Message(
                            self.robot_id,
                            0,
                            MessageType.BID,
                            order.id,
                            cost,
                        )
                    )

            elif msg.type == MessageType.AWARD:
                order = self.model.get_order(msg.order_id)

                if (
                    self.robot.order_id is None
                    and order.assigned_to is None
                ):
                    self.robot.order_id = order.id
                    order.assigned_to = self.robot_id

                    self.model.bus.send(
                        Message(
                            self.robot_id,
                            0,
                            MessageType.ACCEPT,
                            order.id,
                        )
                    )


class WarehouseMesaModel(mesa.Model):
    def __init__(self):
        super().__init__()

        self.warehouse = NegotiatedWarehouse()
        self.bus = MessageBus()
        self.bus.register(0)

        self.robot_agents = []

        for robot in self.warehouse.robots:
            self.bus.register(robot.id)
            agent = WarehouseRobotAgent(self, robot)
            self.robot_agents.append(agent)

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "Completed Orders": (
                    lambda m: m.warehouse.completed_count
                ),
                "Active Orders": (
                    lambda m: sum(
                        not order.completed
                        for order in m.warehouse.orders
                    )
                ),
                "Average Battery": (
                    lambda m: sum(
                        r.battery for r in m.warehouse.robots
                    ) / len(m.warehouse.robots)
                ),
                "Messages Sent": (
                    lambda m: len(m.bus.history)
                ),
            }
        )

    def get_order(self, order_id):
        return next(
            order for order in self.warehouse.orders
            if order.id == order_id
        )

    def add_order(self, pickup):
        return self.warehouse.add_order(pickup)

    def negotiate(self):
        for order in self.warehouse.orders:
            if order.completed or order.assigned_to is not None:
                continue

            # Stage 1: Manager broadcasts CFP.
            for agent in self.robot_agents:
                self.bus.send(
                    Message(
                        0,
                        agent.robot_id,
                        MessageType.CFP,
                        order.id,
                    )
                )

            # Stage 2: Robots calculate and submit bids.
            self.agents.do("step")

            incoming = self.bus.receive(0)
            bids = [
                msg for msg in incoming
                if (
                    msg.type == MessageType.BID
                    and msg.order_id == order.id
                )
            ]

            winner = choose_winner(bids)

            if winner is None:
                continue

            # Stage 3: Manager awards the task.
            for bid in bids:
                message_type = (
                    MessageType.AWARD
                    if bid.sender == winner.sender
                    else MessageType.REJECT
                )

                self.bus.send(
                    Message(
                        0,
                        bid.sender,
                        message_type,
                        order.id,
                    )
                )

            # Stage 4: Winner accepts.
            self.agents.do("step")

            responses = self.bus.receive(0)
            accepted = any(
                msg.type == MessageType.ACCEPT
                and msg.sender == winner.sender
                and msg.order_id == order.id
                for msg in responses
            )

            if accepted:
                self.warehouse.events.append(
                    f"Order {order.id}: "
                    f"Robot {winner.sender} won negotiation"
                )

    def step(self):
        self.negotiate()
        self.warehouse.step()
        self.datacollector.collect(self)
