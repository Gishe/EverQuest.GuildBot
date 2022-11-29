from dataclasses import dataclass

@dataclass
class PlayerBid:
    from_player: str
    amount: int
    is_box_bid: bool
    is_alt_bid: bool
