from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List

from enum import Enum

class BidMessageType(Enum):
    ENQUEUE_BID_ITEMS = 'Qneue Bid Items'
    BID_ON_ITEM = 'Bid On Item'
    START_ROUND = 'Start Round'
    END_ROUND = 'End Round'
    BEGIN_RAID = 'Begin Raid'

@dataclass
class BidMessage(ABC):
    timestamp: datetime
    full_message: str
    from_player: str

    @property
    @abstractmethod
    def message_type(self) -> BidMessageType:
        pass

    def print(self):
        print(vars(self))

@dataclass
class EnqueueBidItemsMessage(BidMessage):
    items: List

    @property
    def message_type(self) -> BidMessageType:
        return BidMessageType.ENQUEUE_BID_ITEMS

@dataclass
class BeginRaidMessage(BidMessage):
    raid_name: str

    @property
    def message_type(self) -> BidMessageType:
        return BidMessageType.BEGIN_RAID

@dataclass
class StartRoundMessage(BidMessage):
    length: int

    @property
    def message_type(self) -> BidMessageType:
        return BidMessageType.START_ROUND

@dataclass
class EndRoundMessage(BidMessage):
    @property
    def message_type(self) -> BidMessageType:
        return BidMessageType.END_ROUND

@dataclass
class BidOnItemMessage(BidMessage):
    item: str
    amount: int
    is_box_bid: bool
    is_alt_bid: bool

    @property
    def message_type(self) -> BidMessageType:
        return BidMessageType.BID_ON_ITEM
