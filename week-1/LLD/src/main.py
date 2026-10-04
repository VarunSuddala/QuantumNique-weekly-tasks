import os
import sys
from datetime import datetime, timedelta

# Ensure parent directory is on sys.path so package imports work cleanly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.models.parking_lot import ParkingLot
from src.services.parking_lot_service import ParkingLotService
from src.strategies.fee_strategy import FlatRateFeeStrategy, TieredFeeStrategy
from src.strategies.slot_allocation_strategy import LowestFloorSlotStrategy


def print_divider(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def main():
    print_divider("INITIALIZING PARKING LOT")
    lot = ParkingLot("LOT-1", "Downtown Multi-Floor Parking")
    service = ParkingLotService(lot)
    print(f"Parking Lot '{lot.name}' created.")

    # 1. Add Floors
    print("\n[Operation 1] Adding 2 Floors...")
    service.add_floor(1)
    service.add_floor(2)
    print("Floors 1 and 2 added successfully.")

    # 2. Add Parking Slots
    print("\n[Operation 2] Adding Slots to Floors...")
    # Floor 1: 1 Bike slot, 1 Car slot
    service.add_slot(1, "F1-B1", "BIKE")
    service.add_slot(1, "F1-C1", "CAR")
    # Floor 2: 1 Car slot, 1 Truck slot
    service.add_slot(2, "F2-C1", "CAR")
    service.add_slot(2, "F2-T1", "TRUCK")
    print("Floor 1: Slots F1-B1 (BIKE), F1-C1 (CAR)")
    print("Floor 2: Slots F2-C1 (CAR), F2-T1 (TRUCK)")

    # 3. View initial free slots
    print_divider("OPERATION: VIEW INITIAL FREE SLOTS")
    all_free = service.view_free_slots()
    print(f"Total free slots available: {len(all_free)}")
    for slot in all_free:
        print(f"  -> Floor {slot.floor_number}, Slot {slot.slot_id} ({slot.supported_type.value})")

    # 4. Park Bike
    print_divider("OPERATION: PARK BIKE")
    ticket_bike = service.park_vehicle("BIKE", "KA-01-AB-1234")
    print(f"SUCCESS: Bike parked!")
    print(f"  Ticket ID : {ticket_bike.ticket_id}")
    print(f"  Floor     : {ticket_bike.floor_number}")
    print(f"  Slot ID   : {ticket_bike.slot_id}")
    print(f"  Entry Time: {ticket_bike.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")

    # 5. Park Car 1
    print_divider("OPERATION: PARK CAR 1")
    ticket_car1 = service.park_vehicle("CAR", "DL-04-CA-5678")
    print(f"SUCCESS: Car 1 parked!")
    print(f"  Ticket ID : {ticket_car1.ticket_id}")
    print(f"  Floor     : {ticket_car1.floor_number} (Allocated lowest available floor)")
    print(f"  Slot ID   : {ticket_car1.slot_id}")

    # 6. Park Truck
    print_divider("OPERATION: PARK TRUCK")
    ticket_truck = service.park_vehicle("TRUCK", "MH-12-TR-9999")
    print(f"SUCCESS: Truck parked!")
    print(f"  Ticket ID : {ticket_truck.ticket_id}")
    print(f"  Floor     : {ticket_truck.floor_number}")
    print(f"  Slot ID   : {ticket_truck.slot_id}")

    # 7. Display Occupancy Status
    print_divider("OPERATION: DISPLAY OCCUPANCY")
    occupancy = service.display_occupancy()
    for floor_num, counts in occupancy.items():
        print(f"Floor {floor_num}:")
        for v_type, data in counts.items():
            if data["total"] > 0:
                print(f"  {v_type:<6}: Total = {data['total']}, Occupied = {data['occupied']}, Free = {data['free']}")

    # 8. Unpark Car 1 and Calculate Fee (Simulating 3 hours duration)
    print_divider("OPERATION: UNPARK VEHICLE & CALCULATE FEE")
    simulated_exit_time = ticket_car1.entry_time + timedelta(hours=3)
    completed_ticket, fee = service.unpark_vehicle(ticket_car1.ticket_id, exit_time=simulated_exit_time)
    print(f"SUCCESS: Vehicle unparked!")
    print(f"  Vehicle Plate: {completed_ticket.vehicle.license_plate} ({completed_ticket.vehicle.vehicle_type.value})")
    print(f"  Slot Released: Floor {completed_ticket.floor_number}, Slot {completed_ticket.slot_id}")
    print(f"  Duration     : 3 hours")
    print(f"  Fee Strategy : FlatRate ($20/hour for Car)")
    print(f"  Total Fee    : ${fee:.2f}")

    # 9. Demonstrate Strategy Switch (Tiered Pricing)
    print_divider("STRATEGY PATTERN: SWITCHING FEE STRATEGY TO TIERED")
    service.set_fee_strategy(TieredFeeStrategy())
    print("Fee strategy switched to TieredFeeStrategy (First hour base, remaining hours discounted).")
    # Park another car and exit after 4 hours
    ticket_car2 = service.park_vehicle("CAR", "TS-07-EA-4321")
    simulated_exit_car2 = ticket_car2.entry_time + timedelta(hours=4)
    _, tiered_fee = service.unpark_vehicle(ticket_car2.ticket_id, exit_time=simulated_exit_car2)
    print(f"Car parked and exited after 4 hours under Tiered Pricing:")
    print(f"  Calculation  : First hour = $20, Next 3 hours @ $15/hr = $45")
    print(f"  Total Fee    : ${tiered_fee:.2f}")

    # =========================================================================
    # EDGE CASES DEMONSTRATION
    # =========================================================================
    print_divider("EDGE CASES & VALIDATION")

    # Edge Case 1: Duplicate Vehicle Parking
    print("\n[Edge Case 1] Trying to park already parked vehicle (Bike 'KA-01-AB-1234')...")
    try:
        service.park_vehicle("BIKE", "KA-01-AB-1234")
    except ValueError as e:
        print(f"  CAUGHT EXPECTED ERROR: {e}")

    # Edge Case 2: Full Slot / No Available Slot
    print("\n[Edge Case 2] Trying to park another Truck when only 1 truck slot existed (and it is occupied)...")
    try:
        service.park_vehicle("TRUCK", "AP-09-TR-7777")
    except ValueError as e:
        print(f"  CAUGHT EXPECTED ERROR: {e}")

    # Edge Case 3: Invalid Ticket ID
    print("\n[Edge Case 3] Trying to unpark with a fake/non-existent ticket ID...")
    try:
        service.unpark_vehicle("TKT-INVALID-999")
    except ValueError as e:
        print(f"  CAUGHT EXPECTED ERROR: {e}")

    # Edge Case 4: Repeated Exit with Already Used Ticket
    print("\n[Edge Case 4] Trying to unpark with already completed ticket (ticket_car1)...")
    try:
        service.unpark_vehicle(ticket_car1.ticket_id)
    except ValueError as e:
        print(f"  CAUGHT EXPECTED ERROR: {e}")

    # Edge Case 5: Invalid Vehicle Type
    print("\n[Edge Case 5] Trying to park an unsupported vehicle type ('AIRPLANE')...")
    try:
        service.park_vehicle("AIRPLANE", "BOEING-737")
    except ValueError as e:
        print(f"  CAUGHT EXPECTED ERROR: {e}")

    # Edge Case 6: Adding Duplicate Floor / Slot
    print("\n[Edge Case 6] Trying to add already existing floor 1...")
    try:
        service.add_floor(1)
    except ValueError as e:
        print(f"  CAUGHT EXPECTED ERROR: {e}")

    print_divider("DRIVER DEMONSTRATION COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
