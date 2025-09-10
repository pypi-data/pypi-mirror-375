from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re
import json
from urllib.parse import urlparse
from ...json_serialized import JsonSerializableMixin


class ValidatedString(str):
    """Custom string type with common validation patterns"""

    @classmethod
    def non_empty_string_validator(
        cls, v: Optional[str], field_name: str = "Field"
    ) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError(f"{field_name} cannot be empty")
        return v.strip() if v else v

    @classmethod
    def number_validator(
        cls, v: Optional[int], field_name: str = "Field"
    ) -> Optional[int]:
        if v is not None and (not v or not v.strip()):
            raise ValueError(f"{field_name} cannot be empty")
        return v.strip() if v else v


class BaseUpsertWorkflowStepRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    name: str = Field(description="Name of the workflow step")
    field_name: Optional[str] = Field(
        None, description="Field name of the workflow step"
    )
    enabled: bool = Field(
        default=True, description="Whether the workflow step is enabled"
    )
    public_urls_expiry: int = Field(default=-1, description="Public URLs expiry")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return ValidatedString.non_empty_string_validator(v, "Name")
