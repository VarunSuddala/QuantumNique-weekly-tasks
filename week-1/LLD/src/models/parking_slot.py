from typing import Optional
from ..enums.vehicle_type import VehicleType
from ..enums.slot_status import SlotStatus
from .vehicle import Vehicle

class ParkingSlot:
    """
    Represents an individual parking slot on a specific floor.
    Each slot is designated for a specific VehicleType.
    """
    def __init__(self, slot_id: str, floor_number: int, supported_type: VehicleType):
        self.slot_id = slot_id
        self.floor_number = floor_number
        self.supported_type = supported_type
        self.status = SlotStatus.AVAILABLE
        self.current_vehicle: Optional[Vehicle] = None

    def is_available(self) -> bool:
        return self.status == SlotStatus.AVAILABLE

    def can_fit_vehicle(self, vehicle: Vehicle) -> bool:
        return self.is_available() and self.supported_type == vehicle.vehicle_type

    def assign_vehicle(self, vehicle: Vehicle) -> None:
        if not self.is_available():
            raise ValueError(f"Slot {self.slot_id} on floor {self.floor_number} is already occupied.")
        if self.supported_type != vehicle.vehicle_type:
            raise ValueError(
                f"Slot {self.slot_id} is for {self.supported_type.value}, cannot park {vehicle.vehicle_type.value}."
            )
        self.current_vehicle = vehicle
        self.status = SlotStatus.OCCUPIED

    def vacate(self) -> Vehicle:
        if self.is_available() or self.current_vehicle is None:
            raise ValueError(f"Slot {self.slot_id} on floor {self.floor_number} is already vacant.")
        released_vehicle = self.current_vehicle
        self.current_vehicle = None
        self.status = SlotStatus.AVAILABLE
        return released_vehicle

    def __repr__(self):
        return f"Slot(id='{self.slot_id}', floor={self.floor_number}, type={self.supported_type.value}, status={self.status.value})"
