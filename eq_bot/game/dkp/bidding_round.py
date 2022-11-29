from typing import List

from game.dkp.entities.biddable_item import BiddableItem
from game.dkp.entities.player_bid import PlayerBid
from game.dkp.entities.bid_result import BidResult

MAX_GUILD_MESSAGE_LENGTH = 508
ITEM_JOIN_STR = ' | '

class BiddingRound:
    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._items = []
        self._enabled = False
        self._length = 0
    
    def start(self, length: int) -> None:
        self._enabled = True
        self._length = length
    
    def has_items(self) -> bool:
        return len(self._items) >= 0

    def is_enabled(self) -> bool:
        return self._enabled

    def _build_round_item_message(self, prefix: str) -> List[str]:
        messages_to_send = []
        message = f'{prefix}: {self._items[0].print()}'

        for item in self._items[1:]:
            item_message = item.print()
            if len(message) + len(item_message) + len(ITEM_JOIN_STR) <= MAX_GUILD_MESSAGE_LENGTH:
                message += f'{ITEM_JOIN_STR}{item_message}'
            else:
                messages_to_send.append(message)

                # start the next message with the current item
                message = item_message
        
        messages_to_send.append(message)
        return messages_to_send

    def build_end_round_messages(self) -> List[str]:
        return self._build_round_item_message('BIDDING CLOSED ON')

    def build_start_round_messages(self) -> List[str]:
        return [
            *self._build_round_item_message('BIDDING CURRENTLY OPEN ON'),
            'Please message me with your bid in the following format: #bid itemname : bidamount [box]'
        ]

    def enqueue_items(self, items: List[str]) -> None:
        for item in items:
            existing_item = next((i for i in self._items if i.name == item), None)
            if existing_item:
                existing_item.increase_count()
            else:
                self._items.append(BiddableItem(item))

    def bid_on_item(self, from_player: str, item: str, amount: int, is_box_bid: bool, is_alt_bid: bool) -> None:
        biddable_item = next((i for i in self._items if i.name == item), None)
        if not biddable_item:
            raise KeyError(f'{from_player} attempted to bid on an item which was not in the round: {item}')

        existing_bid = next((b for b in biddable_item.bids if b.from_player == from_player), None)
        if existing_bid:
            existing_bid.amount = amount
            existing_bid.is_box_bid = is_box_bid
            existing_bid.is_alt_bid = is_alt_bid
        else:
            biddable_item.bids.append(PlayerBid(
                from_player = from_player,
                amount = amount,
                is_box_bid = is_box_bid,
                is_alt_bid = is_alt_bid
            ))

    def end_round(self) -> List[BidResult]:
        round_results = []
        for item in self._items:
            if len(item.bids) == 0:
                round_results.append(BidResult(item=item.name))
                break

            remaining_bids = sorted(item.bids, key = lambda i: i.amount, reverse = True)

            # TODO: Handle alt/box logic
            # - Alt bids should never win over a "non" alt bid
            # - Box bids are for 2x the amount of "non" box bids

            remaining_item_count = item.count
            while remaining_item_count > 0 and len(remaining_bids) > 0:
                top_bid_amount = remaining_bids[0].amount
                tied_bids = list(filter(lambda b: (b.amount == top_bid_amount), item.bids))

                tied_bids_count = len(tied_bids)

                if tied_bids_count > 1:

                    # Get the win amount using the next highest bidder who is not part of the tie
                    win_amount = remaining_bids[tied_bids_count].amount + 1 \
                        if len(remaining_bids) > tied_bids_count else 1

                    # Are there an equal amount or more items available than the number of bidders
                    if tied_bids_count <= remaining_item_count:

                        round_results.extend([
                            BidResult(
                                winner=bid.from_player,
                                item=item.name,
                                amount=win_amount
                            ) for bid in tied_bids
                        ])

                        remaining_item_count -= tied_bids_count
                        remaining_bids = remaining_bids[tied_bids_count:]
                    else:
                        round_results.append(BidResult(
                            tied_players=[ bid.from_player for bid in tied_bids ],
                            item=item.name,
                            amount=win_amount
                        ))
                        remaining_item_count = 0
                        break
                else:
                   # Get the win amount using the next highest bidder
                    win_amount = remaining_bids[1].amount + 1 \
                        if len(remaining_bids) > 1 else 1

                    round_results.append(BidResult(
                        winner=remaining_bids[0].from_player,
                        item=item.name,
                        amount=win_amount
                    ))

                    remaining_item_count -= 1
                    remaining_bids = remaining_bids[1:]

            if remaining_item_count > 0:
                round_results.append(BidResult(item=item.name))
                pass

        # End the round, preventing new bids from being accepted
        self.reset()

        return round_results
