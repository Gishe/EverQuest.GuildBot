
class BiddableItem:
    def __init__(self, name):
        self.count = 1
        self.name = name
        self.bids = []
    
    def increase_count(self):
        self.count += 1

    def print(self):
        return self.name if self.count == 1 else f'{self.name} x{self.count}'
