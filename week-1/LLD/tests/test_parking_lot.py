import unittest
import os
import sys
from datetime import datetime, timedelta

# Ensure parent directory is on sys.path so package imports work cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.parking_lot import ParkingLot
from src.services.parking_lot_service import ParkingLotService
from src.enums.ticket_status import TicketStatus
from src.enums.vehicle_type import VehicleType
from src.strategies.fee_strategy import FlatRateFeeStrategy, TieredFeeStrategy
from src.strategies.slot_allocation_strategy import LowestFloorSlotStrategy, HighFloorFirstStrategy


class TestParkingLotSystem(unittest.TestCase):
    def setUp(self):
        """Set up a fresh ParkingLot with 2 floors and predefined slots before each test."""
        self.lot = ParkingLot("TEST-LOT", "Test Facility")
        self.service = ParkingLotService(self.lot)

        # Floor 1: 1 Bike, 1 Car
        self.service.add_floor(1)
        self.service.add_slot(1, "F1-B1", "BIKE")
        self.service.add_slot(1, "F1-C1", "CAR")

        # Floor 2: 1 Car, 1 Truck
        self.service.add_floor(2)
        self.service.add_slot(2, "F2-C1", "CAR")
        self.service.add_slot(2, "F2-T1", "TRUCK")

    def test_01_successful_parking(self):
        """Test parking a valid car succeeds and updates slot state."""
        ticket = self.service.park_vehicle("CAR", "DL-01-AA-1111")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.vehicle.license_plate, "DL-01-AA-1111")
        self.assertEqual(ticket.status, TicketStatus.ACTIVE)

        # Verify slot is occupied
        slot = self.lot.floors[ticket.floor_number].get_slot(ticket.slot_id)
        self.assertFalse(slot.is_available())
        self.assertEqual(slot.current_vehicle.license_plate, "DL-01-AA-1111")

    def test_02_correct_ticket_generation(self):
        """Test ticket contains correct metadata (ID, vehicle, floor, slot, entry time)."""
        ticket = self.service.park_vehicle("BIKE", "KA-05-BB-2222")
        self.assertTrue(ticket.ticket_id.startswith("TKT-1-F1-B1-"))
        self.assertEqual(ticket.floor_number, 1)
        self.assertEqual(ticket.slot_id, "F1-B1")
        self.assertEqual(ticket.vehicle.vehicle_type, VehicleType.BIKE)
        self.assertIsInstance(ticket.entry_time, datetime)
        self.assertIsNone(ticket.exit_time)

    def test_03_correct_slot_allocation_lowest_floor(self):
        """Test default strategy picks lowest available floor first."""
        # First car should take Floor 1 slot
        ticket1 = self.service.park_vehicle("CAR", "CAR-FLOOR-1")
        self.assertEqual(ticket1.floor_number, 1)
        self.assertEqual(ticket1.slot_id, "F1-C1")

        # Second car should take Floor 2 slot because Floor 1 car slot is full
        ticket2 = self.service.park_vehicle("CAR", "CAR-FLOOR-2")
        self.assertEqual(ticket2.floor_number, 2)
        self.assertEqual(ticket2.slot_id, "F2-C1")

    def test_04_duplicate_vehicle_error(self):
        """Test parking the same license plate twice raises a ValueError."""
        self.service.park_vehicle("CAR", "DUP-1234")
        with self.assertRaises(ValueError) as context:
            self.service.park_vehicle("CAR", "DUP-1234")
        self.assertIn("already parked", str(context.exception))

    def test_05_no_available_slot_error(self):
        """Test parking when all designated slots for that vehicle type are full."""
        # Only 1 truck slot exists (on Floor 2)
        self.service.park_vehicle("TRUCK", "TRUCK-1")
        # Attempting to park a 2nd truck must raise error
        with self.assertRaises(ValueError) as context:
            self.service.park_vehicle("TRUCK", "TRUCK-2")
        self.assertIn("No available slot found", str(context.exception))

    def test_06_invalid_ticket_error(self):
        """Test unparking with a non-existent ticket ID raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.service.unpark_vehicle("TKT-DOES-NOT-EXIST")
        self.assertIn("Invalid ticket", str(context.exception))

    def test_07_successful_exit_and_fee_calculation(self):
        """Test unparking releases slot, marks ticket completed, and calculates fee."""
        ticket = self.service.park_vehicle("CAR", "EXIT-CAR-99")
        exit_time = ticket.entry_time + timedelta(hours=2)

        completed_ticket, fee = self.service.unpark_vehicle(ticket.ticket_id, exit_time=exit_time)

        # 2 hours for Car @ $20/hr = $40.00
        self.assertEqual(fee, 40.0)
        self.assertEqual(completed_ticket.status, TicketStatus.COMPLETED)
        self.assertEqual(completed_ticket.exit_time, exit_time)

        # Verify slot is free again
        slot = self.lot.floors[ticket.floor_number].get_slot(ticket.slot_id)
        self.assertTrue(slot.is_available())

        # Vehicle should no longer be tracked as parked
        self.assertNotIn("EXIT-CAR-99", self.lot.parked_plates)

    def test_08_repeated_exit_error(self):
        """Test attempting to unpark with an already exited ticket raises ValueError."""
        ticket = self.service.park_vehicle("BIKE", "REPEAT-BIKE")
        self.service.unpark_vehicle(ticket.ticket_id)

        # Attempting to unpark a second time
        with self.assertRaises(ValueError) as context:
            self.service.unpark_vehicle(ticket.ticket_id)
        self.assertIn("already been completed", str(context.exception))

    def test_09_invalid_vehicle_type(self):
        """Test attempting to park an unsupported vehicle type raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.service.park_vehicle("HELICOPTER", "HELI-01")
        self.assertIn("Invalid vehicle type", str(context.exception))

    def test_10_tiered_fee_strategy_switching(self):
        """Test dynamic switching to TieredFeeStrategy."""
        self.service.set_fee_strategy(TieredFeeStrategy())
        ticket = self.service.park_vehicle("CAR", "TIER-CAR")
        # 3 hours: 1st hour = $20, next 2 hours @ $15 = $30. Total = $50
        exit_time = ticket.entry_time + timedelta(hours=3)
        _, fee = self.service.unpark_vehicle(ticket.ticket_id, exit_time=exit_time)
        self.assertEqual(fee, 50.0)


if __name__ == "__main__":
    unittest.main()
