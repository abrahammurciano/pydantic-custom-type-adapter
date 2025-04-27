import datetime
from typing import Any, Self


class Timestamp:
    """Custom Timestamp type for testing the PydanticAdapter."""

    def __init__(self, dt: datetime.datetime):
        self.datetime = dt

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timestamp):
            return False
        return self.datetime == other.datetime

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        return cls(datetime.datetime.fromisoformat(data["iso"]))

    def to_dict(self) -> dict[str, Any]:
        return {
            "iso": self.datetime.isoformat(),
            "unix": int(self.datetime.timestamp()),
        }
