# Test with dataclasses and frozen objects
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lng: float

    @classmethod
    def from_string(cls, value: str) -> Self:
        lat, lng = map(float, value.split(","))
        return cls(lat, lng)

    def to_string(self) -> str:
        return f"{self.lat},{self.lng}"
