class Truck:
    pass

class Car:
    pass

class Bike:
    pass

class VehicleFactory:
    _registry = {
        "heavy": Truck,
        "light": Car,
        "two-wheeler": Bike
    }
    
    def create_vehicle(self, vehicle_type):
        return self._registry[vehicle_type]()