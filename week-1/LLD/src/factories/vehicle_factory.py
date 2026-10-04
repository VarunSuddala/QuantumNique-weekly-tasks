from ..enums.vehicle_type import VehicleType
from ..models.vehicle import Vehicle, Bike, Car, Truck

class VehicleFactory:
    """
    Factory Pattern for creating Vehicle instances.
    I used the Factory Pattern so that the caller does not have to worry about
    which concrete class (Bike, Car, Truck) to instantiate.
    It encapsulates object creation and validation in one single place.
    """
    @staticmethod
    def create_vehicle(vehicle_type_str: str, license_plate: str) -> Vehicle:
        v_type = VehicleType.from_string(vehicle_type_str)

        if v_type == VehicleType.BIKE:
            return Bike(license_plate)
        elif v_type == VehicleType.CAR:
            return Car(license_plate)
        elif v_type == VehicleType.TRUCK:
            return Truck(license_plate)
        else:
            raise ValueError(f"Unsupported vehicle type: {v_type.value}")
