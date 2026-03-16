class VehicleFactory:
    
    def create_vehicle(self, vehicle_type):
        if vehicle_type == "heavy":
            return Truck()
        elif vehicle_type == "light":
            return Car()
        elif vehicle_type == "two-wheeler":
            return Bike()

class Truck:
    pass

class Car:
    pass

class Bike:
    pass