from unittest.mock import patch, Mock
from clappia_api_tools.client.base_client import BaseClappiaClient
from clappia_api_tools.client.submission_client import SubmissionClient
from clappia_api_tools.client.app_definition_client import AppDefinitionClient


class TestBaseClappiaClient:
    """Test cases for BaseClappiaClient"""

    @patch("clappia_api_tools.client.base_client.ClappiaAPIUtils")
    def test_init_with_defaults(self, mock_api_utils):
        """Test BaseClappiaClient initialization with default parameters"""
        client = BaseClappiaClient()
        assert client.api_utils is not None
        mock_api_utils.assert_called_once_with(None, None, 30)

    @patch("clappia_api_tools.client.base_client.ClappiaAPIUtils")
    def test_init_with_custom_params(self, mock_api_utils):
        """Test BaseClappiaClient initialization with custom parameters"""
        client = BaseClappiaClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        assert client.api_utils is not None
        mock_api_utils.assert_called_once_with("test_key", "https://test.com", 60)


class TestSubmissionClient:
    """Test cases for SubmissionClient"""

    def test_create_submission_validation_error(self):
        """Test create_submission with invalid app_id"""
        client = SubmissionClient()
        result = client.create_submission("invalid-id", {}, "test@example.com")
        assert result.success is False
        assert (
            "App ID must contain only uppercase letters and numbers" in result.message
        )

    def test_create_submission_empty_email(self):
        """Test create_submission with empty email"""
        client = SubmissionClient()
        result = client.create_submission("MFX093412", {"test": "data"}, "")
        assert result.success is False

    def test_create_submission_invalid_email(self):
        """Test create_submission with invalid email format"""
        client = SubmissionClient()
        result = client.create_submission(
            "MFX093412", {"test": "data"}, "invalid-email"
        )
        assert result.success is False

    def test_create_submission_empty_data(self):
        """Test create_submission with empty data"""
        client = SubmissionClient()
        result = client.create_submission("MFX093412", {}, "test@example.com")
        assert result.success is False
        assert "data cannot be empty" in result.message

    def test_create_submission_invalid_data_type(self):
        """Test create_submission with non-dictionary data"""
        client = SubmissionClient()
        result = client.create_submission("MFX093412", "invalid", "test@example.com")
        assert result.success is False
        assert "data" in result.message

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_create_submission_success(self, mock_request):
        """Test successful create_submission"""
        # Mock successful API response
        mock_request.return_value = (True, None, {"submissionId": "TEST123"})

        client = SubmissionClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.create_submission(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

        assert result.success is True
        assert "Successfully created submission" in result.message
        assert result.submission_id == "TEST123"
        mock_request.assert_called_once()

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_create_submission_api_error(self, mock_request):
        """Test create_submission with API error"""
        # Mock API error response
        mock_request.return_value = (False, "API Error: Invalid request", None)

        client = SubmissionClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.create_submission(
            "MFX093412", {"name": "Test User"}, "test@example.com"
        )

        assert result.success is False
        assert "API Error: Invalid request" in result.message

    def test_edit_submission_invalid_submission_id(self):
        """Test edit_submission with invalid submission ID"""
        client = SubmissionClient()
        result = client.edit_submission(
            "MFX093412", "invalid-id", {"name": "Updated"}, "test@example.com"
        )
        assert result.success is False
        assert (
            "Submission ID must contain only uppercase letters and numbers"
            in result.message
        )


class TestAppDefinitionClient:
    """Test cases for AppDefinitionClient"""

    def test_get_definition_invalid_app_id(self):
        """Test get_definition with invalid app_id"""
        client = AppDefinitionClient()
        result = client.get_definition("invalid-app-id")
        assert result.success is False
        assert (
            "App ID must contain only uppercase letters and numbers" in result.message
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_get_definition_success(self, mock_request):
        """Test successful get_definition"""
        mock_response = {
            "appId": "MFX093412",
            "version": "1.0",
            "state": "active",
            "pageIds": ["page1", "page2"],
            "sectionIds": ["section1"],
            "fieldDefinitions": {"field1": {}, "field2": {}},
            "metadata": {"sectionName": "Test App", "description": "Test Description"},
        }
        mock_request.return_value = (True, None, mock_response)

        client = AppDefinitionClient()
        result = client.get_definition("MFX093412")

        assert result.success is True
        assert "Successfully retrieved app definition" in result.message
        assert result.app_id == "MFX093412"
        mock_request.assert_called_once()

    def test_create_app_invalid_name(self):
        """Test create_app with invalid app name"""
        client = AppDefinitionClient()
        result = client.create_app("", "test@example.com", [])
        assert result.success is False
        assert "name" in result.message

    def test_create_app_invalid_email(self):
        """Test create_app with invalid email"""
        client = AppDefinitionClient()
        result = client.create_app("Valid App Name", "invalid-email", [])
        assert result.success is False
        assert "requesting_user_email_address" in result.message

    def test_add_field_invalid_app_id(self):
        """Test add_field with invalid app_id"""
        client = AppDefinitionClient()
        result = client.add_field(
            "invalid-id", "test@example.com", 0, 0, "singleLineText", "Test Field", True
        )
        assert result.success is False
        assert (
            "App ID must contain only uppercase letters and numbers" in result.message
        )

    def test_add_field_unknown_field_type(self):
        """Test add_field with unknown field type"""
        client = AppDefinitionClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.add_field(
            "MFX093412",
            "test@example.com",
            0,
            0,
            "unknownFieldType",
            "Test Field",
            True,
        )
        assert result.success is False
        assert "field_type" in result.message
