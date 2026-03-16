class VehicleFactory:
    def create_vehicle(self, vehicle_type):
        if vehicle_type == "heavy":
            return "truck"   # ← returns string not object
        elif vehicle_type == "light":
            return "car"