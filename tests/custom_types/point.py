from dataclasses import dataclass
from typing import Self


@dataclass
class Point:
    """Custom Point type for testing the PydanticAdapter."""

    x: float
    y: float

    @classmethod
    def from_string(cls, value: str) -> Self:
        x, y = map(float, value.split(","))
        return cls(x, y)

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Self:
        try:
            return cls(data["x"], data["y"])
        except KeyError:
            raise ValueError("Invalid point dictionary format")

    def to_string(self) -> str:
        return f"{self.x},{self.y}"

    def to_dict(self) -> dict[str, float]:
        return {"x": self.x, "y": self.y}
