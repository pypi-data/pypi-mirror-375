from typing import Optional, List, Dict, Any, Literal
from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_validator,
    ValidationInfo,
    model_validator,
)
import re
from clappia_api_tools.models.permissions import Permission
from clappia_api_tools.utils.utils import Utils

utils = Utils()


class BaseWorkplaceRequest(BaseModel):
    """Base class for workplace request models with common fields"""

    email_address: EmailStr = Field(
        None,
        description="Email address of the user, only one of email or phone number is required",
    )
    phone_number: Optional[str] = Field(
        None,
        description="Phone number of the user, only one of email or phone number is required",
    )

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return utils.validate_phone_number(v)
        return v

    @model_validator(mode="after")
    @classmethod
    def validate_contact_method(cls, value: str, info: ValidationInfo) -> str:
        if isinstance(info.context, dict):
            """Ensure exactly one contact method is provided"""
            email_address = info.data.get("email_address")
            phone_number = info.data.get("phone_number")

            if not email_address and not phone_number:
                raise ValueError(
                    "One of parameter 'emailAddress' or 'phoneNumber' must be present in the input."
                )
            if email_address and phone_number:
                raise ValueError(
                    "Only one of parameter 'emailAddress' or 'phoneNumber' must be present in the input."
                )
        return value


class AddUserToWorkplaceRequest(BaseWorkplaceRequest):
    """Request model for adding a user to workplace"""

    first_name: str = Field(default="", description="First name of the user")
    last_name: str = Field(default="", description="Last name of the user")
    group_names: List[str] = Field(
        default_factory=list, description="List of group names"
    )
    attributes: Dict[str, str] = Field(
        default_factory=dict, description="User attributes"
    )

    @field_validator("group_names")
    @classmethod
    def validate_group_names(cls, v: List[str]) -> List[str]:
        if v:
            unique_groups = list(
                set(
                    group_name.strip()
                    for group_name in v
                    if group_name and group_name.strip()
                )
            )
            return unique_groups
        return []

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v: Dict[str, str]) -> Dict[str, str]:
        if v:
            return {
                key: str(value) if value is not None else "" for key, value in v.items()
            }
        return {}


class UpdateWorkplaceUserDetailsRequest(BaseWorkplaceRequest):
    """Request model for updating workplace user details"""

    updated_details: Dict[str, Any] = Field(description="Updated user details")

    @field_validator("updated_details")
    @classmethod
    def validate_updated_details(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v or not isinstance(v, dict):
            raise ValueError("Parameter 'updatedDetails' must be present in the input.")

        allowed_keys = {"first_name", "last_name", "email_address", "phone_number"}
        invalid_keys = [key for key in v.keys() if key not in allowed_keys]
        if invalid_keys:
            raise ValueError(
                "Only first_name, last_name, email_address, phone_number can be updated"
            )

        has_any_field = any(key in v and v[key] is not None for key in allowed_keys)
        if not has_any_field:
            raise ValueError("updatedDetails must contain at least one valid field")

        return v


class UpdateWorkplaceUserAttributesRequest(BaseWorkplaceRequest):
    """Request model for updating workplace user attributes"""

    attributes: Dict[str, str] = Field(description="User attributes to update")

    @field_validator("attributes")
    @classmethod
    def validate_attributes(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v or not isinstance(v, dict) or isinstance(v, list):
            raise ValueError(
                "Parameter 'attributes' must be a dictionary and must be present in the input."
            )
        return {
            key: str(value) if value is not None else "" for key, value in v.items()
        }


class UpdateWorkplaceUserRoleRequest(BaseWorkplaceRequest):
    """Request model for updating workplace user role"""

    role: Literal["Workplace Manager", "App Builder", "User"] = Field(
        default="User", description="The new role for the user"
    )


class UpdateWorkplaceUserGroupsRequest(BaseWorkplaceRequest):
    """Request model for updating workplace user groups"""

    group_names: List[str] = Field(description="List of group names")

    @field_validator("group_names")
    @classmethod
    def validate_group_names(cls, v: List[str]) -> List[str]:
        if not isinstance(v, list) or len(v) == 0:
            raise ValueError(
                "Parameter 'groupNames' must be a non empty array and must be present in the input."
            )
        unique_groups = list(
            set(
                group_name.strip()
                for group_name in v
                if group_name and group_name.strip()
            )
        )
        return unique_groups


class AddUserToAppRequest(BaseWorkplaceRequest):
    """Request model for adding a user to an app"""

    app_id: str = Field(description="App Id")
    permissions: Permission = Field(
        description="User permissions, possible keys are: can_submit_data, can_edit_data, can_view_data, can_change_status, can_edit_app, can_bulk_upload, can_view_analytics and can_delete_data. Value must be boolean true/false."
    )

    @field_validator("app_id")
    @classmethod
    def validate_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("App ID is required and cannot be empty")
        if not re.match(r"^[A-Z0-9]+$", v.strip()):
            raise ValueError("App ID must contain only uppercase letters and numbers")
        return v.strip()


class GetWorkplaceAppsRequest(BaseModel):
    """Request model for getting workplace apps"""

    pass


class GetWorkplaceUserAppsRequest(BaseWorkplaceRequest):
    """Request model for getting workplace user apps"""

    pass


class GetWorkplaceUsersRequest(BaseModel):
    """Request model for getting workplace users"""

    page_size: Optional[int] = Field(50, description="Page size, default is 50")
    token: Optional[str] = Field(None, description="Token, needed for pagination")

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Page size must be greater than 0")
        return v
