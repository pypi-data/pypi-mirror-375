from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base_response import BaseResponse
from ..workplace_user import WorkplaceUser


class AppMetaData(BaseModel):
    """Response model for app metadata"""

    app_id: str = Field(description="App ID")
    name: Optional[str] = Field(None, description="App name")
    created_at: int = Field(description="App created at")
    created_by: Dict[str, Any] = Field(description="App created by")
    updated_at: int = Field(description="App updated at")
    updated_by: Dict[str, Any] = Field(description="App updated by")

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "AppMetaData":
        """Create AppMetaData instance from JSON data with proper field mapping"""
        mapped_data = {
            "app_id": json_data.get("appId"),
            "name": json_data.get("name", None),
            "created_at": json_data.get("createdAt"),
            "created_by": json_data.get("createdBy"),
            "updated_at": json_data.get("lastUpdatedAt"),
            "updated_by": json_data.get("lastUpdatedBy"),
        }
        return cls(**mapped_data)


# For get workplace user apps
class AppUserMetaData(BaseModel):
    """Response model for app metadata"""

    app_id: str = Field(description="App ID")
    name: Optional[str] = Field(None, description="App name")

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "AppUserMetaData":
        """Create AppUserMetaData instance from JSON data with proper field mapping"""
        mapped_data = {
            "app_id": json_data.get("appId"),
            "name": json_data.get("name", None),
        }
        return cls(**mapped_data)


class WorkplaceUserResponse(BaseResponse):
    """Response model for workplace user operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")


class WorkplaceUserDetailsResponse(BaseResponse):
    """Response model for workplace user details operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    updated_details: Optional[Dict[str, Any]] = Field(
        None, description="Updated user details"
    )


class WorkplaceUserAttributesResponse(BaseResponse):
    """Response model for workplace user attributes operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    attributes: Optional[Dict[str, str]] = Field(None, description="User attributes")


class WorkplaceUserRoleResponse(BaseResponse):
    """Response model for workplace user role operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    role: Optional[str] = Field(None, description="User role")


class WorkplaceUserGroupsResponse(BaseResponse):
    """Response model for workplace user groups operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    group_names: Optional[List[str]] = Field(None, description="Group names")


class AppUserResponse(BaseResponse):
    """Response model for app user operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")
    app_id: Optional[str] = Field(None, description="App ID")
    permissions: Optional[Dict[str, bool]] = Field(None, description="User permissions")


class WorkplaceAppResponse(BaseResponse):
    """Response model for workplace app operations"""

    pass


class WorkplaceUserAppsResponse(BaseResponse):
    """Response model for workplace user app operations"""

    email_address: Optional[str] = Field(None, description="Email address of the user")
    phone_number: Optional[str] = Field(None, description="Phone number of the user")


class WorkplaceUsersResponse(BaseResponse):
    """Response model for workplace users operations"""

    users: List[WorkplaceUser] = Field(description="List of users")
    token: Optional[str] = Field(None, description="Token, needed for pagination")
