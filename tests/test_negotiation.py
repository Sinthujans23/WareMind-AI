
from waremind.mesa_model import WarehouseMesaModel
from waremind.messages import Message, MessageType
from waremind.negotiation import MessageBus, choose_winner


def test_message_delivery():
    bus = MessageBus()
    bus.register(0)
    bus.register(1)

    msg = Message(0, 1, MessageType.CFP, 10)
    bus.send(msg)

    assert bus.receive(1) == [msg]
    assert bus.receive(1) == []


def test_lowest_bid_wins():
    bids = [
        Message(1, 0, MessageType.BID, 1, 12.5),
        Message(2, 0, MessageType.BID, 1, 8.2),
        Message(3, 0, MessageType.BID, 1, 15.0),
    ]

    winner = choose_winner(bids)

    assert winner.sender == 2


def test_contract_net_messages():
    model = WarehouseMesaModel()
    order = model.add_order((3, 2))

    model.step()

    types = [m.type for m in model.bus.history]

    assert MessageType.CFP in types
    assert MessageType.BID in types
    assert MessageType.AWARD in types
    assert MessageType.ACCEPT in types

    assert order.assigned_to is not None


def test_negotiated_delivery():
    model = WarehouseMesaModel()
    model.add_order((3, 2))

    for _ in range(100):
        model.step()
        if model.warehouse.completed_count == 1:
            break

    assert model.warehouse.completed_count == 1


def test_busy_robot_does_not_bid():
    model = WarehouseMesaModel()

    # Create a real order for Robot 1.
    existing_order = model.add_order((2, 3))
    existing_order.assigned_to = 1
    model.warehouse.robots[0].order_id = existing_order.id

    # Create a new order for negotiation.
    new_order = model.add_order((3, 2))

    model.step()

    # Check bids only for the new order.
    bids = [
        msg
        for msg in model.bus.history
        if (
            msg.type == MessageType.BID
            and msg.order_id == new_order.id
        )
    ]

    # Busy Robot 1 must not bid for the new order.
    assert all(msg.sender != 1 for msg in bids)

    # Another available robot should receive the order.
    assert new_order.assigned_to in (2, 3)

