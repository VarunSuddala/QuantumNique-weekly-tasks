from datetime import datetime
from typing import Optional
from ..enums.ticket_status import TicketStatus
from .vehicle import Vehicle

class Ticket:
    """
    Represents a parking receipt issued when a vehicle enters the lot.
    """
    def __init__(self, ticket_id: str, vehicle: Vehicle, floor_number: int, slot_id: str, entry_time: Optional[datetime] = None):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.floor_number = floor_number
        self.slot_id = slot_id
        self.entry_time = entry_time if entry_time is not None else datetime.now()
        self.exit_time: Optional[datetime] = None
        self.fee: float = 0.0
        self.status = TicketStatus.ACTIVE

    def is_active(self) -> bool:
        return self.status == TicketStatus.ACTIVE

    def close(self, exit_time: datetime, fee: float) -> None:
        if self.status == TicketStatus.COMPLETED:
            raise ValueError(f"Ticket {self.ticket_id} is already closed/completed.")
        self.exit_time = exit_time
        self.fee = fee
        self.status = TicketStatus.COMPLETED

    def __repr__(self):
        return (
            f"Ticket(id='{self.ticket_id}', vehicle='{self.vehicle.license_plate}', "
            f"floor={self.floor_number}, slot='{self.slot_id}', status={self.status.value})"
        )
