from unittest.mock import patch
from clappia_api_tools.client.submission_client import SubmissionClient
from clappia_api_tools.models import (
    SubmissionFilters,
    SubmissionQueryGroup,
    SubmissionQuery,
    FilterCondition,
)
from clappia_api_tools.enums import FilterOperator, FilterKeyType, LogicalOperator


def dummy_submission_client():
    """Helper function to create a dummy submission client for testing"""
    return SubmissionClient(
        api_key="dummy_api_key",
        base_url="https://api.clappia.com",
        timeout=30,
    )


class TestSubmissionToolsIntegration:
    """Test cases for SubmissionClient integration"""

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_create_submission_tool(self, mock_validate_env, mock_make_request):
        """Test create_submission with successful response"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {"submissionId": "TEST123", "status": "created"},  # response_data
        )

        client = dummy_submission_client()
        result = client.create_submission(
            "MFX093412",
            {"name": "Test User"},
            "test@example.com",
        )

        # Verify response format based on actual client implementation
        assert "Successfully created submission" in result or result.success is True

        # Verify API was called correctly
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "submissions/create"
        assert call_args[1]["data"]["appId"] == "MFX093412"
        assert call_args[1]["data"]["data"] == {"name": "Test User"}

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_create_submission_with_complex_data(
        self, mock_validate_env, mock_make_request
    ):
        """Test create_submission with complex data structure"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {"submissionId": "COMPLEX123", "status": "created"},  # response_data
        )

        # Complex data with various field types
        complex_data = {
            "employee_name": "John Doe",
            "department": "Engineering",
            "salary": 75000,
            "start_date": "20-02-2025",
            "skills": ["Python", "JavaScript"],
            "is_manager": True,
            "location": "23.456789, 45.678901",
            "profile_image": [
                {
                    "s3Path": {
                        "bucket": "employee-files",
                        "key": "images/john_doe.jpg",
                        "makePublic": False,
                    }
                }
            ],
        }

        client = dummy_submission_client()
        result = client.create_submission("MFX093412", complex_data, "hr@example.com")

        # Verify response
        assert "Successfully created submission" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called with complex data
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["data"]["data"] == complex_data

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_edit_submission_tool(self, mock_validate_env, mock_make_request):
        """Test edit_submission with successful response"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {"submissionId": "HGO51464561", "status": "updated"},  # response_data
        )

        client = dummy_submission_client()
        result = client.edit_submission(
            "MFX093412",
            "HGO51464561",
            {"name": "Updated User"},
            "test@example.com",
        )

        # Verify response
        assert "Successfully edited submission" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called correctly
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "submissions/edit"
        assert call_args[1]["data"]["submissionId"] == "HGO51464561"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_edit_submission_partial_update(self, mock_validate_env, mock_make_request):
        """Test edit_submission with partial field updates"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {
                "submissionId": "HGO51464561",
                "status": "updated",
                "fieldsUpdated": 2,
            },  # response_data
        )

        # Partial update data
        update_data = {
            "salary": 80000,
            "department": "Senior Engineering",
            "last_updated": "11-08-2025",
        }

        client = dummy_submission_client()
        result = client.edit_submission(
            "MFX093412", "HGO51464561", update_data, "manager@example.com"
        )

        # Verify response
        assert "Successfully edited submission" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called with partial data
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["data"]["data"] == update_data

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_update_submission_owners_tool(self, mock_validate_env, mock_make_request):
        """Test update_owners with successful response"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {"submissionId": "HGO51464561", "ownersUpdated": 2},  # response_data
        )

        client = dummy_submission_client()
        result = client.update_owners(
            "MFX093412",
            "HGO51464561",
            "admin@example.com",
            ["user1@company.com", "user2@company.com"],
        )

        # Verify response
        assert "Successfully updated submission owners" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called correctly
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "submissions/updateSubmissionOwners"
        assert call_args[1]["data"]["emailIds"] == [
            "user1@company.com",
            "user2@company.com",
        ]

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_update_submission_owners_multiple_users(
        self, mock_validate_env, mock_make_request
    ):
        """Test update_owners with multiple users"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {"submissionId": "HGO51464561", "ownersUpdated": 5},  # response_data
        )

        # Multiple users list
        email_list = [
            "user1@company.com",
            "user2@company.com",
            "user3@company.com",
            "manager@company.com",
            "admin@company.com",
        ]

        client = dummy_submission_client()
        result = client.update_owners(
            "MFX093412", "HGO51464561", "admin@example.com", email_list
        )

        # Verify response
        assert "Successfully updated submission owners" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called with all users
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert len(call_args[1]["data"]["emailIds"]) == 5
        assert call_args[1]["data"]["emailIds"] == email_list

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_update_submission_status_tool(self, mock_validate_env, mock_make_request):
        """Test update_status with successful response"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {
                "submissionId": "HGO51464561",
                "statusUpdated": "Approved",
            },  # response_data
        )

        client = dummy_submission_client()
        result = client.update_status(
            "MFX093412",
            "HGO51464561",
            "admin@example.com",
            "Approved",
            "Reviewed and approved by manager",
        )

        # Verify response
        assert "Successfully updated submission status" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called correctly
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "submissions/updateStatus"
        assert call_args[1]["data"]["status"]["name"] == "Approved"
        assert (
            call_args[1]["data"]["status"]["comments"]
            == "Reviewed and approved by manager"
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_update_submission_status_different_statuses(
        self, mock_validate_env, mock_make_request
    ):
        """Test update_status with different status values"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {"submissionId": "HGO51464561", "statusUpdated": True},  # response_data
        )

        # Test different status transitions
        status_transitions = [
            ("Pending", "Under review by team lead"),
            ("In Review", "Technical review in progress"),
            ("Rejected", "Missing required documentation"),
            ("Approved", "All criteria met"),
            ("On Hold", "Waiting for additional information"),
            ("Completed", "Process finished successfully"),
        ]

        client = dummy_submission_client()

        for status, comment in status_transitions:
            mock_make_request.reset_mock()  # Reset mock for each iteration

            result = client.update_status(
                "MFX093412", "HGO51464561", "admin@example.com", status, comment
            )

            # Verify response
            assert "Successfully updated submission status" in result or (
                hasattr(result, "success") and result.success is True
            )

            # Verify API was called with correct status
            mock_make_request.assert_called_once()
            call_args = mock_make_request.call_args
            assert call_args[1]["data"]["status"]["name"] == status
            assert call_args[1]["data"]["status"]["comments"] == comment

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_submissions_tool(self, mock_validate_env, mock_make_request):
        """Test get_submissions with successful response"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {  # response_data
                "submissions": [
                    {
                        "submissionId": "SUB001",
                        "name": "John Doe",
                        "department": "Engineering",
                    },
                    {
                        "submissionId": "SUB002",
                        "name": "Jane Smith",
                        "department": "Marketing",
                    },
                ],
                "totalCount": 2,
                "hasMore": False,
            },
        )

        client = dummy_submission_client()
        result = client.get_submissions("MFX093412", "admin@example.com")

        # Verify response
        assert "Successfully retrieved submissions" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called correctly
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "submissions/getSubmissions"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_submissions_with_filters(self, mock_validate_env, mock_make_request):
        """Test get_submissions with properly structured filters"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {  # response_data
                "submissions": [
                    {
                        "submissionId": "SUB001",
                        "name": "John Doe",
                        "department": "Engineering",
                        "salary": 75000,
                    }
                ],
                "totalCount": 1,
                "hasMore": False,
            },
        )

        filters = SubmissionFilters(
            queries=[
                SubmissionQueryGroup(
                    queries=[
                        SubmissionQuery(
                            conditions=[
                                FilterCondition(
                                    operator=FilterOperator.EQ,
                                    filter_key_type=FilterKeyType.CUSTOM,
                                    key="department",
                                    value="Engineering",
                                ),
                                FilterCondition(
                                    operator=FilterOperator.GTE,
                                    filter_key_type=FilterKeyType.CUSTOM,
                                    key="salary",
                                    value=7000,
                                ),
                                FilterCondition(
                                    operator=FilterOperator.GTE,
                                    filter_key_type=FilterKeyType.STANDARD,
                                    key="$createdAt",
                                    value="01-01-2025",
                                ),
                            ],
                            operator=LogicalOperator.AND,
                        )
                    ]
                )
            ]
        )

        client = dummy_submission_client()
        result = client.get_submissions(
            "MFX093412", "admin@example.com", filters=filters
        )

        # Verify response
        assert "Successfully retrieved submissions" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called with proper filters
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert "filters" in call_args[1]["data"]

    def test_create_submission_validation_error(self):
        """Test create_submission with validation errors"""
        client = dummy_submission_client()

        # Test invalid app_id
        result = client.create_submission(
            "invalid-id", {"name": "Test"}, "test@example.com"
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

        # Test empty data
        result = client.create_submission("MFX093412", {}, "test@example.com")
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

        # Test invalid email
        result = client.create_submission(
            "MFX093412", {"name": "Test"}, "invalid-email"
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

    def test_edit_submission_validation_error(self):
        """Test edit_submission with validation errors"""
        client = dummy_submission_client()

        # Test invalid submission_id
        result = client.edit_submission(
            "MFX093412", "invalid-id", {"name": "Test"}, "test@example.com"
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

        # Test invalid app_id
        result = client.edit_submission(
            "invalid-id", "HGO51464561", {"name": "Test"}, "test@example.com"
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

    def test_update_owners_validation_error(self):
        """Test update_owners with validation errors"""
        client = dummy_submission_client()

        # Test empty email list
        result = client.update_owners(
            "MFX093412", "HGO51464561", "admin@example.com", []
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

        # Test invalid email in list
        result = client.update_owners(
            "MFX093412", "HGO51464561", "admin@example.com", ["invalid-email"]
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

    def test_update_status_validation_error(self):
        """Test update_status with validation errors"""
        client = dummy_submission_client()

        # Test empty status name
        result = client.update_status(
            "MFX093412", "HGO51464561", "admin@example.com", "", "comment"
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

        # Test invalid app_id
        result = client.update_status(
            "invalid-id", "HGO51464561", "admin@example.com", "Approved", "comment"
        )
        assert "Error" in result or (
            hasattr(result, "success") and result.success is False
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    def test_submission_api_error_handling(self, mock_make_request):
        """Test submission client API error handling"""
        # Mock API error response
        mock_make_request.return_value = (
            False,  # success
            "API Error (400): Bad Request - Invalid submission data",  # error_message
            None,  # response_data
        )

        client = dummy_submission_client()
        result = client.create_submission(
            "MFX093412", {"name": "Test"}, "test@example.com"
        )

        # Verify error is handled
        assert "API Error (400)" in result or (
            hasattr(result, "success") and result.success is False
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_submission_environment_error(self, mock_validate_env):
        """Test submission client environment validation error"""
        # Mock environment validation failure
        mock_validate_env.return_value = (False, "Invalid API key or workplace ID")

        client = dummy_submission_client()
        result = client.create_submission(
            "MFX093412", {"name": "Test"}, "test@example.com"
        )

        # Verify error is handled
        assert "Invalid API key or workplace ID" in result or (
            hasattr(result, "success") and result.success is False
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_export_submissions_to_excel(self, mock_validate_env, mock_make_request):
        """Test export submissions to Excel format"""
        # Mock environment validation and API response
        mock_validate_env.return_value = (True, None)
        mock_make_request.return_value = (
            True,  # success
            None,  # error_message
            {  # response_data
                "exportUrl": "https://exports.clappia.com/excel/export123.xlsx",
                "fileName": "submissions_export.xlsx",
                "recordCount": 50,
            },
        )

        client = dummy_submission_client()
        result = client.get_submissions_in_excel(
            "MFX093412",
            "admin@example.com",
            field_names=["name", "department", "salary"],
            format="excel",
        )

        # Verify response
        assert "Successfully exported submissions" in result or (
            hasattr(result, "success") and result.success is True
        )

        # Verify API was called correctly
        mock_make_request.assert_called_once()
        call_args = mock_make_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["endpoint"] == "submissions/getSubmissionsExcel"
