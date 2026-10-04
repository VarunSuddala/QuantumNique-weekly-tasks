# UML Class Diagram & Relationship Documentation

This document describes the Object-Oriented design and relationships for the **Extensible Multi-Floor Parking Lot System**.

---

## Mermaid Class Diagram

```mermaid
classDiagram
    %% Core Enums
    class VehicleType {
        <<enumeration>>
        BIKE
        CAR
        TRUCK
        +from_string(value) VehicleType
    }

    class SlotStatus {
        <<enumeration>>
        AVAILABLE
        OCCUPIED
    }

    class TicketStatus {
        <<enumeration>>
        ACTIVE
        COMPLETED
    }

    %% Vehicle Hierarchy (Polymorphism)
    class Vehicle {
        <<abstract>>
        +str license_plate
        +VehicleType vehicle_type
    }

    class Bike {
        +Bike(license_plate)
    }

    class Car {
        +Car(license_plate)
    }

    class Truck {
        +Truck(license_plate)
    }

    Vehicle <|-- Bike
    Vehicle <|-- Car
    Vehicle <|-- Truck
    Vehicle --> VehicleType

    %% Factory Pattern
    class VehicleFactory {
        +create_vehicle(type_str, license_plate) Vehicle
    }
    VehicleFactory ..> Vehicle : instantiates

    %% Slot & Floor Models
    class ParkingSlot {
        +str slot_id
        +int floor_number
        +VehicleType supported_type
        +SlotStatus status
        +Vehicle current_vehicle
        +is_available() bool
        +can_fit_vehicle(vehicle) bool
        +assign_vehicle(vehicle) void
        +vacate() Vehicle
    }
    ParkingSlot --> SlotStatus
    ParkingSlot --> VehicleType
    ParkingSlot o-- Vehicle : contains

    class ParkingFloor {
        +int floor_number
        +dict slots
        +add_slot(slot) void
        +get_slot(slot_id) ParkingSlot
        +get_available_slots(type) List~ParkingSlot~
        +get_occupancy() dict
    }
    ParkingFloor *-- ParkingSlot : contains multiple

    %% Ticket Model
    class Ticket {
        +str ticket_id
        +Vehicle vehicle
        +int floor_number
        +str slot_id
        +datetime entry_time
        +datetime exit_time
        +float fee
        +TicketStatus status
        +is_active() bool
        +close(exit_time, fee) void
    }
    Ticket --> TicketStatus
    Ticket o-- Vehicle

    %% Strategy Pattern: Fee Strategy
    class FeeStrategy {
        <<interface>>
        +calculate_fee(ticket, exit_time)* float
    }

    class FlatRateFeeStrategy {
        +dict hourly_rates
        +calculate_fee(ticket, exit_time) float
    }

    class TieredFeeStrategy {
        +dict tiered_rates
        +calculate_fee(ticket, exit_time) float
    }

    FeeStrategy <|.. FlatRateFeeStrategy
    FeeStrategy <|.. TieredFeeStrategy

    %% Strategy Pattern: Slot Allocation Strategy
    class SlotAllocationStrategy {
        <<interface>>
        +find_slot(floors, vehicle_type)* ParkingSlot
    }

    class LowestFloorSlotStrategy {
        +find_slot(floors, vehicle_type) ParkingSlot
    }

    class HighFloorFirstStrategy {
        +find_slot(floors, vehicle_type) ParkingSlot
    }

    SlotAllocationStrategy <|.. LowestFloorSlotStrategy
    SlotAllocationStrategy <|.. HighFloorFirstStrategy

    %% Central ParkingLot Model
    class ParkingLot {
        +str lot_id
        +str name
        +dict floors
        +dict active_tickets
        +dict parked_plates
        +SlotAllocationStrategy slot_strategy
        +FeeStrategy fee_strategy
        +set_slot_strategy(strategy) void
        +set_fee_strategy(strategy) void
        +add_floor(floor) void
        +park_vehicle(vehicle) Ticket
        +unpark_vehicle(ticket_id, exit_time) Tuple
        +get_free_slots(type) List~ParkingSlot~
        +get_occupancy() dict
    }
    ParkingLot *-- ParkingFloor : contains
    ParkingLot o-- Ticket : tracks active
    ParkingLot --> SlotAllocationStrategy : delegates to
    ParkingLot --> FeeStrategy : delegates to

    %% Service Layer
    class ParkingLotService {
        +ParkingLot parking_lot
        +add_floor(floor_number) void
        +add_slot(floor, slot_id, type) void
        +park_vehicle(type_str, plate) Ticket
        +unpark_vehicle(ticket_id, exit_time) Tuple
        +view_free_slots(type_str) List
        +display_occupancy() dict
        +set_fee_strategy(strategy) void
        +set_slot_strategy(strategy) void
    }
    ParkingLotService --> ParkingLot : coordinates
    ParkingLotService ..> VehicleFactory : uses
```

---

## Real Code Relationships Explained

Every relationship in the diagram directly maps to a line of code:

1. **`ParkingLot` *-- `ParkingFloor` (Composition)**:
   - A parking lot owns its floors (`self.floors = {}`).
   - If the parking lot is destroyed, the floors cease to exist as parking entities.

2. **`ParkingFloor` *-- `ParkingSlot` (Composition)**:
   - A floor owns its designated slots (`self.slots = {}`).

3. **`ParkingSlot` o-- `Vehicle` (Aggregation)**:
   - A slot holds a reference to a parked vehicle (`self.current_vehicle`).
   - When the vehicle unparks, the vehicle continues to exist independently of the slot.

4. **`ParkingLot` o-- `Ticket` (Aggregation)**:
   - The parking lot maintains active tickets in `self.active_tickets`.
   - Tickets exist as historical records even after a vehicle unparks.

5. **`ParkingLot` --> `SlotAllocationStrategy` (Strategy Pattern)**:
   - The parking lot holds an instance of `SlotAllocationStrategy`.
   - When parking, it delegates the search for a free slot to `self.slot_strategy.find_slot(...)`.

6. **`ParkingLot` --> `FeeStrategy` (Strategy Pattern)**:
   - The parking lot holds an instance of `FeeStrategy`.
   - When unparking, it delegates pricing calculations to `self.fee_strategy.calculate_fee(...)`.

7. **`Bike`, `Car`, `Truck` --|> `Vehicle` (Inheritance & Polymorphism)**:
   - Subclasses inherit from the abstract base class `Vehicle` and set their specific `VehicleType`.

8. **`VehicleFactory` ..> `Vehicle` (Factory Pattern / Dependency)**:
   - `VehicleFactory.create_vehicle(...)` instantiates the correct subclass without leaking instantiation details to the service.

9. **`ParkingLotService` --> `ParkingLot` (Dependency / Coordination)**:
   - The service wraps business operations and provides a clean API for the driver and external callers.
