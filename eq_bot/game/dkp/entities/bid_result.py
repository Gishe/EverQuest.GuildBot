from typing import List
from dataclasses import dataclass

class BidResult:
    def __init__(self, item: str, winner: str = None, tied_players: List[str] = None, amount: int = 0):
        self.winner = winner
        self.tied_players = tied_players or []
        self.amount = amount
        self.item = item

    def build_chat_messages(self):
        if self.tied_players:
            return [
                f'The following players are tied at {self.amount} DKP for the {self.item}: {", ".join(self.tied_players)}',
                f'Please provide your 30 day RA and lifetime ticks to the loot officer to determine tiebreaks.'
            ]

        if not self.winner:
            return [
                f'A {self.item} was released for guild funds'
            ]

        return [
            f'{self.item} ; {self.amount} ; {self.winner} grats'
        ]
