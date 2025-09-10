from typing import Dict, Any, List, Optional
from .base_client import BaseClappiaClient
from clappia_api_tools.utils.logging_utils import get_logger
from clappia_api_tools.models.request import (
    AddUserToWorkplaceRequest,
    UpdateWorkplaceUserDetailsRequest,
    UpdateWorkplaceUserAttributesRequest,
    UpdateWorkplaceUserRoleRequest,
    UpdateWorkplaceUserGroupsRequest,
    AddUserToAppRequest,
    GetWorkplaceAppsRequest,
    GetWorkplaceUserAppsRequest,
    GetWorkplaceUsersRequest,
)
from clappia_api_tools.models.response import (
    WorkplaceUserResponse,
    WorkplaceUserDetailsResponse,
    WorkplaceUserAttributesResponse,
    WorkplaceUserRoleResponse,
    WorkplaceUserGroupsResponse,
    AppUserResponse,
    WorkplaceAppResponse,
    WorkplaceUserAppsResponse,
    WorkplaceUsersResponse,
)
from clappia_api_tools.models.workplace_user import WorkplaceUser
from clappia_api_tools.models.permissions import Permission

logger = get_logger(__name__)


class WorkplaceClient(BaseClappiaClient):
    """Client for managing Clappia workplace users.

    This client handles workplace user management operations including
    adding users to workplace, updating user details, attributes, roles,
    groups, and adding users to apps.
    """

    def add_user_to_workplace(
        self,
        first_name: str = "",
        last_name: str = "",
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
        group_names: Optional[List[str]] = None,
        attributes: Optional[Dict[str, str]] = None,
    ) -> WorkplaceUserResponse:
        """Add a user to the workplace.

        Args:
            email_address: Email address of the user (only one of email or phone is required)
            phone_number: Phone number of the user (only one of email or phone is required)
            first_name: First name of the user
            last_name: Last name of the user
            group_names: List of group names to assign to the user
            attributes: User attributes as key-value pairs

        Returns:
            WorkplaceUserResponse: Response containing operation result
        """
        try:
            request = AddUserToWorkplaceRequest(
                email_address=email_address,
                phone_number=phone_number,
                first_name=first_name,
                last_name=last_name,
                group_names=group_names or [],
                attributes=attributes or {},
            )
        except Exception as e:
            return WorkplaceUserResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                operation="add_user_to_workplace",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUserResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                operation="add_user_to_workplace",
            )

        payload = {
            "firstName": request.first_name,
            "lastName": request.last_name,
            "groupNames": request.group_names,
            "attributes": request.attributes,
        }

        if request.email_address:
            payload["emailAddress"] = request.email_address
        if request.phone_number:
            payload["phoneNumber"] = request.phone_number

        logger.info(f"Adding user to workplace with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workplace/addUserToWorkplace",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUserResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                operation="add_user_to_workplace",
            )

        return WorkplaceUserResponse(
            success=True,
            message="Successfully added user to workplace",
            email_address=email_address,
            phone_number=phone_number,
            operation="add_user_to_workplace",
            data=response_data,
        )

    def update_workplace_user_details(
        self,
        updated_details: Dict[str, Any],
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> WorkplaceUserDetailsResponse:
        """Update workplace user details.

        Args:
            email_address: Email address of the user (only one of email or phone is required)
            phone_number: Phone number of the user (only one of email or phone is required)
            updated_details: Dictionary containing the details to update

        Returns:
            WorkplaceUserDetailsResponse: Response containing operation result
        """
        try:
            request = UpdateWorkplaceUserDetailsRequest(
                email_address=email_address,
                phone_number=phone_number,
                updated_details=updated_details,
            )
        except Exception as e:
            return WorkplaceUserDetailsResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_details",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUserDetailsResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_details",
            )

        payload = {
            "updatedDetails": {
                "firstName": request.updated_details.get("first_name"),
                "lastName": request.updated_details.get("last_name"),
                "emailAddress": request.updated_details.get("email_address"),
                "phoneNumber": request.updated_details.get("phone_number"),
            }
        }

        if request.email_address:
            payload["emailAddress"] = request.email_address
        if request.phone_number:
            payload["phoneNumber"] = request.phone_number

        logger.info(f"Updating workplace user details with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserDetails",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUserDetailsResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_details",
            )

        return WorkplaceUserDetailsResponse(
            success=True,
            message="Successfully updated workplace user details",
            email_address=email_address,
            phone_number=phone_number,
            updated_details=updated_details,
            operation="update_workplace_user_details",
            data=response_data,
        )

    def update_workplace_user_attributes(
        self,
        attributes: Dict[str, str],
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> WorkplaceUserAttributesResponse:
        """Update workplace user attributes.

        Args:
            email_address: Email address of the user (only one of email or phone is required)
            phone_number: Phone number of the user (only one of email or phone is required)
            attributes: Dictionary containing the attributes to update

        Returns:
            WorkplaceUserAttributesResponse: Response containing operation result
        """
        try:
            request = UpdateWorkplaceUserAttributesRequest(
                email_address=email_address,
                phone_number=phone_number,
                attributes=attributes,
            )
        except Exception as e:
            return WorkplaceUserAttributesResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_attributes",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUserAttributesResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_attributes",
            )

        payload = {
            "attributes": request.attributes,
        }

        if request.email_address:
            payload["emailAddress"] = request.email_address
        if request.phone_number:
            payload["phoneNumber"] = request.phone_number

        logger.info(f"Updating workplace user attributes with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserAttributes",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUserAttributesResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_attributes",
            )

        return WorkplaceUserAttributesResponse(
            success=True,
            message="Successfully updated workplace user attributes",
            email_address=email_address,
            phone_number=phone_number,
            attributes=attributes,
            operation="update_workplace_user_attributes",
            data=response_data,
        )

    def update_workplace_user_role(
        self,
        role: str,
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> WorkplaceUserRoleResponse:
        """Update workplace user role.

        Args:
            email_address: Email address of the user (only one of email or phone is required)
            phone_number: Phone number of the user (only one of email or phone is required)
            role: The new role for the user

        Returns:
            WorkplaceUserRoleResponse: Response containing operation result
        """
        try:
            request = UpdateWorkplaceUserRoleRequest(
                email_address=email_address,
                phone_number=phone_number,
                role=role,
            )
        except Exception as e:
            return WorkplaceUserRoleResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_role",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUserRoleResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_role",
            )

        payload = {
            "role": request.role.value,
        }

        if request.email_address:
            payload["emailAddress"] = request.email_address
        if request.phone_number:
            payload["phoneNumber"] = request.phone_number

        logger.info(f"Updating workplace user role with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserRole",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUserRoleResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_role",
            )

        return WorkplaceUserRoleResponse(
            success=True,
            message=f"Successfully updated workplace user role to {role}",
            email_address=email_address,
            phone_number=phone_number,
            role=role,
            operation="update_workplace_user_role",
            data=response_data,
        )

    def update_workplace_user_groups(
        self,
        group_names: List[str],
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> WorkplaceUserGroupsResponse:
        """Update workplace user groups.

        Args:
            email_address: Email address of the user (only one of email or phone is required)
            phone_number: Phone number of the user (only one of email or phone is required)
            group_names: List of group names to assign to the user

        Returns:
            WorkplaceUserGroupsResponse: Response containing operation result
        """
        try:
            request = UpdateWorkplaceUserGroupsRequest(
                email_address=email_address,
                phone_number=phone_number,
                group_names=group_names,
            )
        except Exception as e:
            return WorkplaceUserGroupsResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_groups",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUserGroupsResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_groups",
            )

        payload = {
            "groupNames": request.group_names,
        }

        if request.email_address:
            payload["emailAddress"] = request.email_address
        if request.phone_number:
            payload["phoneNumber"] = request.phone_number

        logger.info(f"Updating workplace user groups with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workplace/updateWorkplaceUserGroups",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUserGroupsResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                operation="update_workplace_user_groups",
            )

        return WorkplaceUserGroupsResponse(
            success=True,
            message=f"Successfully updated workplace user groups to {', '.join(group_names)}",
            email_address=email_address,
            phone_number=phone_number,
            group_names=group_names,
            operation="update_workplace_user_groups",
            data=response_data,
        )

    def add_user_to_app(
        self,
        app_id: str,
        permissions: Dict[str, bool],
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> AppUserResponse:
        """Add a user to an app."""
        try:
            permission_instance = Permission(**permissions)
            request = AddUserToAppRequest(
                app_id=app_id,
                email_address=email_address,
                phone_number=phone_number,
                permissions=permission_instance,
            )
        except Exception as e:
            return AppUserResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                app_id=app_id,
                operation="add_user_to_app",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return AppUserResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                app_id=app_id,
                operation="add_user_to_app",
            )
        dict_permissions = request.permissions.to_dict()

        payload = {
            "appId": request.app_id,
            "permissions": dict_permissions,
        }

        if request.email_address:
            payload["emailAddress"] = request.email_address
        if request.phone_number:
            payload["phoneNumber"] = request.phone_number

        logger.info(f"Adding user to app with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="app/addUserToApp",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return AppUserResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                app_id=app_id,
                operation="add_user_to_app",
                permissions=dict_permissions,
            )

        return AppUserResponse(
            success=True,
            message=f"Successfully added user to app {app_id}",
            email_address=email_address,
            phone_number=phone_number,
            app_id=app_id,
            permissions=dict_permissions,
            operation="add_user_to_app",
            data=response_data,
        )

    def get_workplace_apps(self) -> WorkplaceAppResponse:
        """Get all apps in the workplace.

        Returns:
            WorkplaceAppResponse: Response containing list of apps
        """
        try:
            request = GetWorkplaceAppsRequest()
        except Exception as e:
            return WorkplaceAppResponse(
                success=False,
                message=str(e),
                apps=[],
                operation="get_workplace_apps",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceAppResponse(
                success=False,
                message=env_error,
                apps=[],
                operation="get_workplace_apps",
            )

        logger.info("Getting workplace apps")

        success, error_message, response_data = self.api_utils.make_request(
            method="GET",
            endpoint="workplace/getApps",
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceAppResponse(
                success=False,
                message=error_message,
                apps=[],
                operation="get_workplace_apps",
            )

        apps = []
        if response_data and isinstance(response_data, list):
            for app_data in response_data:
                try:
                    from clappia_api_tools.models.response.workplace_responses import (
                        AppMetaData,
                    )

                    print(app_data)
                    app = AppMetaData.from_json(app_data)
                    apps.append(app)
                except Exception as e:
                    logger.warning(f"Failed to parse app data: {e}")

        return WorkplaceAppResponse(
            success=True,
            message="Successfully retrieved workplace apps",
            operation="get_workplace_apps",
            data=apps,
        )

    def get_workplace_user_apps(
        self,
        email_address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> WorkplaceUserAppsResponse:
        """Get apps for a specific workplace user.

        Args:
            email_address: Email address of the user (only one of email or phone is required)
            phone_number: Phone number of the user (only one of email or phone is required)

        Returns:
            WorkplaceUserAppsResponse: Response containing list of user's apps
        """
        try:
            request = GetWorkplaceUserAppsRequest(
                email_address=email_address,
                phone_number=phone_number,
            )
        except Exception as e:
            return WorkplaceUserAppsResponse(
                success=False,
                message=str(e),
                email_address=email_address,
                phone_number=phone_number,
                apps=[],
                operation="get_workplace_user_apps",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUserAppsResponse(
                success=False,
                message=env_error,
                email_address=email_address,
                phone_number=phone_number,
                apps=[],
                operation="get_workplace_user_apps",
            )

        params = {
            "emailAddress": request.email_address,
            "phoneNumber": request.phone_number,
        }

        logger.info(f"Getting workplace user apps with params: {params}")

        success, error_message, response_data = self.api_utils.make_request(
            method="GET",
            endpoint="workplace/getUserApps",
            params=params,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUserAppsResponse(
                success=False,
                message=error_message,
                email_address=email_address,
                phone_number=phone_number,
                apps=[],
                operation="get_workplace_user_apps",
            )

        apps = []
        if response_data and isinstance(response_data, list):
            for app_data in response_data:
                try:
                    from clappia_api_tools.models.response.workplace_responses import (
                        AppUserMetaData,
                    )

                    app = AppUserMetaData.from_json(app_data)
                    apps.append(app)
                except Exception as e:
                    logger.warning(f"Failed to parse app data: {e}")

        return WorkplaceUserAppsResponse(
            success=True,
            message="Successfully retrieved workplace user apps",
            email_address=email_address,
            phone_number=phone_number,
            operation="get_workplace_user_apps",
            data=apps,
        )

    def get_workplace_users(
        self,
        page_size: Optional[int] = 50,
        token: Optional[str] = None,
    ) -> WorkplaceUsersResponse:
        """Get workplace users with pagination.

        Args:
            page_size: Number of users to retrieve per page
            token: Token for pagination

        Returns:
            WorkplaceUsersResponse: Response containing list of users and pagination token
        """
        try:
            request = GetWorkplaceUsersRequest(
                page_size=page_size,
                token=token,
            )
        except Exception as e:
            return WorkplaceUsersResponse(
                success=False,
                message=str(e),
                users=[],
                operation="get_workplace_users",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return WorkplaceUsersResponse(
                success=False,
                message=env_error,
                users=[],
                operation="get_workplace_users",
            )

        payload = {
            "pageSize": request.page_size,
            "token": request.token,
        }

        logger.info(f"Getting workplace users with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="workplace/getWorkplaceUsers",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return WorkplaceUsersResponse(
                success=False,
                message=error_message,
                users=[],
                operation="get_workplace_users",
            )

        # Parse users from response data
        users = []
        next_token = None

        if response_data and isinstance(response_data, dict):
            users_data = response_data.get("users", [])
            next_token = response_data.get("token")

            if isinstance(users_data, list):
                for user_data in users_data:
                    try:
                        user = WorkplaceUser(**user_data)
                        users.append(user)
                    except Exception as e:
                        logger.warning(f"Failed to parse user data: {e}")

        return WorkplaceUsersResponse(
            success=True,
            message="Successfully retrieved workplace users",
            users=users,
            token=next_token,
            operation="get_workplace_users",
            data=response_data,
        )
