# Low-Level Design (LLD): Extensible Multi-Floor Parking Lot System

## Project Overview

This project is a console-based, object-oriented parking lot application built in Python 3. It simulates a multi-floor parking lot that can park different vehicle types, issue tickets, track occupancy, release slots, and compute parking fees dynamically.

The system is designed following clean Object-Oriented Programming (OOP) principles and uses two design patterns:
1. **Strategy Pattern**: For slot allocation and fee calculation.
2. **Factory Pattern**: For vehicle creation and validation.

---

## Directory Structure

```
LLD/
├── src/
│   ├── enums/
│   │   ├── vehicle_type.py        # BIKE, CAR, TRUCK
│   │   ├── slot_status.py         # AVAILABLE, OCCUPIED
│   │   ├── ticket_status.py       # ACTIVE, COMPLETED
│   │   └── __init__.py
│   ├── models/
│   │   ├── vehicle.py             # Vehicle (Base), Bike, Car, Truck
│   │   ├── parking_slot.py        # Slot entity
│   │   ├── parking_floor.py       # Floor containing slots
│   │   ├── ticket.py              # Parking ticket
│   │   ├── parking_lot.py         # Main parking lot model
│   │   └── __init__.py
│   ├── strategies/
│   │   ├── fee_strategy.py        # FlatRateFeeStrategy, TieredFeeStrategy
│   │   ├── slot_allocation_strategy.py # LowestFloorSlotStrategy, HighFloorFirstStrategy
│   │   └── __init__.py
│   ├── factories/
│   │   ├── vehicle_factory.py     # VehicleFactory
│   │   └── __init__.py
│   ├── services/
│   │   ├── parking_lot_service.py # Service/controller layer
│   │   └── __init__.py
│   └── main.py                   # Driver program demonstrating operations
│
├── tests/
│   └── test_parking_lot.py       # 10 unit test cases
│
├── UML.md                        # UML explanation and Mermaid code
├── class_diagram.mmd             # Raw Mermaid class diagram
├── sample_output.txt             # Captured console output
└── README.md                     # This documentation file
```

---

## Core Classes & Responsibilities

- **`ParkingLot`**: Manages floors, active tickets, and currently parked vehicles. Delegates slot allocation and fee calculation to strategy objects.
- **`ParkingFloor`**: Represents a floor number and owns a collection of `ParkingSlot` objects. Provides floor-level availability and occupancy metrics.
- **`ParkingSlot`**: Represents an individual slot with an ID, designated `VehicleType`, and current state (`AVAILABLE` or `OCCUPIED`).
- **`Vehicle` (Abstract Base Class)**: Base class containing `license_plate` and `vehicle_type`. Inherited by concrete classes `Bike`, `Car`, and `Truck`.
- **`Ticket`**: Represents an issued parking receipt with `ticket_id`, vehicle details, assigned floor and slot, entry timestamp, exit timestamp, fee, and status (`ACTIVE` / `COMPLETED`).
- **`FeeStrategy` (Interface)**: Defines `calculate_fee(ticket, exit_time)`. Implemented by `FlatRateFeeStrategy` and `TieredFeeStrategy`.
- **`SlotAllocationStrategy` (Interface)**: Defines `find_slot(floors, vehicle_type)`. Implemented by `LowestFloorSlotStrategy` and `HighFloorFirstStrategy`.
- **`VehicleFactory`**: Centralizes the creation of `Vehicle` instances based on input string and license plate.
- **`ParkingLotService`**: Acts as a controller layer coordinating between the caller, `VehicleFactory`, and `ParkingLot`.

---

## Design Patterns Used

### 1. Strategy Pattern
- **Where it is used**:
  - In `FeeStrategy` (for pricing).
  - In `SlotAllocationStrategy` (for choosing which slot to assign).
- **Why it is needed**:
  - Different parking lots or business hours use different fee rules (e.g. flat hourly rates vs tiered first-hour base rates).
  - Similarly, slot allocation logic might prioritize the lowest floor, closest to the entrance, or balanced floor utilization.
- **What problem it solves**:
  - It removes hard-coded `if/else` checks from the `ParkingLot` class.
  - The parking lot only knows about the strategy interface. Pricing and slot allocation algorithms can be changed at runtime using `set_fee_strategy()` and `set_slot_strategy()`.

### 2. Factory Pattern
- **Where it is used**:
  - In `VehicleFactory.create_vehicle(vehicle_type_str, license_plate)`.
- **Why it is needed**:
  - The driver or API receives string input like `"CAR"` or `"BIKE"`.
- **What problem it solves**:
  - Without a factory, every service method or controller would have repetitive `if/elif` blocks instantiating `Car()`, `Bike()`, or `Truck()`.
  - The factory encapsulates validation and object creation in a single place.

---

## Validation & Error Handling

The application validates every operation and raises clear `ValueError` exceptions with human-readable error messages:

1. **Duplicate Vehicle Parking**:
   - `parked_plates` dictionary tracks currently parked license plates.
   - If a car with license plate `"KA-01-AB-1234"` is already parked, attempting to park it again raises:
     `"Vehicle with plate 'KA-01-AB-1234' is already parked (Ticket: ...)."`
