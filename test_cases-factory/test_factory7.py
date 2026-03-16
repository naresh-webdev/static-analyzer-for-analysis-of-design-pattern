from abc import ABC, abstractmethod

class Restaurant(ABC):
    @abstractmethod
    def create_burger(self):
        pass

class BeefRestaurant(Restaurant):
    def create_burger(self):
        return BeefBurger()  # ← only one subclass, not enough
    

class BeefBurger:
    pass
