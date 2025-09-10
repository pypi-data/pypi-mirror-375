import json
from .base_client import BaseClappiaClient
from clappia_api_tools.utils.logging_utils import get_logger
from typing import List, Dict, Any, Optional
from clappia_api_tools.models.request import (
    CreateAppRequest,
    AddPageBreakRequest,
    UpdatePageBreakRequest,
    ReorderSectionRequest,
    UpsertSectionRequest,
    UpsertFieldTextRequest,
    UpsertFieldTextAreaRequest,
    UpsertFieldDependencyAppRequest,
    UpsertFieldRestApiRequest,
    UpsertFieldAddressRequest,
    UpsertFieldDatabaseRequest,
    UpsertFieldDateRequest,
    UpsertFieldAIRequest,
    UpsertFieldCodeRequest,
    UpsertFieldCodeReaderRequest,
    UpsertFieldEmailInputRequest,
    UpsertFieldEmojiRequest,
    UpsertFieldFileRequest,
    UpsertFieldGpsLocationRequest,
    UpsertFieldLiveTrackingRequest,
    UpsertFieldManualAddressRequest,
    UpsertFieldPhoneNumberRequest,
    UpsertFieldProgressBarRequest,
    UpsertFieldSignatureRequest,
    UpsertFieldCounterRequest,
    UpsertFieldSliderRequest,
    UpsertFieldTimeRequest,
    UpsertFieldToggleRequest,
    UpsertFieldValidationRequest,
    UpsertFieldVideoViewerRequest,
    UpsertFieldVoiceRequest,
    UpsertFieldFormulaRequest,
    UpsertFieldImageViewerRequest,
    UpsertFieldRichTextEditorRequest,
    UpsertFieldNfcReaderRequest,
    UpsertFieldNumberInputRequest,
    UpsertFieldPdfViewerRequest,
    UpsertFieldReadOnlyFileRequest,
    UpsertFieldReadOnlyTextRequest,
    UpsertFieldTagsRequest,
    UpsertFieldUniqueSequentialRequest,
    UpsertFieldDropdownRequest,
    UpsertFieldRadioRequest,
    UpsertFieldUrlInputRequest,
    UpsertFieldCheckboxRequest,
    UpsertFieldRazorpayPaymentGatewayRequest,
    UpsertFieldEazypayPaymentGatewayRequest,
    UpsertFieldPaypalPaymentGatewayRequest,
    UpsertFieldStripePaymentGatewayRequest,
    UpsertFieldButtonRequest,
)

from clappia_api_tools.models.response import (
    AppDefinitionResponse,
    PageBreakOperationResponse,
    FieldOperationResponse,
    UpsertSectionOperationResponse,
    AppCreationResponse,
    ReorderSectionOperationResponse,
)

from clappia_api_tools.enums import FieldType

logger = get_logger(__name__)


