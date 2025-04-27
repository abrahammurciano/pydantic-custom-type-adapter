# Pydantic Custom Types

Use any type with pydantic, without any of the hassle

## Installation

You can install this package with pip.
```sh
$ pip install pydantic-custom-type-adapter
```

## Links

[![Documentation](https://img.shields.io/badge/Documentation-C61C3E?style=for-the-badge&logo=Read+the+Docs&logoColor=%23FFFFFF)](https://abrahammurciano.github.io/pydantic-custom-type-adapter)

[![Source Code - GitHub](https://img.shields.io/badge/Source_Code-GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=%23FFFFFF)](https://github.com/abrahammurciano/pydantic-custom-type-adapter.git)

[![PyPI - pydantic-custom-type-adapter](https://img.shields.io/badge/PyPI-pydantic_custom_type_adapter-006DAD?style=for-the-badge&logo=PyPI&logoColor=%23FFD242)](https://pypi.org/project/pydantic-custom-type-adapter/)

## Usage

The `pydantic-custom-type-adapter` package provides a simple way to integrate custom types with Pydantic models through the `PydanticAdapter` class. This adapter handles serialization and deserialization of your custom types, making them fully compatible with Pydantic's validation system.

By using PydanticAdapter, you can seamlessly integrate any custom type with Pydantic's validation system, without having to modify the original type or create complex serialization logic.

### Basic usage

To use a custom type with Pydantic:

1. Import the necessary components:

```python
from typing import Annotated
from pydantic import BaseModel
from pydantic_custom_type_adapter import PydanticAdapter
```

2. Create an adapter for your custom type:

```python
from my_module import MyCustomType

# Define how to parse from JSON and dump to JSON
MyCustomTypeAnnotation = Annotated[
    MyCustomType,
    PydanticAdapter(
        type=MyCustomType,
        parse=MyCustomType.from_string,  # Convert string to MyCustomType
        dump=str  # Convert MyCustomType to string
    )
]
```
3. Use the custom type in your Pydantic model:

```python
class MyModel(BaseModel):
	custom_field: MyCustomTypeAnnotation
```

### Complete example

Here's a complete example with a custom Email type:

```python
from typing import Annotated
from pydantic import BaseModel
from pydantic_custom_type_adapter import PydanticAdapter

class Email:
    def __init__(self, address: str):
        if "@" not in address:
            raise ValueError("Invalid email address")
        self.address = address

    def __str__(self) -> str:
        return self.address

# Create the adapter
EmailType = Annotated[Email, PydanticAdapter(type=Email, parse=Email, dump=str)]

# Use in a model
class User(BaseModel):
    name: str
    email: EmailType

# Create a model instance
user = User(name="John Doe", email="john@example.com")
# or with an already constructed Email instance
user = User(name="Jane Doe", email=Email("jane@example.com"))

# Serialize to JSON
json_data = user.model_dump_json()
print(json_data)  # {"name": "John Doe", "email": "john@example.com"}

# Deserialize from JSON
user_dict = {"name": "Alice", "email": "alice@example.com"}
user = User.model_validate(user_dict)
print(user.email.address)  # alice@example.com
```

### Working with complex types

The `PydanticAdapter` also works with complex types that need custom serialization to JSON:

```python
from datetime import datetime, timezone
from typing import Annotated, Any, Self

from pydantic import BaseModel
from pydantic_custom_type_adapter import PydanticAdapter

class Timestamp:
    def __init__(self, dt: datetime):
        self.datetime = dt

    @classmethod
    def parse(cls, data: dict[str, Any]) -> Self:
        return cls(datetime.fromisoformat(data["iso"]))

    def to_dict(self) -> dict[str, Any]:
        return {
            "iso": self.datetime.isoformat(),
            "unix": int(self.datetime.timestamp())
        }

# Create the adapter with dict serialization
TimestampType = Annotated[
    Timestamp,
    PydanticAdapter(
        type=Timestamp,
        parse=Timestamp.parse,
        dump=lambda ts: ts.to_dict()
    )
]

class Event(BaseModel):
    name: str
    timestamp: TimestampType

# Create and use the model
event = Event(
    name="Server Started",
    timestamp=Timestamp(datetime.now(timezone.utc))
)

# Serialize to JSON - timestamp will be a dictionary with iso and unix fields
json_data = event.model_dump_json()
print(json_data)
```

### Multiple adapters for different contexts

You can create multiple annotations for the same type to handle different serialization formats:

```python
from typing import Annotated, Self
from pydantic import BaseModel
from pydantic_custom_type_adapter import PydanticAdapter

class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @classmethod
    def from_string(cls, value: str) -> Self:
        x, y = map(float, value.split(","))
        return cls(x, y)

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        return cls(data["x"], data["y"])

    def to_string(self) -> str:
        return f"{self.x},{self.y}"

    def to_dict(self) -> dict:
        return {"x": self.x, "y": self.y}

# String representation adapter
PointString = Annotated[
    Point,
    PydanticAdapter(
        type=Point,
        parse=Point.from_string,
        dump=lambda p: p.to_string()
    )
]

# Dictionary representation adapter
PointDict = Annotated[
    Point,
    PydanticAdapter(
        type=Point,
        parse=Point.from_dict,
        dump=lambda p: p.to_dict()
    )
]

# Use different representations in different models
class LocationString(BaseModel):
    position: PointString

class LocationDict(BaseModel):
    position: PointDict
```