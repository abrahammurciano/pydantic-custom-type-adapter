# Test with recursive structures
from typing import Any, Dict, Self, Sequence


class TreeNode:
    def __init__(self, value: str, children: Sequence[Self] | None = None):
        self.value = value
        self.children = children or []

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TreeNode):
            return False
        return self.value == other.value and self.children == other.children

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Self:
        children = [cls.from_dict(child) for child in data.get("children", [])]
        return cls(data["value"], children)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "value": self.value,
            "children": [child.to_dict() for child in self.children],
        }
