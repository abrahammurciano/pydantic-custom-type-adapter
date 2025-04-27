from typing import Annotated

from pydantic import BaseModel

from pydantic_custom_types import PydanticAdapter
from tests.custom_types import Point, Timestamp

# Define annotated types directly in the file
PointStringType = Annotated[
    Point,
    PydanticAdapter(type=Point, parse=Point.from_string, dump=lambda p: p.to_string()),
]

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


def test_string_serialization():
    """Test string serialization of custom types."""

    # Define model in the test
    class LocationString(BaseModel):
        name: str
        position: PointStringType

    # String representation
    location = LocationString.model_validate({"name": "Home", "position": "10.5,20.3"})
    assert isinstance(location.position, Point)
    assert location.position.x == 10.5
    assert location.position.y == 20.3

    # Serialize
    location_dict = location.model_dump()
    assert location_dict == {"name": "Home", "position": "10.5,20.3"}

    # Deserialize
    location_data = {"name": "Work", "position": "5.1,3.2"}
    location = LocationString.model_validate(location_data)
    assert isinstance(location.position, Point)
    assert location.position.x == 5.1
    assert location.position.y == 3.2


def test_dict_serialization():
    """Test dictionary serialization of custom types."""

    # Define model in the test
    class LocationDict(BaseModel):
        name: str
        position: PointDictType

    # Dict representation
    location = LocationDict.model_validate(
        {"name": "Home", "position": {"x": 10.5, "y": 20.3}}
    )
    assert isinstance(location.position, Point)
    assert location.position.x == 10.5
    assert location.position.y == 20.3

    # Serialize
    location_dict = location.model_dump()
    assert location_dict == {"name": "Home", "position": {"x": 10.5, "y": 20.3}}

    # Deserialize
    location_data = {"name": "Work", "position": {"x": 5.1, "y": 3.2}}
    location = LocationDict.model_validate(location_data)
    assert isinstance(location.position, Point)
    assert location.position.x == 5.1
    assert location.position.y == 3.2


def test_complex_type_serialization(utc_now):
    """Test complex type with custom dictionary serialization."""

    # Define model in the test
    class Event(BaseModel):
        name: str
        timestamp: TimestampType

    # Create timestamp
    now = utc_now
    timestamp = Timestamp(now)
    event = Event(name="Server Start", timestamp=timestamp)

    # Verify type
    assert isinstance(event.timestamp, Timestamp)
    assert event.timestamp.datetime == now

    # Serialize
    event_dict = event.model_dump()
    assert event_dict["name"] == "Server Start"
    assert event_dict["timestamp"]["iso"] == now.isoformat()
    assert event_dict["timestamp"]["unix"] == int(now.timestamp())

    # Deserialize
    event_data = {
        "name": "Server Stop",
        "timestamp": {"iso": now.isoformat(), "unix": int(now.timestamp())},
    }
    event = Event.model_validate(event_data)
    assert isinstance(event.timestamp, Timestamp)
    assert event.timestamp.datetime.isoformat() == now.isoformat()
