from datetime import datetime
from game.logging.entities.log_message import LogMessage
from game.dkp.entities.bid_message import BidMessage, EnqueueBidItemsMessage, \
    StartRoundMessage, EndRoundMessage, BidOnItemMessage, BeginRaidMessage, \
    BidMessageType

ENQUEUE_ITEMS_CMD = '#enqueue-items'
START_ROUND_CMD = '#start-round'
END_ROUND_CMD = '#end-round'
ITEM_BID_CMD = '#bid'
BEGIN_RAID_CMD = '#begin-raid'

def parse_bid_message(tell_message: LogMessage):
    if tell_message.inner_message.startswith(ENQUEUE_ITEMS_CMD):
        return EnqueueBidItemsMessage(
            timestamp = tell_message.timestamp,
            full_message = tell_message.inner_message,
            from_player = tell_message.from_character,
            items = [
                item.strip() for item in
                filter(None, tell_message.inner_message.lstrip(ENQUEUE_ITEMS_CMD).split(';'))
            ]
        )
    if tell_message.inner_message.startswith(START_ROUND_CMD):
        round_length = tell_message.inner_message.lstrip(START_ROUND_CMD).strip()
        if len(round_length) > 0:
            if not round_length.isnumeric():
                # TODO: Raise an exception / send message back to player
                return

        return StartRoundMessage(
            timestamp = tell_message.timestamp,
            full_message = tell_message.inner_message,
            from_player = tell_message.from_character,
            length = round_length or 0
        )
    if tell_message.inner_message.startswith(END_ROUND_CMD):
        return EndRoundMessage(
            timestamp = tell_message.timestamp,
            full_message = tell_message.inner_message,
            from_player = tell_message.from_character
        )
    if tell_message.inner_message.startswith(ITEM_BID_CMD):
        bid_parts = tell_message.inner_message.lstrip(ITEM_BID_CMD).split(':')

        if len(bid_parts) != 2:
            # TODO: Raise an exception / send message back to player
            return

        bid_attributes = bid_parts[1].strip().split(' ')

        amount_str = bid_attributes[0].strip() 
        if not amount_str or not amount_str.isnumeric():
            # TODO: Raise an exception / send message back to player
            return

        return BidOnItemMessage(
            timestamp = tell_message.timestamp,
            full_message = tell_message.inner_message,
            from_player = tell_message.from_character,
            item = bid_parts[0].strip(),
            amount = int(amount_str),
            is_box_bid = 'box' in bid_attributes,
            is_alt_bid = 'alt' in bid_attributes
        )
    if tell_message.inner_message.startswith(BEGIN_RAID_CMD):
        raid_name = tell_message.inner_message.lstrip(BEGIN_RAID_CMD).strip()
        if not raid_name:
            # TODO: Raise an exception / send message back to player
            return
        
        return BeginRaidMessage(
            timestamp = tell_message.timestamp,
            full_message = tell_message.inner_message,
            from_player = tell_message.from_character,
            raid_name = raid_name
        )

    return None
