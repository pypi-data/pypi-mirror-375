from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re
import json
from urllib.parse import urlparse
from ...json_serialized import JsonSerializableMixin



class ValidatedString(str):
    """Custom string type with common validation patterns"""

    @classmethod
    def field_name_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Field name cannot be empty")
            v = v.strip()
            if not re.match(r"^[_a-z][\d_a-z]*$", v):
                raise ValueError(
                    "Field name must start with letter/underscore and contain only lowercase letters, numbers, underscore"
                )
        return v

    @classmethod
    def non_empty_string_validator(
        cls, v: Optional[str], field_name: str = "Field"
    ) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError(f"{field_name} cannot be empty")
        return v.strip() if v else v

    @classmethod
    def url_validator(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("URL is required")
        v = v.strip()
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Must be a valid URL")
        except Exception:
            raise ValueError("Must be a valid URL")
        return v

    @classmethod
    def json_string_validator(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Must be valid JSON string")
        return v


class UniqueListValidator:
    """Validator for ensuring list uniqueness"""

    @classmethod
    def validate_unique_strings(
        cls, v: Optional[List[str]], field_name: str = "Items"
    ) -> Optional[List[str]]:
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError(f"{field_name} must be unique")
            for item in v:
                if not item or not item.strip():
                    raise ValueError(f"{field_name} cannot contain empty values")
        return v


class BaseFieldComponent(BaseModel, JsonSerializableMixin):
    """Base component for field-related models"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


"""
    For this class we need to provide the extra things
    In case of add 
    app_id
    pade_index      
    section_index
    field_index
    field_type
    field_name

    In case of update
    app_id
    field_name
    newFieldName (if field name need to change)
"""


class BaseUpsertFieldRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    label: str = Field(description="Display label for the field")
    description: Optional[str] = Field(
        None,
        description="Field description, Example: This is a description for the field",
    )
    placeholder: Optional[str] = Field(None, description="Field placeholder")
    dependency_app_id: Optional[str] = Field(
        None, description="Dependency app ID, must be a valid Clappia app ID"
    )
    server_url: Optional[str] = Field(
        None, description="Server URL, mandatory if field type is getDataFromRestApis"
    )
    display_condition: Optional[str] = Field(
        None, description="Display condition Example: {field_name} == 'value'"
    )
    required: bool = Field(default=False, description="Whether field is required")
    hidden: bool = Field(default=False, description="Whether field is hidden")
    is_editable: bool = Field(default=True, description="Whether field is editable")
    editability_condition: Optional[str] = Field(
        None, description="Editability condition, Example: {field_name} == 'value'"
    )
    default_value: Optional[str] = Field(
        None, description="Default value, Example: 'value'"
    )
    width: int = Field(default=100, description="Desktop width")
    mobile_width: int = Field(default=100, description="Mobile width")
    retain_values: bool = Field(default=True, description="Retain values when hidden")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "Label")


class BaseUpsertPageRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    app_id: str = Field(description="App ID")

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "App ID")


class BaseUpsertSectionRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    app_id: str = Field(description="App ID")
    section_index: int = Field(ge=0, description="Section index")
    page_index: int = Field(ge=0, description="Page index")

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "App ID")
