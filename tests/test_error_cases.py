from typing import Annotated

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_custom_type_adapter import PydanticAdapter
from tests.custom_types import Email


def failing_parse(_: str) -> int:
    raise ValueError("This parse function always fails")


FailingType = Annotated[int, PydanticAdapter(type=int, parse=failing_parse, dump=str)]


def test_invalid_parse_function() -> None:
    """Test behavior when parse function raises exception other than ValueError."""

    class FailModel(BaseModel):
        field: FailingType

    with pytest.raises(ValidationError):
        FailModel.model_validate({"field": "123"})


EmailType = Annotated[Email, PydanticAdapter(type=Email, parse=Email.parse, dump=str)]


def test_none_handling() -> None:
    """Test handling of None values with Optional fields."""

    class OptionalModel(BaseModel):
        email: EmailType | None = None

    # None default
    model = OptionalModel()
    assert model.email is None

    # Explicit None
    model = OptionalModel(email=None)
    assert model.email is None

    # With value
    model = OptionalModel.model_validate({"email": "test@example.com"})
    assert isinstance(model.email, Email)
    assert model.email == Email("test@example.com")


def test_list_of_custom_types() -> None:
    """Test using lists of custom types."""

    class EmailList(BaseModel):
        emails: list[EmailType]

    # Create from strings
    model = EmailList.model_validate(
        {"emails": ["one@example.com", "two@example.com", "three@example.com"]}
    )
    assert all(isinstance(c, Email) for c in model.emails)
    assert [c.address for c in model.emails] == [
        "one@example.com",
        "two@example.com",
        "three@example.com",
    ]

    # Create from instances
    emails = [Email("four@example.com"), Email("five@example.com")]
    model = EmailList(emails=emails)
    assert model.emails == emails

    # Serialize
    model_dict = model.model_dump()
    assert model_dict == {"emails": ["four@example.com", "five@example.com"]}

    # Deserialize
    model = EmailList.model_validate(
        {"emails": ["six@example.com", "seven@example.com"]}
    )
    assert [c.address for c in model.emails] == ["six@example.com", "seven@example.com"]


def test_dict_with_custom_types() -> None:
    """Test using dictionaries with custom type values."""

    class EmailMap(BaseModel):
        mapping: dict[str, EmailType]

    # Create from strings
    model = EmailMap.model_validate(
        {"mapping": {"primary": "main@example.com", "secondary": "other@example.com"}}
    )
    assert all(isinstance(c, Email) for c in model.mapping.values())
    assert model.mapping["primary"] == Email.parse("main@example.com")
    assert model.mapping["secondary"] == Email.parse("other@example.com")

    # Create from instances
    mapping = {"primary": Email("one@example.com")}
    model = EmailMap(mapping=mapping)
    assert model.mapping["primary"] is mapping["primary"]

    # Serialize
    model_dict = model.model_dump()
    assert model_dict == {"mapping": {"primary": "one@example.com"}}

    # Deserialize
    model = EmailMap.model_validate({"mapping": {"primary": "two@example.com"}})
    assert model.mapping["primary"] == Email.parse("two@example.com")


def test_nesting() -> None:
    """Test nesting PydanticAdapter types."""

    class User(BaseModel):
        email: EmailType

    class WrapperModel(BaseModel):
        user: User

    # Create nested model
    wrapper = WrapperModel(user=User(email=Email("test@example.com")))

    # Verify types
    assert isinstance(wrapper.user.email, Email)
    assert wrapper.user.email.address == "test@example.com"

    # Serialize
    nested_dict = wrapper.model_dump()
    assert nested_dict == {"user": {"email": "test@example.com"}}

    # Deserialize
    nested_data = {"user": {"email": "test@example.com"}}
    wrapper = WrapperModel.model_validate(nested_data)
    assert wrapper.user.email.address == "test@example.com"
