from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
import re
import json
from urllib.parse import urlparse
from enum import Enum
from datetime import datetime, date
from .model import ExternalFilter
from ...json_serialized import JsonSerializableMixin

class BaseFieldComponent(BaseModel, JsonSerializableMixin):
    """Base component for field-related models"""

    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)


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


class BaseUpsertChartRequest(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    width: int = Field(default=50, description="Width of the chart")
    filters: Optional[List[ExternalFilter]] = Field(
        default=None, description="Filters for the chart"
    )
