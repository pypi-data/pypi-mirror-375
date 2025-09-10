import random

class RandomObject:
    def __init__(self, *items):
        if not items:
            raise ValueError("باید حداقل یک مقدار وارد کنی.")
        self.items = items

    def get(self):
        return random.choice(self.items)
