"""
.. include:: ../README.md
"""

import importlib.metadata as metadata
from typing import Callable

from pydantic_core import core_schema

__version__ = metadata.version(__package__ or __name__)


class PydanticAdapter[T, J]:
    """A Pydantic adapter for a custom type.

    This class allows you to use custom types with pydantic by providing functions to convert between your custom type and some JSON-compatible type, such as a string or a number.

    It is useful when you want to use a custom type in a Pydantic model and need to define how to serialize and deserialize that type.

    Example:
        ```python
        from typing import Annotated
        from pydantic import BaseModel
        from some_module import CustomType
        from pydantic_custom_type_adapter import PydanticAdapter

        CustomTypeAnnotation = Annotated[CustomType, PydanticAdapter(CustomType, parse=CustomType.parse, dump=str)]

        class MyModel(BaseModel):
            custom_field: CustomTypeAnnotation
        ```
    Args:
        type: The type of the custom object.
        parse: A function that takes a JSON value and returns an instance of the custom type. The function should raise a ValueError if the value cannot be converted to the custom type, either because it is of the wrong type entirely or because it is not a valid value for the custom type.
        dump: A function that takes an instance of the custom type and returns a JSON value. The value returned should be a valid input for the `parse` function.
    """

    def __init__(
        self, type: type[T], *, parse: Callable[[J], T], dump: Callable[[T], J]
    ) -> None:
        self._type = type
        self._parse = parse
        self._dump = dump

    def __get_pydantic_core_schema__(self, *_: object) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(self._type),
                core_schema.no_info_plain_validator_function(self._parse),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(self._dump),
        )
