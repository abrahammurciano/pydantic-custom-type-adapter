from typing import Self


class Email:
    """Custom Email type for testing the PydanticAdapter."""

    def __init__(self, address: str):
        if "@" not in address:
            raise ValueError("Invalid email address")
        self.address = address

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Email):
            return False
        return self.address == other.address

    def __str__(self) -> str:
        return self.address

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)