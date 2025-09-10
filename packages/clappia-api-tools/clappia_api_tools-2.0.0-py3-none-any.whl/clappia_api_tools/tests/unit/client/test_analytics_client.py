from unittest.mock import patch, Mock
import pytest
from clappia_api_tools.client.analytics_client import AnalyticsClient
from clappia_api_tools.enums import ChartType


class TestAnalyticsClient:
    """Test cases for AnalyticsClient"""

    def test_get_charts_validation_error(self):
        """Test get_charts with invalid app_id"""
        client = AnalyticsClient()
        result = client.get_charts("invalid-id")
        assert result.success is False
        assert (
            "App ID must contain only uppercase letters and numbers" in result.message
        )

    def test_get_charts_empty_app_id(self):
        """Test get_charts with empty app_id"""
        client = AnalyticsClient()
        result = client.get_charts("")
        assert result.success is False
        assert "App ID is required and cannot be empty" in result.message

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_charts_success_with_charts(self, mock_validate_env, mock_request):
        """Test successful get_charts with charts data"""
        # Mock environment validation
        mock_validate_env.return_value = (True, None)

        # Mock successful API response with charts data
        mock_response_data = {
            "charts": [
                {
                    "chartId": "chart1",
                    "chartType": "pieChart",
                    "chartTitle": "Test Pie Chart",
                    "configuration": {"key": "value"},
                },
                {
                    "chartId": "chart2",
                    "chartType": "barGraph",
                    "chartTitle": "Test Bar Chart",
                    "configuration": None,
                },
            ]
        }
        mock_request.return_value = (True, None, mock_response_data)

        client = AnalyticsClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.get_charts("MFX093412")

        assert result.success is True
        assert "Successfully retrieved charts" in result.message
        assert result.app_id == "MFX093412"
        assert result.operation == "get"
        assert len(result.charts) == 2

        # Verify first chart
        assert result.charts[0].chart_id == "chart1"
        assert result.charts[0].chart_type == ChartType.PIE_CHART
        assert result.charts[0].chart_title == "Test Pie Chart"
        assert result.charts[0].configuration == {"key": "value"}

        # Verify second chart
        assert result.charts[1].chart_id == "chart2"
        assert result.charts[1].chart_type == ChartType.BAR_GRAPH
        assert result.charts[1].chart_title == "Test Bar Chart"
        assert result.charts[1].configuration is None

        mock_request.assert_called_once_with(
            method="POST", endpoint="analytics/getCharts", data={"appId": "MFX093412"}
        )

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_charts_success_no_charts(self, mock_validate_env, mock_request):
        """Test successful get_charts with no charts data"""
        # Mock environment validation
        mock_validate_env.return_value = (True, None)

        # Mock successful API response with no charts
        mock_response_data = {"charts": []}
        mock_request.return_value = (True, None, mock_response_data)

        client = AnalyticsClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.get_charts("MFX093412")

        assert result.success is True
        assert "Successfully retrieved charts" in result.message
        assert result.app_id == "MFX093412"
        assert result.operation == "get"
        assert result.charts is None  # No charts in response

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_charts_api_error(self, mock_validate_env, mock_request):
        """Test get_charts with API error"""
        # Mock environment validation
        mock_validate_env.return_value = (True, None)

        # Mock API error response
        mock_request.return_value = (False, "API Error: Invalid request", None)

        client = AnalyticsClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.get_charts("MFX093412")

        assert result.success is False
        assert "API Error: Invalid request" in result.message
        assert result.app_id == "MFX093412"
        assert result.operation == "get"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_charts_environment_error(self, mock_validate_env):
        """Test get_charts with environment validation error"""
        # Mock environment validation failure
        mock_validate_env.return_value = (False, "Environment validation failed")

        client = AnalyticsClient()
        result = client.get_charts("MFX093412")

        assert result.success is False
        assert "Environment validation failed" in result.message
        assert result.app_id == "MFX093412"
        assert result.operation == "get"

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_charts_malformed_response(self, mock_validate_env, mock_request):
        """Test get_charts with malformed response data"""
        # Mock environment validation
        mock_validate_env.return_value = (True, None)

        # Mock successful API response but with malformed chart data
        mock_response_data = {
            "charts": [
                {
                    "chartId": "chart1",
                    "chartType": "invalidType",  # Invalid chart type
                    "chartTitle": "Test Chart",
                }
            ]
        }
        mock_request.return_value = (True, None, mock_response_data)

        client = AnalyticsClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.get_charts("MFX093412")

        # Should still succeed but with warning logged for malformed chart
        assert result.success is True
        assert "Successfully retrieved charts" in result.message
        assert result.app_id == "MFX093412"
        assert result.operation == "get"
        # Charts should be None due to parsing error
        assert result.charts is None

    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.make_request")
    @patch("clappia_api_tools.utils.api_utils.ClappiaAPIUtils.validate_environment")
    def test_get_charts_no_response_data(self, mock_validate_env, mock_request):
        """Test get_charts with no response data"""
        # Mock environment validation
        mock_validate_env.return_value = (True, None)

        # Mock successful API response but with no data
        mock_request.return_value = (True, None, None)

        client = AnalyticsClient(
            api_key="test_key",
            base_url="https://test.com",
            timeout=60,
        )
        result = client.get_charts("MFX093412")

        assert result.success is True
        assert "Successfully retrieved charts" in result.message
        assert result.app_id == "MFX093412"
        assert result.operation == "get"
        assert result.charts is None
