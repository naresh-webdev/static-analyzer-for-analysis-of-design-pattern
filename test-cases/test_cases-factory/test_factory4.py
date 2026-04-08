class VehicleFactory:
    def create_vehicle(self, vehicle_type):
        if vehicle_type == "heavy":
            return Truck()
        elif vehicle_type == "light":
            return Truck()  # ← same type, not a real factory
        


class Truck:
    pass

class Car:
    pass
