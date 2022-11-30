from typing import List

from game.dkp.entities.bid_result import BidResult
from game.dkp.entities.player_bid import PlayerBid

class BiddableItem:
    def __init__(self, name):
        self.count = 1
        self.name = name
        self.bids = []
    
    def increase_count(self):
        self.count += 1

    def _get_win_amount(self, remaining_bids: List[PlayerBid], next_bid_position: int) -> int:
        return remaining_bids[next_bid_position].amount + 1 \
            if len(remaining_bids) > next_bid_position else 1
    
    def _adjust_player_win_amount(self, win_amount: int, player_bid: PlayerBid) -> int:
        return win_amount * 2 if player_bid.is_box_bid else win_amount

    def _resolve_bids(self, bids) -> List[BidResult]:
        remaining_bids = sorted(bids, key = lambda i: i.amount, reverse = True)

        round_results = []
        while self.count > 0 and len(remaining_bids) > 0:
            top_bid_amount = remaining_bids[0].amount
            tied_bids = list(filter(lambda b: (b.amount == top_bid_amount), bids))

            tied_bids_count = len(tied_bids)

            if tied_bids_count > 1:

                # Get the win amount using the next highest bidder who is not part of the tie
                win_amount = self._get_win_amount(remaining_bids, next_bid_position=tied_bids_count)

                # Are there an equal amount or more items available than the number of bidders
                if tied_bids_count <= self.count:

                    round_results.extend([
                        BidResult(
                            winner=bid.from_player,
                            item=self.name,
                            # Adjust bid for each player (i.e. boxes are 2x amount)
                            amount=self._adjust_player_win_amount(win_amount, bid)
                        ) for bid in tied_bids
                    ])

                    # Subtract the items we awarded from remaining bids
                    self.count -= tied_bids_count
                    remaining_bids = remaining_bids[tied_bids_count:]
                else:
                    round_results.append(BidResult(
                        tied_players=[ bid.from_player for bid in tied_bids ],
                        item=self.name,
                        # Do not run through the adjust_player_win_count, since a
                        # tie is associated with multiple bids.
                        amount=win_amount
                    ))

                    # Set remaining to 0 so that we don't release any to guild funds
                    self.count = 0
                    break
            else:
                round_results.append(BidResult(
                    winner=remaining_bids[0].from_player,
                    item=self.name,
                    # Adjust bid for player (i.e. boxes are 2x amount)
                    amount=self._adjust_player_win_amount(
                        # Get the win amount using the next highest bidder
                        self._get_win_amount(remaining_bids, next_bid_position=1),
                        remaining_bids[0])
                ))

                self.count -= 1
                remaining_bids = remaining_bids[1:]

        return round_results
    
    def _get_bids(self, is_alt_bid):
        return list(filter(lambda b: (b.is_alt_bid == is_alt_bid), self.bids))
    
    def _resolve_no_bidders(self):
        return [ BidResult(item=self.name) for _ in range(self.count) ]

    def resolve_bids(self) -> List[BidResult]:
        # Look for items w/o no bids at all and create no bid results
        if len(self.bids) == 0:
            return self._resolve_no_bidders()

        return [
            # Order is important as each function will reduce the count of items
            # and only mains/boxes can win before an alt is allowed to win
            *self._resolve_bids(self._get_bids(is_alt_bid=False)),
            *self._resolve_bids(self._get_bids(is_alt_bid=True)),

            # Add leftovers
            *self._resolve_no_bidders()
        ]

    def print(self):
        return self.name if self.count == 1 else f'{self.name} x{self.count}'
