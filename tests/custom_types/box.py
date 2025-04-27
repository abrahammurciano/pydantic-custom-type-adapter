from dataclasses import dataclass


@dataclass
class Box[T]:
    value: T
