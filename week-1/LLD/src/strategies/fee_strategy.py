from abc import ABC, abstractmethod
from datetime import datetime
import math
from ..models.ticket import Ticket
from ..enums.vehicle_type import VehicleType

class FeeStrategy(ABC):
    """
    Strategy interface for calculating parking fees.
    I used the Strategy Pattern so pricing algorithms can be changed
    without modifying the ParkingLot or Ticket classes.
    """
    @abstractmethod
    def calculate_fee(self, ticket: Ticket, exit_time: datetime) -> float:
        pass


class FlatRateFeeStrategy(FeeStrategy):
    """
    Charges a flat hourly rate based on vehicle type.
    Partial hours are rounded up to the nearest full hour (minimum 1 hour).
    """
    def __init__(self):
        self.hourly_rates = {
            VehicleType.BIKE: 10.0,
            VehicleType.CAR: 20.0,
            VehicleType.TRUCK: 50.0,
        }

    def calculate_fee(self, ticket: Ticket, exit_time: datetime) -> float:
        duration_seconds = (exit_time - ticket.entry_time).total_seconds()
        if duration_seconds < 0:
            raise ValueError("Exit time cannot be earlier than entry time.")

        # Minimum 1 hour, partial hours rounded up
        hours = max(1, math.ceil(duration_seconds / 3600.0))
        rate = self.hourly_rates.get(ticket.vehicle.vehicle_type, 20.0)
        return float(hours * rate)


class TieredFeeStrategy(FeeStrategy):
    """
    Charges a base rate for the first hour and a discounted hourly rate
    for subsequent hours.
    """
    def __init__(self):
        # (first_hour_rate, additional_hour_rate)
        self.tiered_rates = {
            VehicleType.BIKE: (10.0, 5.0),
            VehicleType.CAR: (20.0, 15.0),
            VehicleType.TRUCK: (50.0, 35.0),
        }

    def calculate_fee(self, ticket: Ticket, exit_time: datetime) -> float:
        duration_seconds = (exit_time - ticket.entry_time).total_seconds()
        if duration_seconds < 0:
            raise ValueError("Exit time cannot be earlier than entry time.")

        hours = max(1, math.ceil(duration_seconds / 3600.0))
        first_hour_rate, next_hour_rate = self.tiered_rates.get(
            ticket.vehicle.vehicle_type, (20.0, 15.0)
        )

        if hours == 1:
            return float(first_hour_rate)
        return float(first_hour_rate + (hours - 1) * next_hour_rate)
