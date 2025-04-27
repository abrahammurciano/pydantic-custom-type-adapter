from typing import Annotated

import pytest
from pydantic import BaseModel, TypeAdapter

from pydantic_custom_types import PydanticAdapter
from tests.custom_types import Box, Coordinates, TreeNode
from tests.custom_types.email import Email

StringBoxType = Annotated[
    Box[str],
    PydanticAdapter(type=Box, parse=Box, dump=lambda b: b.value),
]

IntBoxType = Annotated[
    Box[int],
    PydanticAdapter(type=Box, parse=Box, dump=lambda b: b.value),
]


def test_generic_types() -> None:
    """Test using generic types with PydanticAdapter."""

    class BoxContainer(BaseModel):
        string_box: StringBoxType
        int_box: IntBoxType

    # Create containers
    container = BoxContainer.model_validate({"string_box": "Hello", "int_box": 42})
    assert isinstance(container.string_box, Box)
    assert isinstance(container.int_box, Box)
    assert container.string_box.value == "Hello"
    assert container.int_box.value == 42

    # Serialize
    container_dict = container.model_dump()
    assert container_dict == {"string_box": "Hello", "int_box": 42}

    # Deserialize
    container_data = {"string_box": "World", "int_box": 123}
    container = BoxContainer.model_validate(container_data)
    assert container.string_box.value == "World"
    assert container.int_box.value == 123


CoordinatesType = Annotated[
    Coordinates,
    PydanticAdapter(
        type=Coordinates,
        parse=Coordinates.from_string,
        dump=lambda c: c.to_string(),
    ),
]


def test_frozen_dataclass() -> None:
    """Test using frozen dataclasses with PydanticAdapter."""

    class Location(BaseModel):
        name: str
        coordinates: CoordinatesType

    # Create from string
    location = Location.model_validate(
        {"name": "Home", "coordinates": "42.1234,-71.5678"}
    )
    assert isinstance(location.coordinates, Coordinates)
    assert location.coordinates.lat == 42.1234
    assert location.coordinates.lng == -71.5678

    # Create from instance
    coords = Coordinates(37.7749, -122.4194)
    location = Location(name="San Francisco", coordinates=coords)
    assert location.coordinates is coords

    # Serialize
    location_dict = location.model_dump()
    assert location_dict == {
        "name": "San Francisco",
        "coordinates": "37.7749,-122.4194",
    }

    # Deserialize
    location_data = {"name": "New York", "coordinates": "40.7128,-74.006"}
    location = Location.model_validate(location_data)
    assert location.coordinates.lat == 40.7128
    assert location.coordinates.lng == -74.006


TreeNodeType = Annotated[
    TreeNode,
    PydanticAdapter(
        type=TreeNode, parse=TreeNode.from_dict, dump=lambda t: t.to_dict()
    ),
]


def test_recursive_structures() -> None:
    """Test using recursive structures with PydanticAdapter."""

    class Tree(BaseModel):
        root: TreeNodeType

    # Create tree
    tree_node = TreeNode(
        "root", [TreeNode("child1"), TreeNode("child2", [TreeNode("grandchild")])]
    )
    tree = Tree(root=tree_node)
    assert tree.root is tree_node

    # Serialize
    tree_dict = tree.model_dump()
    expected = {
        "root": {
            "value": "root",
            "children": [
                {"value": "child1", "children": []},
                {
                    "value": "child2",
                    "children": [{"value": "grandchild", "children": []}],
                },
            ],
        }
    }
    assert tree_dict == expected

    # Deserialize
    tree = Tree.model_validate(tree_dict)
    assert tree.root.value == "root"
    assert len(tree.root.children) == 2
    assert tree.root.children[0].value == "child1"
    assert tree.root.children[1].value == "child2"
    assert tree.root.children[1].children[0].value == "grandchild"


EmailType = Annotated[
    Email,
    PydanticAdapter(type=Email, parse=Email.parse, dump=str),
]


def test_type_adapter() -> None:
    """Test PydanticAdapter working with TypeAdapter."""

    class User(BaseModel):
        email: EmailType

    adapter = TypeAdapter(User)

    user = adapter.validate_python({"email": "test@example.com"})
    assert isinstance(user.email, Email)
    assert user.email.address == "test@example.com"
    assert user.model_dump() == {"email": "test@example.com"}

    with pytest.raises(ValueError):
        adapter.validate_python({"email": "invalid-email"})
