from enum import Enum

class VehicleType(Enum):
    BIKE = "BIKE"
    CAR = "CAR"
    TRUCK = "TRUCK"

    @classmethod
    def from_string(cls, value: str):
        try:
            return cls[value.upper()]
        except KeyError:
            valid_types = ", ".join([t.value for t in cls])
            raise ValueError(f"Invalid vehicle type '{value}'. Supported types are: {valid_types}.")
