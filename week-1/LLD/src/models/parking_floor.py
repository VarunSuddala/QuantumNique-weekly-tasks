from typing import Dict, List, Optional
from ..enums.vehicle_type import VehicleType
from .parking_slot import ParkingSlot

class ParkingFloor:
    """
    Represents a single floor containing multiple parking slots.
    """
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.slots: Dict[str, ParkingSlot] = {}

    def add_slot(self, slot: ParkingSlot) -> None:
        if slot.slot_id in self.slots:
            raise ValueError(f"Slot {slot.slot_id} already exists on floor {self.floor_number}.")
        self.slots[slot.slot_id] = slot

    def get_slot(self, slot_id: str) -> Optional[ParkingSlot]:
        return self.slots.get(slot_id)

    def get_available_slots(self, vehicle_type: Optional[VehicleType] = None) -> List[ParkingSlot]:
        available = []
        for slot in self.slots.values():
            if slot.is_available():
                if vehicle_type is None or slot.supported_type == vehicle_type:
                    available.append(slot)
        # Return slots sorted by slot_id for predictable ordering
        return sorted(available, key=lambda s: s.slot_id)

    def get_occupancy(self) -> Dict[str, Dict[str, int]]:
        """
        Returns total and occupied slot counts grouped by vehicle type for this floor.
        """
        summary = {vt.value: {"total": 0, "occupied": 0, "free": 0} for vt in VehicleType}
        for slot in self.slots.values():
            vt = slot.supported_type.value
            summary[vt]["total"] += 1
            if not slot.is_available():
                summary[vt]["occupied"] += 1
            else:
                summary[vt]["free"] += 1
        return summary
