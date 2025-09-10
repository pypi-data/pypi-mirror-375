from typing import Literal
from pydantic import Field, field_validator
from .base import BaseFieldComponent, ValidatedString


class RestApiOutputField(BaseFieldComponent):
    name: str = Field(min_length=1, description="Name of the output field")
    data_type: Literal["textInput", "file", "textArea"] = Field(
        description="Data type of the output field"
    )
    json_path_query: str = Field(description="JSON path query for extracting data")
    x_path_query: str = Field(description="XPath query for extracting data")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "Name")


class SortField(BaseFieldComponent):
    sort_by: str = Field(min_length=1, description="Field name to sort by")
    sort_direction: Literal["asc", "desc"] = Field(description="Sort direction")

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "Sort by field name")


class FilterField(BaseFieldComponent):
    key: str = Field(
        min_length=1, description="Filter key field name, Example: 'field_name'"
    )
    value: str = Field(description="Filter value, Example: 'value'")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "Filter key")
