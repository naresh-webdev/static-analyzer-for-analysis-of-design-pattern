from abc import ABC, abstractmethod

class Restaurant(ABC):
    @abstractmethod
    def create_burger(self):
        pass
    
    def order_burger(self):
        burger = self.create_burger()
        return burger

class BeefRestaurant(Restaurant):
    def create_burger(self):
        return BeefBurger()

class VeggieRestaurant(Restaurant):
    def create_burger(self):
        return VeggieBurger()

class BeefBurger:
    pass

class VeggieBurger:
    pass