2. **Full Slot / No Available Slot**:
   - If all designated slots for a vehicle type are occupied, the system raises:
     `"Parking Full: No available slot found for vehicle type 'TRUCK'."`
3. **Invalid Ticket ID**:
   - If unparking is attempted with a ticket ID not found in `active_tickets`, the system raises:
     `"Invalid ticket: Ticket 'TKT-INVALID-999' not found."`
4. **Repeated Exit**:
   - If an unpark is attempted using a ticket that was already closed, the system checks `ticket.is_active()` and raises:
     `"Repeated exit: Ticket '...' has already been completed."`
5. **Invalid Vehicle Type**:
   - If an unknown type like `"AIRPLANE"` is entered, `VehicleType.from_string()` raises:
     `"Invalid vehicle type 'AIRPLANE'. Supported types are: BIKE, CAR, TRUCK."`
6. **Invalid Floor or Slot**:
   - Adding a duplicate floor or adding a slot to a non-existent floor raises descriptive errors.

---

## Extensibility: How to Add New Features

I made the code modular, but realistically, adding new features requires specific changes:

### 1. Adding a New Vehicle Type (e.g., `BUS` or `ELECTRIC_CAR`)
To add a new vehicle type:
1. Add `BUS = "BUS"` to `VehicleType` enum in `src/enums/vehicle_type.py`.
2. Create a `Bus(Vehicle)` subclass in `src/models/vehicle.py`.
3. Add a branch in `VehicleFactory.create_vehicle()` to return `Bus(license_plate)`.
4. Add pricing rates for `VehicleType.BUS` in `FlatRateFeeStrategy` and `TieredFeeStrategy`.

### 2. Adding a New Fee Strategy (e.g., `WeekendSurgeFeeStrategy`)
1. Create a new class `WeekendSurgeFeeStrategy(FeeStrategy)` in `src/strategies/fee_strategy.py`.
2. Implement `calculate_fee(ticket, exit_time)`.
3. Pass it to the parking lot: `service.set_fee_strategy(WeekendSurgeFeeStrategy())`.
4. *No changes required in `ParkingLot`, `Vehicle`, or `ParkingSlot`.*

### 3. Adding a New Slot Allocation Strategy (e.g., `NearestToExitSlotStrategy`)
1. Create a new class `NearestToExitSlotStrategy(SlotAllocationStrategy)` in `src/strategies/slot_allocation_strategy.py`.
2. Implement `find_slot(floors, vehicle_type)`.
3. Pass it to the parking lot: `service.set_slot_strategy(NearestToExitSlotStrategy())`.
4. *No changes required in existing models.*

---

## How to Run the Application

### Running the Main Driver Program
From the `week-1/LLD` folder:
```bash
python src/main.py
```
Or from the project root:
```bash
python -m week-1.LLD.src.main
```

### Running the Unit Tests
From the `week-1/LLD` folder:
```bash
python -m unittest discover -s tests
```
Or directly run the test file:
```bash
python tests/test_parking_lot.py
```

---

## Sample Operations Demonstrated

1. **Adding Floors and Slots**: Two floors created with dedicated bike, car, and truck slots.
2. **View Free Slots**: Inspecting available slots by vehicle type.
3. **Park Bike, Car, and Truck**: Successful parking with ticket issuance.
4. **Occupancy Display**: Floor-by-floor breakdown of total, occupied, and free slots.
5. **Unparking and Fee Calculation**: Vacating the slot and calculating charges based on duration.
6. **Runtime Strategy Switching**: Dynamically changing from Flat Rate pricing to Tiered pricing.
7. **Edge Cases**:
   - Duplicate vehicle parking rejection.
   - Full capacity rejection.
   - Non-existent ticket handling.
   - Repeated exit rejection.
   - Unsupported vehicle type rejection.

---

## Viva / Interview Preparation

1. **Why did you use the Strategy Pattern for fee calculation?**
   - *"I used the Strategy Pattern because parking rates can change depending on promotions, time of day, or weekends. By extracting fee calculation into a strategy interface, I can swap pricing rules at runtime without modifying the ParkingLot or Ticket classes."*
2. **Why did you use the Factory Pattern for vehicles?**
   - *"I used the Factory Pattern so the service layer doesn't need if/else statements checking vehicle types. The factory handles string validation and object instantiation in one place."*
3. **How do you handle duplicate vehicle parking?**
   - *"The ParkingLot class maintains a dictionary mapping active license plates to ticket IDs. If a car with the same license plate tries to park before exiting, the system immediately rejects it."*
4. **What happens when all slots for a vehicle type are full?**
   - *"The SlotAllocationStrategy returns None. The ParkingLot detects this and raises a clear error stating that no slot is available for that vehicle type."*
5. **How does your design follow the Open/Closed Principle?**
   - *"The ParkingLot is open for extension but closed for modification. If we want a new fee formula or a new slot picking rule, we simply create a new strategy class implementing the existing interface without editing the core parking lot code."*

---

## Assumptions & Limitations

- **Assumptions**: Each parking slot holds exactly one vehicle of its designated type. Duration is calculated in hours (partial hours are rounded up with a 1-hour minimum).
- **Limitations**: The current implementation runs as an in-memory console application. In a production setting with concurrent gates, thread locks or database row locking would be required to prevent two gates from assigning the same slot at the exact same millisecond.