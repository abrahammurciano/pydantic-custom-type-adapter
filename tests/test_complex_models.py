import datetime
import uuid
from typing import Annotated, Any

from pydantic import BaseModel

from pydantic_custom_type_adapter import PydanticAdapter
from tests.custom_types import Email, Point, Timestamp

EmailType = Annotated[Email, PydanticAdapter(type=Email, parse=Email.parse, dump=str)]

PointDictType = Annotated[
    Point,
    PydanticAdapter(type=Point, parse=Point.from_dict, dump=lambda p: p.to_dict()),
]

TimestampType = Annotated[
    Timestamp,
    PydanticAdapter(
        type=Timestamp, parse=Timestamp.parse, dump=lambda ts: ts.to_dict()
    ),
]


def test_complex_model(test_uuid: uuid.UUID, utc_now: datetime.datetime) -> None:
    """Test a more complex model with multiple custom types."""

    class ComplexModel(BaseModel):
        id: uuid.UUID
        name: str
        email: EmailType
        location: PointDictType
        timestamp: TimestampType
        metadata: dict[str, Any]
        tags: list[str]
        optional_field: EmailType | None = None

    test_email = Email("test@example.com")
    test_point = Point(10.0, 20.0)
    test_time = utc_now
    test_timestamp = Timestamp(test_time)

    # Create complex model
    model = ComplexModel(
        id=test_uuid,
        name="Complex Test",
        email=test_email,
        location=test_point,
        timestamp=test_timestamp,
        metadata={"version": "1.0", "active": True},
        tags=["test", "example"],
    )

    # Check types
    assert isinstance(model.email, Email)
    assert isinstance(model.location, Point)
    assert isinstance(model.timestamp, Timestamp)

    # Serialize
    model_dict = model.model_dump()
    assert str(model_dict["id"]) == str(test_uuid)
    assert model_dict["email"] == "test@example.com"
    assert model_dict["location"] == {"x": 10.0, "y": 20.0}
    assert model_dict["timestamp"]["iso"] == test_time.isoformat()

    # Deserialize
    json_data = {
        "id": str(test_uuid),
        "name": "Complex Test From JSON",
        "email": "json@example.com",
        "location": {"x": 15.0, "y": 25.0},
        "timestamp": {
            "iso": test_time.isoformat(),
            "unix": int(test_time.timestamp()),
        },
        "metadata": {"version": "2.0", "active": False},
        "tags": ["json", "test"],
    }
    model = ComplexModel.model_validate(json_data)
    assert str(model.id) == str(test_uuid)
    assert model.email.address == "json@example.com"
    assert model.location.x == 15.0
    assert model.location.y == 25.0
    assert model.timestamp.datetime.isoformat() == test_time.isoformat()


def test_optional_fields() -> None:
    """Test optional fields with custom types."""

    # Define model in the test
    class ComplexModel(BaseModel):
        id: uuid.UUID
        name: str
        email: EmailType
        location: PointDictType
        timestamp: TimestampType
        metadata: dict[str, Any]
        tags: list[str]
        optional_field: EmailType | None = None

    # Without optional field
    model = ComplexModel.model_validate(
        {
            "id": uuid.uuid4(),
            "name": "Optional Test",
            "email": "test@example.com",
            "location": {"x": 10.0, "y": 20.0},
            "timestamp": {
                "iso": datetime.datetime.now(datetime.timezone.utc).isoformat()
            },
            "metadata": {},
            "tags": [],
        }
    )
    assert model.optional_field is None

    # With optional field
    model = ComplexModel.model_validate(
        {
            "id": uuid.uuid4(),
            "name": "Optional Test",
            "email": "test@example.com",
            "location": {"x": 10.0, "y": 20.0},
            "timestamp": {
                "iso": datetime.datetime.now(datetime.timezone.utc).isoformat()
            },
            "metadata": {},
            "tags": [],
            "optional_field": "optional@example.com",
        }
    )
    assert isinstance(model.optional_field, Email)
    assert model.optional_field.address == "optional@example.com"
