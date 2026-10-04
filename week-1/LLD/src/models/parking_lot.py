from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid
from ..enums.vehicle_type import VehicleType
from ..models.parking_floor import ParkingFloor
from ..models.parking_slot import ParkingSlot
from ..models.vehicle import Vehicle
from ..models.ticket import Ticket
from ..strategies.slot_allocation_strategy import SlotAllocationStrategy, LowestFloorSlotStrategy
from ..strategies.fee_strategy import FeeStrategy, FlatRateFeeStrategy

class ParkingLot:
    """
    Central model for the parking lot.
    Maintains floors, active tickets, and references to slot and fee strategies.
    """
    def __init__(
        self,
        lot_id: str,
        name: str,
        slot_strategy: Optional[SlotAllocationStrategy] = None,
        fee_strategy: Optional[FeeStrategy] = None,
    ):
        self.lot_id = lot_id
        self.name = name
        self.floors: Dict[int, ParkingFloor] = {}
        self.active_tickets: Dict[str, Ticket] = {}
        # Maps license_plate -> ticket_id to quickly prevent duplicate vehicle parking
        self.parked_plates: Dict[str, str] = {}

        # Default strategies (Strategy Pattern)
        self.slot_strategy = slot_strategy if slot_strategy is not None else LowestFloorSlotStrategy()
        self.fee_strategy = fee_strategy if fee_strategy is not None else FlatRateFeeStrategy()

    def set_slot_strategy(self, strategy: SlotAllocationStrategy) -> None:
        self.slot_strategy = strategy

    def set_fee_strategy(self, strategy: FeeStrategy) -> None:
        self.fee_strategy = strategy

    def add_floor(self, floor: ParkingFloor) -> None:
        if floor.floor_number in self.floors:
            raise ValueError(f"Floor {floor.floor_number} already exists in {self.name}.")
        self.floors[floor.floor_number] = floor

    def park_vehicle(self, vehicle: Vehicle) -> Ticket:
        # Check duplicate vehicle parking
        if vehicle.license_plate in self.parked_plates:
            existing_ticket_id = self.parked_plates[vehicle.license_plate]
            raise ValueError(
                f"Vehicle with plate '{vehicle.license_plate}' is already parked (Ticket: {existing_ticket_id})."
            )

        # Allocate slot using current SlotAllocationStrategy
        slot = self.slot_strategy.find_slot(self.floors, vehicle.vehicle_type)
        if slot is None:
            raise ValueError(
                f"Parking Full: No available slot found for vehicle type '{vehicle.vehicle_type.value}'."
            )

        # Occupy slot
        slot.assign_vehicle(vehicle)

        # Issue ticket
        ticket_id = f"TKT-{slot.floor_number}-{slot.slot_id}-{uuid.uuid4().hex[:6].upper()}"
        ticket = Ticket(
            ticket_id=ticket_id,
            vehicle=vehicle,
            floor_number=slot.floor_number,
            slot_id=slot.slot_id,
        )

        self.active_tickets[ticket_id] = ticket
        self.parked_plates[vehicle.license_plate] = ticket_id
        return ticket

    def unpark_vehicle(self, ticket_id: str, exit_time: Optional[datetime] = None) -> Tuple[Ticket, float]:
        if exit_time is None:
            exit_time = datetime.now()

        # Check if ticket exists
        if ticket_id not in self.active_tickets:
            raise ValueError(f"Invalid ticket: Ticket '{ticket_id}' not found.")

        ticket = self.active_tickets[ticket_id]

        # Check repeated exit
        if not ticket.is_active():
            raise ValueError(f"Repeated exit: Ticket '{ticket_id}' has already been completed.")

        # Find slot and vacate
        floor = self.floors.get(ticket.floor_number)
        if not floor:
            raise ValueError(f"Floor {ticket.floor_number} referenced in ticket does not exist.")

        slot = floor.get_slot(ticket.slot_id)
        if not slot:
            raise ValueError(f"Slot {ticket.slot_id} on floor {ticket.floor_number} does not exist.")

        # Vacate slot
        slot.vacate()

        # Calculate fee using current FeeStrategy
        fee = self.fee_strategy.calculate_fee(ticket, exit_time)
        ticket.close(exit_time, fee)

        # Remove from active tracking
        del self.parked_plates[ticket.vehicle.license_plate]

        return ticket, fee

    def get_free_slots(self, vehicle_type: Optional[VehicleType] = None) -> List[ParkingSlot]:
        free_slots = []
        for floor_num in sorted(self.floors.keys()):
            free_slots.extend(self.floors[floor_num].get_available_slots(vehicle_type))
        return free_slots

    def get_occupancy(self) -> Dict[int, Dict[str, Dict[str, int]]]:
        """
        Returns floor-by-floor occupancy breakdown.
        """
        occupancy = {}
        for floor_num in sorted(self.floors.keys()):
            occupancy[floor_num] = self.floors[floor_num].get_occupancy()
        return occupancy