class AppDefinitionClient(BaseClappiaClient):
    """Client for managing Clappia app definitions.

    This client handles retrieving and managing app definitions, including
    getting app definitions, creating apps, adding fields, and updating fields.
    """

    def create_app(self, request: CreateAppRequest) -> AppCreationResponse:
        """Create a new app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return AppCreationResponse(success=False, message=env_error)

        payload = request.to_json()

        logger.info(f"Creating app with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/createApp",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return AppCreationResponse(success=False, message=error_message)

        return AppCreationResponse(
            success=True, message="Successfully created app", data=response_data
        )

    def get_definition(self, app_id: str) -> AppDefinitionResponse:
        """Retrieve the complete definition for a specific app."""
        params = {"appId": app_id}

        logger.info(f"Getting app definition for app_id: {app_id}")

        success, error_message, response_data = self.api_utils.make_request(
            method="GET",
            endpoint="appdefinitionv2/getAppDefinition",
            params=params,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return AppDefinitionResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="get_definition",
            )

        return AppDefinitionResponse(
            success=True,
            message="Successfully retrieved app definition",
            app_id=app_id,
            data=response_data,
            operation="get_definition",
        )

    def add_text_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTextRequest,
    ) -> FieldOperationResponse:
        """Add a text field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_text_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SINGLE_LINE_TEXT.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding text field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_text_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added text field",
            app_id=app_id,
            operation="add_text_field",
            field_name=field_name,
            data=response_data,
        )

    def update_text_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTextRequest,
    ) -> FieldOperationResponse:
        """Update a text field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_text_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating text field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_text_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated text field",
            app_id=app_id,
            operation="update_text_field",
            field_name=field_name,
            data=response_data,
        )

    # TextArea Field Methods
    def add_textarea_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTextAreaRequest,
    ) -> FieldOperationResponse:
        """Add a textarea field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_textarea_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.MULTI_LINE_TEXT.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding textarea field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_textarea_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added textarea field",
            app_id=app_id,
            operation="add_textarea_field",
            field_name=field_name,
            data=response_data,
        )

    def update_textarea_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTextAreaRequest,
    ) -> FieldOperationResponse:
        """Update a textarea field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_textarea_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating textarea field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_textarea_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated textarea field",
            app_id=app_id,
            operation="update_textarea_field",
            field_name=field_name,
            data=response_data,
        )

    # Dependency App Field Methods
    def add_dependency_app_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDependencyAppRequest,
    ) -> FieldOperationResponse:
        """Add a dependency app field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_dependency_app_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GET_DATA_FROM_OTHER_APPS.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding dependency app field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_dependency_app_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added dependency app field",
            app_id=app_id,
            operation="add_dependency_app_field",
            field_name=field_name,
            data=response_data,
        )

    def update_dependency_app_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDependencyAppRequest,
    ) -> FieldOperationResponse:
        """Update a dependency app field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_dependency_app_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating dependency app field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_dependency_app_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated dependency app field",
            app_id=app_id,
            operation="update_dependency_app_field",
            field_name=field_name,
            data=response_data,
        )

    # Rest API Field Methods
    def add_rest_api_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRestApiRequest,
    ) -> FieldOperationResponse:
        """Add a REST API field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_rest_api_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GET_DATA_FROM_REST_APIS.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding REST API field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_rest_api_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added REST API field",
            app_id=app_id,
            operation="add_rest_api_field",
            field_name=field_name,
            data=response_data,
        )

    def update_rest_api_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRestApiRequest,
    ) -> FieldOperationResponse:
        """Update a REST API field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_rest_api_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating REST API field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_rest_api_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated REST API field",
            app_id=app_id,
            operation="update_rest_api_field",
            field_name=field_name,
            data=response_data,
        )

    # Address Field Methods
    def add_address_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldAddressRequest,
    ) -> FieldOperationResponse:
        """Add an address field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_address_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GEO_ADDRESS.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding address field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_address_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added address field",
            app_id=app_id,
            operation="add_address_field",
            field_name=field_name,
            data=response_data,
        )

    def update_address_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldAddressRequest,
    ) -> FieldOperationResponse:
        """Update an address field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_address_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating address field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_address_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated address field",
            app_id=app_id,
            operation="update_address_field",
            field_name=field_name,
            data=response_data,
        )

    # Database Field Methods
    def add_database_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDatabaseRequest,
    ) -> FieldOperationResponse:
        """Add a database field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_database_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.DATABASE.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding database field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_database_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added database field",
            app_id=app_id,
            operation="add_database_field",
            field_name=field_name,
            data=response_data,
        )

    def update_database_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDatabaseRequest,
    ) -> FieldOperationResponse:
        """Update a database field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_database_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating database field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_database_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated database field",
            app_id=app_id,
            operation="update_database_field",
            field_name=field_name,
            data=response_data,
        )

    # Date Field Methods
    def add_date_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDateRequest,
    ) -> FieldOperationResponse:
        """Add a date field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_date_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.DATE_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding date field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_date_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added date field",
            app_id=app_id,
            operation="add_date_field",
            field_name=field_name,
            data=response_data,
        )

    def update_date_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDateRequest,
    ) -> FieldOperationResponse:
        """Update a date field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_date_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating date field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_date_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated date field",
            app_id=app_id,
            operation="update_date_field",
            field_name=field_name,
            data=response_data,
        )

    # AI Field Methods
    def add_ai_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldAIRequest,
    ) -> FieldOperationResponse:
        """Add an AI field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_ai_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.AI.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding AI field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_ai_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added AI field",
            app_id=app_id,
            operation="add_ai_field",
            field_name=field_name,
            data=response_data,
        )

    def update_ai_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldAIRequest,
    ) -> FieldOperationResponse:
        """Update an AI field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_ai_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating AI field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_ai_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated AI field",
            app_id=app_id,
            operation="update_ai_field",
            field_name=field_name,
            data=response_data,
        )

    # Code Field Methods
    def add_code_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCodeRequest,
    ) -> FieldOperationResponse:
        """Add a code field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_code_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.CODE.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding code field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_code_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added code field",
            app_id=app_id,
            operation="add_code_field",
            field_name=field_name,
            data=response_data,
        )

    def update_code_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCodeRequest,
    ) -> FieldOperationResponse:
        """Update a code field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_code_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating code field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_code_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated code field",
            app_id=app_id,
            operation="update_code_field",
            field_name=field_name,
            data=response_data,
        )

    # Code Reader Field Methods
    def add_code_reader_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCodeReaderRequest,
    ) -> FieldOperationResponse:
        """Add a code reader field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_code_reader_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.CODE_SCANNER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding code reader field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_code_reader_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added code reader field",
            app_id=app_id,
            operation="add_code_reader_field",
            field_name=field_name,
            data=response_data,
        )

    def update_code_reader_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCodeReaderRequest,
    ) -> FieldOperationResponse:
        """Update a code reader field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_code_reader_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating code reader field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_code_reader_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated code reader field",
            app_id=app_id,
            operation="update_code_reader_field",
            field_name=field_name,
            data=response_data,
        )

    # Email Input Field Methods
    def add_email_input_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldEmailInputRequest,
    ) -> FieldOperationResponse:
        """Add an email input field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_email_input_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.EMAIL_INPUT.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding email input field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_email_input_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added email input field",
            app_id=app_id,
            operation="add_email_input_field",
            field_name=field_name,
            data=response_data,
        )

    def update_email_input_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldEmailInputRequest,
    ) -> FieldOperationResponse:
        """Update an email input field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_email_input_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating email input field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_email_input_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated email input field",
            app_id=app_id,
            operation="update_email_input_field",
            field_name=field_name,
            data=response_data,
        )

    # Emoji Field Methods
    def add_emoji_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldEmojiRequest,
    ) -> FieldOperationResponse:
        """Add an emoji field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_emoji_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.RATINGS.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding emoji field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_emoji_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added emoji field",
            app_id=app_id,
            operation="add_emoji_field",
            field_name=field_name,
            data=response_data,
        )

    def update_emoji_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldEmojiRequest,
    ) -> FieldOperationResponse:
        """Update an emoji field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_emoji_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating emoji field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_emoji_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated emoji field",
            app_id=app_id,
            operation="update_emoji_field",
            field_name=field_name,
            data=response_data,
        )

    # File Field Methods
    def add_file_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldFileRequest,
    ) -> FieldOperationResponse:
        """Add a file field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_file_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.FILE.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding file field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_file_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added file field",
            app_id=app_id,
            operation="add_file_field",
            field_name=field_name,
            data=response_data,
        )

    def update_file_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldFileRequest,
    ) -> FieldOperationResponse:
        """Update a file field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_file_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating file field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_file_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated file field",
            app_id=app_id,
            operation="update_file_field",
            field_name=field_name,
            data=response_data,
        )

    # GPS Location Field Methods
    def add_gps_location_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldGpsLocationRequest,
    ) -> FieldOperationResponse:
        """Add a GPS location field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_gps_location_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.GPS_LOCATION.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding GPS location field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_gps_location_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added GPS location field",
            app_id=app_id,
            operation="add_gps_location_field",
            field_name=field_name,
            data=response_data,
        )

    def update_gps_location_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldGpsLocationRequest,
    ) -> FieldOperationResponse:
        """Update a GPS location field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_gps_location_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating GPS location field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_gps_location_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated GPS location field",
            app_id=app_id,
            operation="update_gps_location_field",
            field_name=field_name,
            data=response_data,
        )

    # Live Tracking Field Methods
    def add_live_tracking_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldLiveTrackingRequest,
    ) -> FieldOperationResponse:
        """Add a live tracking field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_live_tracking_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.LIVE_TRACKING.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding live tracking field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_live_tracking_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added live tracking field",
            app_id=app_id,
            operation="add_live_tracking_field",
            field_name=field_name,
            data=response_data,
        )

    def update_live_tracking_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldLiveTrackingRequest,
    ) -> FieldOperationResponse:
        """Update a live tracking field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_live_tracking_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating live tracking field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_live_tracking_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated live tracking field",
            app_id=app_id,
            operation="update_live_tracking_field",
            field_name=field_name,
            data=response_data,
        )

    # Manual Address Field Methods
    def add_manual_address_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldManualAddressRequest,
    ) -> FieldOperationResponse:
        """Add a manual address field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_manual_address_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.ADDRESS.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding manual address field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_manual_address_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added manual address field",
            app_id=app_id,
            operation="add_manual_address_field",
            field_name=field_name,
            data=response_data,
        )

    def update_manual_address_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldManualAddressRequest,
    ) -> FieldOperationResponse:
        """Update a manual address field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_manual_address_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating manual address field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_manual_address_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated manual address field",
            app_id=app_id,
            operation="update_manual_address_field",
            field_name=field_name,
            data=response_data,
        )

    # Phone Number Field Methods
    def add_phone_number_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldPhoneNumberRequest,
    ) -> FieldOperationResponse:
        """Add a phone number field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_phone_number_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PHONE_NUMBER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding phone number field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_phone_number_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added phone number field",
            app_id=app_id,
            operation="add_phone_number_field",
            field_name=field_name,
            data=response_data,
        )

    def update_phone_number_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldPhoneNumberRequest,
    ) -> FieldOperationResponse:
        """Update a phone number field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_phone_number_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating phone number field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_phone_number_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated phone number field",
            app_id=app_id,
            operation="update_phone_number_field",
            field_name=field_name,
            data=response_data,
        )

    # Progress Bar Field Methods
    def add_progress_bar_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldProgressBarRequest,
    ) -> FieldOperationResponse:
        """Add a progress bar field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_progress_bar_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PROGRESS_BAR.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding progress bar field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_progress_bar_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added progress bar field",
            app_id=app_id,
            operation="add_progress_bar_field",
            field_name=field_name,
            data=response_data,
        )

    def update_progress_bar_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldProgressBarRequest,
    ) -> FieldOperationResponse:
        """Update a progress bar field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_progress_bar_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating progress bar field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_progress_bar_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated progress bar field",
            app_id=app_id,
            operation="update_progress_bar_field",
            field_name=field_name,
            data=response_data,
        )

    # Signature Field Methods
    def add_signature_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldSignatureRequest,
    ) -> FieldOperationResponse:
        """Add a signature field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_signature_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SIGNATURE.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding signature field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_signature_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added signature field",
            app_id=app_id,
            operation="add_signature_field",
            field_name=field_name,
            data=response_data,
        )

    def update_signature_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldSignatureRequest,
    ) -> FieldOperationResponse:
        """Update a signature field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_signature_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating signature field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_signature_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated signature field",
            app_id=app_id,
            operation="update_signature_field",
            field_name=field_name,
            data=response_data,
        )

    # Counter Field Methods
    def add_counter_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCounterRequest,
    ) -> FieldOperationResponse:
        """Add a counter field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_counter_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.COUNTER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding counter field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_counter_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added counter field",
            app_id=app_id,
            operation="add_counter_field",
            field_name=field_name,
            data=response_data,
        )

    def update_counter_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCounterRequest,
    ) -> FieldOperationResponse:
        """Update a counter field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_counter_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating counter field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_counter_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated counter field",
            app_id=app_id,
            operation="update_counter_field",
            field_name=field_name,
            data=response_data,
        )

    # Slider Field Methods
    def add_slider_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldSliderRequest,
    ) -> FieldOperationResponse:
        """Add a slider field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_slider_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SLIDER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding slider field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_slider_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added slider field",
            app_id=app_id,
            operation="add_slider_field",
            field_name=field_name,
            data=response_data,
        )

    def update_slider_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldSliderRequest,
    ) -> FieldOperationResponse:
        """Update a slider field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_slider_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating slider field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_slider_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated slider field",
            app_id=app_id,
            operation="update_slider_field",
            field_name=field_name,
            data=response_data,
        )

    # Time Field Methods
    def add_time_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTimeRequest,
    ) -> FieldOperationResponse:
        """Add a time field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_time_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.TIME_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding time field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_time_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added time field",
            app_id=app_id,
            operation="add_time_field",
            field_name=field_name,
            data=response_data,
        )

    def update_time_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTimeRequest,
    ) -> FieldOperationResponse:
        """Update a time field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_time_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating time field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_time_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated time field",
            app_id=app_id,
            operation="update_time_field",
            field_name=field_name,
            data=response_data,
        )

    # Toggle Field Methods
    def add_toggle_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldToggleRequest,
    ) -> FieldOperationResponse:
        """Add a toggle field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_toggle_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.TOGGLE.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding toggle field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_toggle_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added toggle field",
            app_id=app_id,
            operation="add_toggle_field",
            field_name=field_name,
            data=response_data,
        )

    def update_toggle_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldToggleRequest,
    ) -> FieldOperationResponse:
        """Update a toggle field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_toggle_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating toggle field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_toggle_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated toggle field",
            app_id=app_id,
            operation="update_toggle_field",
            field_name=field_name,
            data=response_data,
        )

    # Validation Field Methods
    def add_validation_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldValidationRequest,
    ) -> FieldOperationResponse:
        """Add a validation field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_validation_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.VALIDATION.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding validation field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_validation_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added validation field",
            app_id=app_id,
            operation="add_validation_field",
            field_name=field_name,
            data=response_data,
        )

    def update_validation_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldValidationRequest,
    ) -> FieldOperationResponse:
        """Update a validation field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_validation_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating validation field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_validation_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated validation field",
            app_id=app_id,
            operation="update_validation_field",
            field_name=field_name,
            data=response_data,
        )

    # Video Viewer Field Methods
    def add_video_viewer_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldVideoViewerRequest,
    ) -> FieldOperationResponse:
        """Add a video viewer field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_video_viewer_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.VIDEO_VIEWER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding video viewer field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_video_viewer_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added video viewer field",
            app_id=app_id,
            operation="add_video_viewer_field",
            field_name=field_name,
            data=response_data,
        )

    def update_video_viewer_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldVideoViewerRequest,
    ) -> FieldOperationResponse:
        """Update a video viewer field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_video_viewer_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating video viewer field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_video_viewer_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated video viewer field",
            app_id=app_id,
            operation="update_video_viewer_field",
            field_name=field_name,
            data=response_data,
        )

    # Voice Field Methods
    def add_voice_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldVoiceRequest,
    ) -> FieldOperationResponse:
        """Add a voice field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_voice_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.AUDIO.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding voice field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_voice_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added voice field",
            app_id=app_id,
            operation="add_voice_field",
            field_name=field_name,
            data=response_data,
        )

    def update_voice_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldVoiceRequest,
    ) -> FieldOperationResponse:
        """Update a voice field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_voice_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating voice field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_voice_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated voice field",
            app_id=app_id,
            operation="update_voice_field",
            field_name=field_name,
            data=response_data,
        )

    # Formula Field Methods
    def add_formula_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldFormulaRequest,
    ) -> FieldOperationResponse:
        """Add a formula field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_formula_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.CALCULATIONS_AND_LOGIC.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding formula field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_formula_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added formula field",
            app_id=app_id,
            operation="add_formula_field",
            field_name=field_name,
            data=response_data,
        )

    def update_formula_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldFormulaRequest,
    ) -> FieldOperationResponse:
        """Update a formula field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_formula_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating formula field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_formula_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated formula field",
            app_id=app_id,
            operation="update_formula_field",
            field_name=field_name,
            data=response_data,
        )

    def add_image_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldImageViewerRequest,
    ) -> FieldOperationResponse:
        """Add an image field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_image_field",
                field_name=field_name,
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.IMAGE_VIEWER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding image field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_image_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added image field",
            app_id=app_id,
            operation="add_image_field",
            field_name=field_name,
            data=response_data,
        )

    def update_image_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldImageViewerRequest,
    ) -> FieldOperationResponse:
        """Update an image field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_image_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating image field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_image_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated image field",
            app_id=app_id,
            operation="update_image_field",
            field_name=field_name,
            data=response_data,
        )

    def add_rich_text_editor_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRichTextEditorRequest,
    ) -> FieldOperationResponse:
        """Add a rich text editor field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_rich_text_editor_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.RICH_TEXT_EDITOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding rich text editor field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_rich_text_editor_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added rich text editor field",
            app_id=app_id,
            operation="add_rich_text_editor_field",
            field_name=field_name,
            data=response_data,
        )

    def update_rich_text_editor_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRichTextEditorRequest,
    ) -> FieldOperationResponse:
        """Update a rich text editor field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_rich_text_editor_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating rich text editor field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_rich_text_editor_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated rich text editor field",
            app_id=app_id,
            operation="update_rich_text_editor_field",
            field_name=field_name,
            data=response_data,
        )

    def add_nfc_reader_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldNfcReaderRequest,
    ) -> FieldOperationResponse:
        """Add an NFC reader field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_nfc_reader_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.NFC_READER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding NFC reader field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_nfc_reader_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added NFC reader field",
            app_id=app_id,
            operation="add_nfc_reader_field",
            field_name=field_name,
            data=response_data,
        )

    def update_nfc_reader_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldNfcReaderRequest,
    ) -> FieldOperationResponse:
        """Update an NFC reader field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_nfc_reader_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating NFC reader field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_nfc_reader_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated NFC reader field",
            app_id=app_id,
            operation="update_nfc_reader_field",
            field_name=field_name,
            data=response_data,
        )

    def add_number_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldNumberInputRequest,
    ) -> FieldOperationResponse:
        """Add a number field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_number_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.NUMBER_INPUT.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding number field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_number_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added number field",
            app_id=app_id,
            operation="add_number_field",
            field_name=field_name,
            data=response_data,
        )

    def update_number_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldNumberInputRequest,
    ) -> FieldOperationResponse:
        """Update a number field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_number_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating number field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_number_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated number field",
            app_id=app_id,
            operation="update_number_field",
            field_name=field_name,
            data=response_data,
        )

    def add_pdf_viewer_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldPdfViewerRequest,
    ) -> FieldOperationResponse:
        """Add a PDF viewer field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_pdf_viewer_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PDF_VIEWER.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding PDF viewer field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_pdf_viewer_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added PDF viewer field",
            app_id=app_id,
            operation="add_pdf_viewer_field",
            field_name=field_name,
            data=response_data,
        )

    def update_pdf_viewer_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldPdfViewerRequest,
    ) -> FieldOperationResponse:
        """Update a PDF viewer field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_pdf_viewer_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating PDF viewer field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                field_name=field_name,
                operation="update_pdf_viewer_field",
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated PDF viewer field",
            app_id=app_id,
            operation="update_pdf_viewer_field",
            field_name=field_name,
            data=response_data,
        )

    def add_read_only_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldReadOnlyFileRequest,
    ) -> FieldOperationResponse:
        """Add a read only field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_read_only_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.ATTACHED_FILES.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding read only field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_read_only_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added read only field",
            app_id=app_id,
            operation="add_read_only_field",
            field_name=field_name,
            data=response_data,
        )

    def update_read_only_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldReadOnlyFileRequest,
    ) -> FieldOperationResponse:
        """Update a read only field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_read_only_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating read only field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_read_only_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated read only field",
            app_id=app_id,
            operation="update_read_only_field",
            field_name=field_name,
            data=response_data,
        )

    def add_read_only_text_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldReadOnlyTextRequest,
    ) -> FieldOperationResponse:
        """Add a read only text field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_read_only_text_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.HTML.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding read only text field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_read_only_text_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added read only text field",
            app_id=app_id,
            operation="add_read_only_text_field",
            field_name=field_name,
            data=response_data,
        )

    def update_read_only_text_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldReadOnlyTextRequest,
    ) -> FieldOperationResponse:
        """Update a read only text field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_read_only_text_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating read only text field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_read_only_text_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated read only text field",
            app_id=app_id,
            operation="update_read_only_text_field",
            field_name=field_name,
            data=response_data,
        )

    def add_tag_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldTagsRequest,
    ) -> FieldOperationResponse:
        """Add a tag field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_tag_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.TAGS.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding tag field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_tag_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added tag field",
            app_id=app_id,
            operation="add_tag_field",
            field_name=field_name,
            data=response_data,
        )

    def update_tag_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldTagsRequest,
    ) -> FieldOperationResponse:
        """Update a tag field in an app."""

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_tag_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating tag field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_tag_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated tag field",
            app_id=app_id,
            operation="update_tag_field",
            field_name=field_name,
            data=response_data,
        )

    def add_unique_sequential_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldUniqueSequentialRequest,
    ) -> FieldOperationResponse:
        """Add a unique sequential field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_unique_sequential_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.UNIQUE_NUMBERING.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding unique sequential field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_unique_sequential_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added unique sequential field",
            app_id=app_id,
            operation="add_unique_sequential_field",
            field_name=field_name,
            data=response_data,
        )

    def update_unique_sequential_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldUniqueSequentialRequest,
    ) -> FieldOperationResponse:
        """Update a unique sequential field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_unique_sequential_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating unique sequential field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_unique_sequential_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated unique sequential field",
            app_id=app_id,
            operation="update_unique_sequential_field",
            field_name=field_name,
            data=response_data,
        )

    def add_drop_down_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldDropdownRequest,
    ) -> FieldOperationResponse:
        """Add a drop down field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_drop_down_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.DROP_DOWN.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding drop down field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_drop_down_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added drop down field",
            app_id=app_id,
            operation="add_drop_down_field",
            field_name=field_name,
            data=response_data,
        )

    def update_drop_down_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldDropdownRequest,
    ) -> FieldOperationResponse:
        """Update a drop down field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_drop_down_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating drop down field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_drop_down_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated drop down field",
            app_id=app_id,
            operation="update_drop_down_field",
            field_name=field_name,
            data=response_data,
        )

    def add_radio_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRadioRequest,
    ) -> FieldOperationResponse:
        """Add a radio field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_radio_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.SINGLE_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding radio field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_radio_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added radio field",
            app_id=app_id,
            operation="add_radio_field",
            field_name=field_name,
            data=response_data,
        )

    def update_radio_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRadioRequest,
    ) -> FieldOperationResponse:
        """Update a radio field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_radio_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Updating radio field in app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_radio_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated radio field",
            app_id=app_id,
            operation="update_radio_field",
            field_name=field_name,
            data=response_data,
        )

    def add_url_input_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldUrlInputRequest,
    ) -> FieldOperationResponse:
        """Add a URL input field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_url_input_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.URL_INPUT.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding URL input field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_url_input_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added URL input field",
            app_id=app_id,
            operation="add_url_input_field",
            field_name=field_name,
            data=response_data,
        )

    def update_url_input_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldUrlInputRequest,
    ) -> FieldOperationResponse:
        """Update a URL input field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_url_input_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating URL input field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_url_input_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated URL input field",
            app_id=app_id,
            operation="update_url_input_field",
            field_name=field_name,
            data=response_data,
        )

    def add_checkbox_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldCheckboxRequest,
    ) -> FieldOperationResponse:
        """Add a checkbox field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_checkbox_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.MULTI_SELECTOR.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding checkbox field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_checkbox_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added checkbox field",
            app_id=app_id,
            operation="add_checkbox_field",
            field_name=field_name,
            data=response_data,
        )

    def update_checkbox_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldCheckboxRequest,
    ) -> FieldOperationResponse:
        """Update a checkbox field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_checkbox_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating checkbox field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_checkbox_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated checkbox field",
            app_id=app_id,
            operation="update_checkbox_field",
            field_name=field_name,
            data=response_data,
        )

    def add_razorpay_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldRazorpayPaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Add a razorpay payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_razorpay_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding razorpay payment gateway field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_razorpay_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added razorpay payment gateway field",
            app_id=app_id,
            operation="add_razorpay_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def update_razorpay_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldRazorpayPaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Update a razorpay payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_razorpay_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating razorpay payment gateway field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_razorpay_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated razorpay payment gateway field",
            app_id=app_id,
            operation="update_razorpay_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def add_eazypay_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldEazypayPaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Add an eazypay payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_eazypay_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding eazypay payment gateway field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_eazypay_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added eazypay payment gateway field",
            app_id=app_id,
            operation="add_eazypay_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def update_eazypay_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldEazypayPaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Update an eazypay payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_eazypay_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating eazypay payment gateway field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_eazypay_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated eazypay payment gateway field",
            app_id=app_id,
            operation="update_eazypay_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def add_paypal_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldPaypalPaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Add a paypal payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_paypal_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding paypal payment gateway field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_paypal_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added paypal payment gateway field",
            app_id=app_id,
            operation="add_paypal_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def update_paypal_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldPaypalPaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Update a paypal payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_paypal_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating paypal payment gateway field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_paypal_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated paypal payment gateway field",
            app_id=app_id,
            operation="update_paypal_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def add_stripe_payment_gateway_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldStripePaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Add a stripe payment gateway field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_stripe_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "pageIndex": page_index,
            "fieldType": FieldType.PAYMENT_GATEWAY.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Adding stripe payment gateway field to app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_stripe_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added stripe payment gateway field",
            app_id=app_id,
            operation="add_stripe_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def update_stripe_payment_gateway_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldStripePaymentGatewayRequest,
    ) -> FieldOperationResponse:
        """Update a stripe payment gateway field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_stripe_payment_gateway_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating stripe payment gateway field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_stripe_payment_gateway_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated stripe payment gateway field",
            app_id=app_id,
            operation="update_stripe_payment_gateway_field",
            field_name=field_name,
            data=response_data,
        )

    def add_button_field(
        self,
        app_id: str,
        section_index: int,
        field_index: int,
        page_index: int,
        field_name: str,
        request: UpsertFieldButtonRequest,
    ) -> FieldOperationResponse:
        """Add a button field to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="add_button_field",
            )

        payload = {
            "appId": app_id,
            "sectionIndex": section_index,
            "fieldIndex": field_index,
            "fieldType": FieldType.BUTTON.value,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(f"Adding button field to app_id: {app_id} with payload: {payload}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_button_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully added button field",
            app_id=app_id,
            operation="add_button_field",
            field_name=field_name,
            data=response_data,
        )

    def update_button_field(
        self,
        app_id: str,
        field_name: str,
        request: UpsertFieldButtonRequest,
    ) -> FieldOperationResponse:
        """Update a button field in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return FieldOperationResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                field_name=field_name,
                operation="update_button_field",
            )

        payload = {
            "appId": app_id,
            "fieldName": field_name,
            **request.to_json(),
        }

        logger.info(
            f"Updating button field in app_id: {app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateField",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return FieldOperationResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_button_field",
                field_name=field_name,
            )

        return FieldOperationResponse(
            success=True,
            message="Successfully updated button field",
            app_id=app_id,
            operation="update_button_field",
            field_name=field_name,
            data=response_data,
        )

    def add_page_break(
        self, request: AddPageBreakRequest
    ) -> PageBreakOperationResponse:
        """Add a page break to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return PageBreakOperationResponse(
                success=False,
                message=env_error,
                app_id=request.app_id,
                page_index=request.page_index,
                operation="add_page_break",
            )

        payload = {
            "appId": request.app_id,
            "pageIndex": request.page_index,
            "sectionIndex": request.section_index,
            "pageMetadata": request.page_metadata.to_json(),
        }

        logger.info(
            f"Adding page break to app_id: {request.app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addPageBreak",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return PageBreakOperationResponse(
                success=False,
                message=error_message,
                app_id=request.app_id,
                page_index=request.page_index,
                operation="add_page_break",
                data=response_data,
            )

        return PageBreakOperationResponse(
            success=True,
            message=f"Page break after Page with index {request.page_index} and after section with index {request.section_index} added successfully",
            app_id=request.app_id,
            page_index=request.page_index,
            operation="add_page_break",
            data=response_data,
        )

    def update_page(
        self, request: UpdatePageBreakRequest
    ) -> PageBreakOperationResponse:
        """Update page break settings in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return PageBreakOperationResponse(
                success=False,
                message=env_error,
                app_id=request.app_id,
                page_index=request.page_index,
                operation="update_page",
            )

        payload = {
            "appId": request.app_id.strip(),
            "pageIndex": request.page_index,
            "pageMetadata": request.page_metadata.to_json(),
        }

        logger.info(
            f"Updating page '{request.page_index}' in app_id: {request.app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updatePageBreak",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return PageBreakOperationResponse(
                success=False,
                message=error_message,
                app_id=request.app_id,
                page_index=request.page_index,
                operation="update_page",
                data=response_data,
            )

        return PageBreakOperationResponse(
            success=True,
            message=f"Page at index {request.page_index} updated successfully",
            app_id=request.app_id,
            page_index=request.page_index,
            operation="update_page",
            data=response_data,
        )

    def reorder_section(
        self, request: ReorderSectionRequest
    ) -> ReorderSectionOperationResponse:
        """Reorder a section within an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ReorderSectionOperationResponse(
                success=False,
                message=env_error,
                app_id=request.app_id,
                source_section_index=request.source_section_index,
                target_section_index=request.target_section_index,
                source_page_index=request.source_page_index,
                target_page_index=request.target_page_index,
                operation="reorder_section",
            )

        payload = {
            "appId": request.app_id.strip(),
            "sourceSectionIndex": request.source_section_index,
            "targetSectionIndex": request.target_section_index,
        }

        if request.source_page_index is not None:
            payload["sourcePageIndex"] = request.source_page_index
        if request.target_page_index is not None:
            payload["targetPageIndex"] = request.target_page_index

        logger.info(
            f"Reordering section in app_id: {request.app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/reorderSection",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ReorderSectionOperationResponse(
                success=False,
                message=error_message,
                app_id=request.app_id,
                source_section_index=request.source_section_index,
                target_section_index=request.target_section_index,
                source_page_index=request.source_page_index,
                target_page_index=request.target_page_index,
                operation="reorder_section",
                data=response_data,
            )

        return ReorderSectionOperationResponse(
            success=True,
            message="Section reordered successfully",
            app_id=request.app_id,
            source_section_index=request.source_section_index,
            target_section_index=request.target_section_index,
            source_page_index=request.source_page_index,
            target_page_index=request.target_page_index,
            operation="reorder_section",
            data=response_data,
        )

    def add_section(
        self, request: UpsertSectionRequest
    ) -> UpsertSectionOperationResponse:
        """Add a section to an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return UpsertSectionOperationResponse(
                success=False,
                message=env_error,
                app_id=request.app_id,
                section_index=request.section_index,
                page_index=request.page_index,
                operation="add_section",
            )

        payload = request.to_json()

        logger.info(
            f"Adding section to app_id: {request.app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/addSection",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return UpsertSectionOperationResponse(
                success=False,
                message=error_message,
                app_id=request.app_id,
                section_index=request.section_index,
                page_index=request.page_index,
                operation="add_section",
                data=response_data,
            )

        return UpsertSectionOperationResponse(
            success=True,
            message="Section added successfully",
            app_id=request.app_id,
            section_index=request.section_index,
            operation="add_section",
            data=response_data,
        )

    def update_section(
        self, request: UpsertSectionRequest
    ) -> UpsertSectionOperationResponse:
        """Update a section in an app."""
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return UpsertSectionOperationResponse(
                success=False,
                message=env_error,
                app_id=request.app_id,
                section_index=request.section_index,
                page_index=request.page_index,
                operation="update_section",
            )

        payload = request.to_json()

        logger.info(
            f"Updating section in app_id: {request.app_id} with payload: {payload}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="appdefinitionv2/updateSection",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return UpsertSectionOperationResponse(
                success=False,
                message=error_message,
                app_id=request.app_id,
                section_index=request.section_index,
                page_index=request.page_index,
                operation="update_section",
                data=response_data,
            )

        return UpsertSectionOperationResponse(
            success=True,
            message="Section updated successfully",
            app_id=request.app_id,
            section_index=request.section_index,
            page_index=request.page_index,
            operation="update_section",
            data=response_data,
        )
