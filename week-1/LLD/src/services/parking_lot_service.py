from typing import Optional, List, Dict
from datetime import datetime

from ..models.parking_lot import ParkingLot
from ..models.parking_floor import ParkingFloor
from ..models.parking_slot import ParkingSlot
from ..models.ticket import Ticket
from ..enums.vehicle_type import VehicleType
from ..factories.vehicle_factory import VehicleFactory
from ..strategies.fee_strategy import FeeStrategy
from ..strategies.slot_allocation_strategy import SlotAllocationStrategy

class ParkingLotService:
    """
    Service layer providing clean business APIs for the parking lot application.
    Coordinates between models, factories, and strategies.
    """
    def __init__(self, parking_lot: ParkingLot):
        self.parking_lot = parking_lot

    def add_floor(self, floor_number: int) -> None:
        if floor_number < 1:
            raise ValueError(f"Floor number must be positive (received: {floor_number}).")
        floor = ParkingFloor(floor_number)
        self.parking_lot.add_floor(floor)

    def add_slot(self, floor_number: int, slot_id: str, vehicle_type_str: str) -> None:
        floor = self.parking_lot.floors.get(floor_number)
        if not floor:
            raise ValueError(f"Floor {floor_number} does not exist. Please add floor first.")
        v_type = VehicleType.from_string(vehicle_type_str)
        slot = ParkingSlot(slot_id, floor_number, v_type)
        floor.add_slot(slot)

    def park_vehicle(self, vehicle_type_str: str, license_plate: str) -> Ticket:
        # Uses VehicleFactory to instantiate appropriate Vehicle subclass
        vehicle = VehicleFactory.create_vehicle(vehicle_type_str, license_plate)
        return self.parking_lot.park_vehicle(vehicle)

    def unpark_vehicle(self, ticket_id: str, exit_time: Optional[datetime] = None) -> (Ticket, float):
        return self.parking_lot.unpark_vehicle(ticket_id, exit_time)

    def view_free_slots(self, vehicle_type_str: Optional[str] = None) -> List[ParkingSlot]:
        v_type = VehicleType.from_string(vehicle_type_str) if vehicle_type_str else None
        return self.parking_lot.get_free_slots(v_type)

    def display_occupancy(self) -> Dict[int, Dict[str, Dict[str, int]]]:
        return self.parking_lot.get_occupancy()

    def set_fee_strategy(self, strategy: FeeStrategy) -> None:
        self.parking_lot.set_fee_strategy(strategy)

    def set_slot_strategy(self, strategy: SlotAllocationStrategy) -> None:
        self.parking_lot.set_slot_strategy(strategy)
