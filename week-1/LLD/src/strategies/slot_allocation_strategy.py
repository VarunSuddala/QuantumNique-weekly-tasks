from abc import ABC, abstractmethod
from typing import Dict, Optional
from ..models.parking_floor import ParkingFloor
from ..models.parking_slot import ParkingSlot
from ..enums.vehicle_type import VehicleType

class SlotAllocationStrategy(ABC):
    """
    Strategy interface for finding a suitable parking slot.
    I used the Strategy Pattern here so that slot allocation logic
    (e.g., lowest floor first, nearest to elevator, best-fit)
    can be swapped without altering the ParkingLot class.
    """
    @abstractmethod
    def find_slot(self, floors: Dict[int, ParkingFloor], vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        pass


class LowestFloorSlotStrategy(SlotAllocationStrategy):
    """
    Finds the first available slot matching the vehicle type,
    starting from the lowest floor number upwards.
    """
    def find_slot(self, floors: Dict[int, ParkingFloor], vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        # Iterate through floors in ascending numerical order
        for floor_num in sorted(floors.keys()):
            floor = floors[floor_num]
            available_slots = floor.get_available_slots(vehicle_type)
            if available_slots:
                return available_slots[0]
        return None


class HighFloorFirstStrategy(SlotAllocationStrategy):
    """
    Alternative strategy: fills higher floors first to keep lower floors
    open for quick turnarounds.
    """
    def find_slot(self, floors: Dict[int, ParkingFloor], vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        for floor_num in sorted(floors.keys(), reverse=True):
            floor = floors[floor_num]
            available_slots = floor.get_available_slots(vehicle_type)
            if available_slots:
                return available_slots[0]
        return None
