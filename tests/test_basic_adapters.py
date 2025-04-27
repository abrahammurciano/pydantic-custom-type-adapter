from typing import Annotated

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_custom_type_adapter import PydanticAdapter
from tests.custom_types import Email, Point, SafeString, UserId

# Define annotated types directly in the file
EmailType = Annotated[Email, PydanticAdapter(type=Email, parse=Email.parse, dump=str)]


def test_email_adapter() -> None:
    """Test the basic functionality of Email adapter."""

    class User(BaseModel):
        name: str
        email: EmailType

    # Create from string
    user = User.model_validate({"name": "John Doe", "email": "john@example.com"})
    assert isinstance(user.email, Email)
    assert user.email.address == "john@example.com"

    # Create from instance
    email = Email("jane@example.com")
    user = User(name="Jane Doe", email=email)
    assert user.email == email

    # Serialize to dict
    user_dict = user.model_dump()
    assert user_dict == {"name": "Jane Doe", "email": "jane@example.com"}

    # Deserialize from dict
    user_data = {"name": "Alice", "email": "alice@example.com"}
    user = User.model_validate(user_data)
    assert isinstance(user.email, Email)
    assert user.email.address == "alice@example.com"


UserIdType = Annotated[
    UserId, PydanticAdapter(type=UserId, parse=UserId.parse, dump=lambda uid: uid.id)
]


def test_integer_adapter() -> None:
    """Test adapter with integer values."""

    # Define model in the test
    class User(BaseModel):
        name: str
        email: EmailType
        id: UserIdType

    # Create from int
    user = User.model_validate(
        {"name": "John Doe", "email": "john@example.com", "id": 1}
    )
    assert isinstance(user.id, UserId)
    assert user.id.id == 1

    # Create from instance
    user_id = UserId(2)
    user = User.model_validate(
        {"name": "Jane Doe", "email": "jane@example.com", "id": user_id}
    )
    assert user.id == user_id

    # Serialize to dict
    user_dict = user.model_dump()
    assert user_dict == {"name": "Jane Doe", "email": "jane@example.com", "id": 2}

    # Deserialize from dict
    user_data = {"name": "Alice", "email": "alice@example.com", "id": 3}
    user = User.model_validate(user_data)
    assert isinstance(user.id, UserId)
    assert user.id.id == 3


PointStringType = Annotated[
    Point,
    PydanticAdapter(type=Point, parse=Point.from_string, dump=lambda p: p.to_string()),
]

PointDictType = Annotated[
    Point,
    PydanticAdapter(type=Point, parse=Point.from_dict, dump=lambda p: p.to_dict()),
]

SafeStringType = Annotated[
    SafeString,
    PydanticAdapter(type=SafeString, parse=SafeString.parse, dump=lambda s: s.value),
]


def test_validation_errors() -> None:
    """Test validation errors are raised correctly."""

    # Define models in the test
    class User(BaseModel):
        name: str
        email: EmailType
        id: UserIdType

    class Form(BaseModel):
        username: SafeStringType

    class LocationString(BaseModel):
        name: str
        position: PointStringType

    class LocationDict(BaseModel):
        name: str
        position: PointDictType

    # Invalid email
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate({"name": "John Doe", "email": "invalid-email", "id": 1})
    assert "Invalid email address" in str(exc_info.value)

    # Invalid user ID
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate({"name": "John Doe", "email": "john@example.com", "id": -1})
    assert "User ID must be positive" in str(exc_info.value)

    # Invalid safe string
    with pytest.raises(ValidationError) as exc_info:
        Form.model_validate({"username": "user@123!"})
    assert "String must be alphanumeric" in str(exc_info.value)

    # Invalid point string format
    with pytest.raises(ValidationError):
        LocationString.model_validate({"name": "Test", "position": "invalid"})

    # Invalid point dict format
    with pytest.raises(ValidationError):
        LocationDict.model_validate(
            {"name": "Test", "position": {"x": 10}}
        )  # missing y


def test_instance_passthrough() -> None:
    """Test that instance objects are passed through without calling parse."""

    # Define model in the test
    class User(BaseModel):
        name: str
        email: EmailType

    # Create from instance
    email = Email("test@example.com")
    user = User(name="Test User", email=email)
    assert user.email is email
