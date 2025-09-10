from unittest.mock import patch
from clappia_api_tools.client.app_definition_client import AppDefinitionClient
from clappia_api_tools.client.submission_client import SubmissionClient


def dummy_app_definition_client():
    return AppDefinitionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        timeout=30,
    )


def dummy_submission_client():
    return SubmissionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        timeout=30,
    )


class TestDefinitionToolsIntegration:

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_get_definition_tool_basic(self, mock_make_request):
        mock_make_request.return_value = (
            True,
            None,
            {
                "appId": "MFX093412",
                "version": "1.0",
                "state": "active",
                "pageIds": ["page1", "page2"],
                "sectionIds": ["section1"],
                "fieldDefinitions": {"field1": {}, "field2": {}},
                "metadata": {"name": "Test App", "description": "Test Description"},
            },
        )

        client = dummy_app_definition_client()
        result = client.get_definition("MFX093412")

        assert result.success is True
        assert "Successfully retrieved app definition" in result.message
        assert result.app_id == "MFX093412"
        assert result.data["name"] == "Test App"

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="appdefinitionv2/getAppDefinition",
            params={
                "appId": "MFX093412",
                "language": "en",
                "stripHtml": "true",
                "includeTags": "true",
            },
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_get_definition_tool_with_language(self, mock_make_request):
        mock_make_request.return_value = (
            True,
            None,
            {
                "appId": "MFX093412",
                "version": "1.0",
                "state": "active",
                "pageIds": ["page1", "page2"],
                "sectionIds": ["section1"],
                "fieldDefinitions": {"field1": {}, "field2": {}},
                "metadata": {
                    "name": "Aplicación de Prueba",
                    "description": "Descripción de prueba",
                },
            },
        )

        client = dummy_app_definition_client()
        result = client.get_definition("MFX093412", language="es")

        assert result.success is True
        assert "Successfully retrieved app definition" in result.message
        assert result.app_id == "MFX093412"
        assert result.data["name"] == "Aplicación de Prueba"

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="appdefinitionv2/getAppDefinition",
            params={
                "appId": "MFX093412",
                "language": "es",
                "stripHtml": "true",
                "includeTags": "true",
            },
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_get_definition_tool_custom_options(self, mock_make_request):
        mock_make_request.return_value = (
            True,
            None,
            {
                "appId": "MFX093412",
                "version": "1.0",
                "state": "active",
                "pageIds": ["page1"],
                "sectionIds": ["section1"],
                "fieldDefinitions": {"field1": {"type": "text", "html": "<b>Bold</b>"}},
                "metadata": {
                    "name": "Test App",
                    "description": "Test with <em>HTML</em>",
                },
            },
        )

        client = dummy_app_definition_client()
        result = client.get_definition(
            "MFX093412", language="fr", strip_html=False, include_tags=False
        )

        assert result.success is True
        assert "Successfully retrieved app definition" in result.message
        assert result.app_id == "MFX093412"

        mock_make_request.assert_called_once_with(
            method="GET",
            endpoint="appdefinitionv2/getAppDefinition",
            params={
                "appId": "MFX093412",
                "language": "fr",
                "stripHtml": "false",
                "includeTags": "false",
            },
        )

    def test_get_definition_tool_error_handling(self):
        client = dummy_app_definition_client()
        result = client.get_definition("invalid-app-id")

        assert result.success is False
        assert (
            "App ID must contain only uppercase letters and numbers" in result.message
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_basic(self, mock_validate_env, mock_make_request):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (True, None, {"fieldName": "TEST_FIELD"})

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=0,
            field_index=1,
            field_type="singleLineText",
            label="Employee Name",
            required=True,
        )

        assert result.success is True
        assert "Successfully added singleLineText field" in result.message
        assert result.app_id == "MFX093412"
        assert result.field_name == "TEST_FIELD"

        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "appdefinitionv2/addField"
        assert call_args[1]["data"]["fieldType"] == "singleLineText"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_with_options(self, mock_validate_env, mock_make_request):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (True, None, {"fieldName": "DROPDOWN_FIELD"})

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=0,
            field_index=2,
            field_type="dropDown",
            label="Department",
            required=True,
            description="Select employee department",
            options=["Engineering", "Marketing", "Sales", "HR"],
            block_width_percentage_desktop=50,
        )

        assert result.success is True
        assert "Successfully added dropDown field" in result.message
        assert result.app_id == "MFX093412"
        assert result.field_name == "DROPDOWN_FIELD"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_selector_field(self, mock_validate_env, mock_make_request):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (True, None, {"fieldName": "RADIO_FIELD"})

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=1,
            field_index=0,
            field_type="singleSelector",
            label="Employment Type",
            required=True,
            options=["Full-time", "Part-time", "Contract", "Intern"],
            style="standard",
            number_of_cols=2,
        )

        assert result.success is True
        assert "Successfully added singleSelector field" in result.message
        assert result.app_id == "MFX093412"
        assert result.field_name == "RADIO_FIELD"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_file_field(self, mock_validate_env, mock_make_request):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (True, None, {"fieldName": "FILE_FIELD"})

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=2,
            field_index=0,
            field_type="file",
            label="Resume Upload",
            required=False,
            allowed_file_types=["documents"],
            max_file_allowed=1,
            file_name_prefix="resume_",
        )

        assert result.success is True
        assert "Successfully added file field" in result.message
        assert result.app_id == "MFX093412"
        assert result.field_name == "FILE_FIELD"

    def test_add_field_tool_validation_error(self):
        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=0,
            field_index=0,
            field_type="invalidFieldType",
            label="Invalid Field",
            required=True,
        )

        assert result.success is False
        assert "1 validation error for AddFieldRequest" in result.message

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_create_app_tool_basic(self, mock_validate_env, mock_make_request):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,
            None,
            {"appId": "APP123", "appUrl": "https://app.clappia.com/APP123"},
        )

        sections = [
            {
                "section_name": "Personal Information",
                "fields": [
                    {
                        "field_type": "singleLineText",
                        "label": "Full Name",
                        "options": None,
                        "required": False,
                    },
                    {
                        "field_type": "singleLineText",
                        "label": "Email Address",
                        "options": None,
                        "required": False,
                    },
                ],
            }
        ]

        client = dummy_app_definition_client()
        result = client.create_app(
            app_name="Employee Registration",
            requesting_user_email_address="admin@example.com",
            sections=sections,
        )

        assert result.success is True
        assert "App created successfully" in result.message
        assert result.app_id == "APP123"
        assert result.app_name == "Employee Registration"
        assert result.sections_created == 1

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_create_app_tool_multiple_sections(
        self, mock_validate_env, mock_make_request
    ):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,
            None,
            {"appId": "COMPLEX123", "appUrl": "https://app.clappia.com/COMPLEX123"},
        )

        sections = [
            {
                "section_name": "Personal Information",
                "fields": [
                    {
                        "field_type": "singleLineText",
                        "label": "Full Name",
                        "options": None,
                    },
                    {"field_type": "singleLineText", "label": "Email", "options": None},
                ],
            },
            {
                "section_name": "Employment Details",
                "fields": [
                    {
                        "field_type": "dropDown",
                        "label": "Department",
                        "options": ["Engineering", "Marketing"],
                    },
                    {
                        "field_type": "singleSelector",
                        "label": "Position",
                        "options": ["Junior", "Senior", "Lead"],
                    },
                ],
            },
            {
                "section_name": "Additional Information",
                "fields": [
                    {
                        "field_type": "multiLineText",
                        "label": "Comments",
                        "options": None,
                    }
                ],
            },
        ]

        client = dummy_app_definition_client()
        result = client.create_app(
            app_name="Comprehensive Employee Survey",
            requesting_user_email_address="hr@example.com",
            sections=sections,
        )

        assert result.success is True
        assert "App created successfully" in result.message
        assert result.app_id == "COMPLEX123"
        assert result.sections_created == 3

    def test_create_app_tool_validation_error(self):
        sections = [
            {
                "section_name": "Test",
                "fields": [{"field_type": "singleLineText", "label": "Test Field"}],
            }
        ]

        client = dummy_app_definition_client()
        result = client.create_app(
            app_name="AB",
            requesting_user_email_address="admin@example.com",
            sections=sections,
        )

        assert result.success is False
        assert "1 validation error for CreateAppRequest" in result.message

    def test_create_app_tool_email_validation_error(self):
        sections = [
            {
                "section_name": "Test Section",
                "fields": [{"field_type": "singleLineText", "label": "Test Field"}],
            }
        ]

        client = dummy_app_definition_client()
        result = client.create_app(
            app_name="Valid App Name",
            requesting_user_email_address="invalid-email",
            sections=sections,
        )

        assert result.success is False
        assert "1 validation error for CreateAppRequest" in result.message

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_formula_field(self, mock_validate_env, mock_make_request):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (True, None, {"fieldName": "CALC_FIELD"})

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=1,
            field_index=3,
            field_type="calculationsAndLogic",
            label="Total Salary",
            required=False,
            formula="base_salary + bonus",
            hidden=False,
        )

        assert result.success is True
        assert "Successfully added calculationsAndLogic field" in result.message
        assert result.app_id == "MFX093412"
        assert result.field_name == "CALC_FIELD"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_conditional_field(
        self, mock_validate_env, mock_make_request
    ):
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (True, None, {"fieldName": "COND_FIELD"})

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=0,
            field_index=5,
            field_type="singleLineText",
            label="Manager Name",
            required=False,
            display_condition="employment_type == 'Full-time'",
            is_editable=True,
            editability_condition="user_role == 'admin'",
            description="Enter manager name for full-time employees",
        )

        assert result.success is True
        assert "Successfully added singleLineText field" in result.message
        assert result.app_id == "MFX093412"
        assert result.field_name == "COND_FIELD"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_get_definition_tool_api_error(self, mock_make_request):
        mock_make_request.return_value = (False, "API Error (403): Forbidden", None)

        client = dummy_app_definition_client()
        result = client.get_definition("MFX093412")

        assert result.success is False
        assert "API Error (403): Forbidden" in result.message
        assert result.app_id == "MFX093412"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_add_field_tool_environment_error(self, mock_validate_env):
        mock_validate_env.return_value = (False, "Invalid API configuration")

        client = dummy_app_definition_client()
        result = client.add_field(
            app_id="MFX093412",
            section_index=0,
            field_index=0,
            field_type="singleLineText",
            label="Test Field",
            required=True,
        )

        assert result.success is False
        assert "Invalid API configuration" in result.message
