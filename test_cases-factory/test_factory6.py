class VehicleFactory:
    _registry = {
        "heavy": "Truck",    # ← strings not class references
        "light": "Car"
    }
    
    def create_vehicle(self, vehicle_type):
        return self._registry[vehicle_type]()