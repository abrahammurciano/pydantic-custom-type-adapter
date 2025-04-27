from typing import Self


class UserId:
    """Custom UserId type for testing the PydanticAdapter."""

    def __init__(self, id: int):
        if id <= 0:
            raise ValueError("User ID must be positive")
        self.id = id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserId):
            return False
        return self.id == other.id

    @classmethod
    def parse(cls, value: int) -> Self:
        return cls(value)
