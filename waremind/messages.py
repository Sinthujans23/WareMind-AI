
"""Messages exchanged between warehouse agents."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MessageType(str, Enum):
    CFP = "CFP"
    BID = "BID"
    AWARD = "AWARD"
    REJECT = "REJECT"
    ACCEPT = "ACCEPT"


@dataclass(frozen=True)
class Message:
    sender: int
    receiver: int
    type: MessageType
    order_id: int
    bid_value: Optional[float] = None
