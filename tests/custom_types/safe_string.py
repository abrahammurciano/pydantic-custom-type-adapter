from typing import Self


class SafeString:
    """Custom SafeString type for testing the PydanticAdapter."""

    def __init__(self, value: str):
        if not value.isalnum():
            raise ValueError("String must be alphanumeric")
        self.value = value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SafeString):
            return False
        return self.value == other.value

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)
