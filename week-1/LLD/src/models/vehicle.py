from abc import ABC
from ..enums.vehicle_type import VehicleType

class Vehicle(ABC):
    """
    Abstract base class for all vehicles.
    Uses polymorphism so that each vehicle subclass supplies its own VehicleType.
    """
    def __init__(self, license_plate: str, vehicle_type: VehicleType):
        if not license_plate or not license_plate.strip():
            raise ValueError("License plate cannot be empty.")
        self.license_plate = license_plate.strip().upper()
        self.vehicle_type = vehicle_type

    def __repr__(self):
        return f"{self.__class__.__name__}(plate='{self.license_plate}', type={self.vehicle_type.value})"


class Bike(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.BIKE)


class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)


class Truck(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.TRUCK)
