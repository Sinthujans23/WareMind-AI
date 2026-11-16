
"""Simple Contract Net communication helpers."""

from .messages import Message, MessageType


class MessageBus:
    def __init__(self):
        self.inboxes = {}
        self.history = []

    def register(self, agent_id):
        if agent_id in self.inboxes:
            raise ValueError("Agent already registered")
        self.inboxes[agent_id] = []

    def send(self, message: Message):
        if message.receiver not in self.inboxes:
            raise ValueError("Unknown receiver")
        self.inboxes[message.receiver].append(message)
        self.history.append(message)

    def receive(self, agent_id):
        messages = list(self.inboxes[agent_id])
        self.inboxes[agent_id].clear()
        return messages


def choose_winner(bids):
    """Select the lowest-cost bid, then lowest robot ID."""
    if not bids:
        return None

    return min(
        bids,
        key=lambda msg: (msg.bid_value, msg.sender)
    )
