from typing import Dict, Any, Optional
from .base_client import BaseClappiaClient
from clappia_api_tools.utils.logging_utils import get_logger
from clappia_api_tools.models.request import (
    UpsertSummaryChartDefinitionRequest,
    UpsertBarChartDefinitionRequest,
    UpsertPieChartDefinitionRequest,
    UpsertDoughnutChartDefinitionRequest,
    UpsertLineChartDefinitionRequest,
    UpsertDataTableChartDefinitionRequest,
    UpsertMapChartDefinitionRequest,
    UpsertGanttChartDefinitionRequest,
)
from clappia_api_tools.models.response import ChartResponse, BaseResponse
from clappia_api_tools.enums import ChartType

logger = get_logger(__name__)


class AnalyticsClient(BaseClappiaClient):
    """Client for managing Clappia analytics and charts.

    This client handles retrieving and managing analytics configurations, including
    adding charts, removing charts, updating charts, and reordering charts.
    """

    def add_summary_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertSummaryChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a summary chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_summary_chart",
                chart_type=ChartType.SUMMARY_CARD.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.SUMMARY_CARD.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding summary chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_summary_chart",
                chart_type=ChartType.SUMMARY_CARD.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added summary chart",
            app_id=app_id,
            chart_type=ChartType.SUMMARY_CARD.value,
            operation="add_summary_chart",
            data=response_data,
        )

    def update_summary_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertSummaryChartDefinitionRequest,
    ) -> ChartResponse:
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_summary_chart",
                chart_type=ChartType.SUMMARY_CARD.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.SUMMARY_CARD.value,
            **request.to_json(),
        }
        logger.info(
            f"Updating summary chart for app_id: {app_id} at index {chart_index}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_summary_chart",
            )

        return ChartResponse(
            success=True,
            message="Successfully updated summary chart",
            app_id=app_id,
            operation="update_summary_chart",
            data=response_data,
        )

    def add_bar_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertBarChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a bar chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_bar_chart",
                chart_type=ChartType.BAR_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.BAR_CHART.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding bar chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_bar_chart",
                chart_type=ChartType.BAR_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added bar chart",
            app_id=app_id,
            chart_type=ChartType.BAR_CHART.value,
            operation="add_bar_chart",
            data=response_data,
        )

    def update_bar_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertBarChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a bar chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_bar_chart",
                chart_type=ChartType.BAR_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.BAR_CHART.value,
            **request.to_json(),
        }
        logger.info(f"Updating bar chart for app_id: {app_id} at index {chart_index}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_bar_chart",
                chart_type=ChartType.BAR_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated bar chart",
            app_id=app_id,
            operation="update_bar_chart",
            chart_type=ChartType.BAR_CHART.value,
            data=response_data,
        )

    def add_pie_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertPieChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a pie chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_pie_chart",
                chart_type=ChartType.PIE_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.PIE_CHART.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding pie chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_pie_chart",
                chart_type=ChartType.PIE_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added pie chart",
            app_id=app_id,
            chart_type=ChartType.PIE_CHART.value,
            operation="add_pie_chart",
            data=response_data,
        )

    def update_pie_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertPieChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a pie chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_pie_chart",
                chart_type=ChartType.PIE_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.PIE_CHART.value,
            **request.to_json(),
        }
        logger.info(f"Updating pie chart for app_id: {app_id} at index {chart_index}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_pie_chart",
                chart_type=ChartType.PIE_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated pie chart",
            app_id=app_id,
            operation="update_pie_chart",
            chart_type=ChartType.PIE_CHART.value,
            data=response_data,
        )

    def add_doughnut_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertDoughnutChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a doughnut chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_doughnut_chart",
                chart_type=ChartType.DOUGHNUT_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.DOUGHNUT_CHART.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding doughnut chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_doughnut_chart",
                chart_type=ChartType.DOUGHNUT_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added doughnut chart",
            app_id=app_id,
            chart_type=ChartType.DOUGHNUT_CHART.value,
            operation="add_doughnut_chart",
            data=response_data,
        )

    def update_doughnut_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertDoughnutChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a doughnut chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_doughnut_chart",
                chart_type=ChartType.DOUGHNUT_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.DOUGHNUT_CHART.value,
            **request.to_json(),
        }
        logger.info(
            f"Updating doughnut chart for app_id: {app_id} at index {chart_index}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_doughnut_chart",
                chart_type=ChartType.DOUGHNUT_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated doughnut chart",
            app_id=app_id,
            operation="update_doughnut_chart",
            chart_type=ChartType.DOUGHNUT_CHART.value,
            data=response_data,
        )

    def add_line_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertLineChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a line chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_line_chart",
                chart_type=ChartType.LINE_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.LINE_CHART.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding line chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_line_chart",
                chart_type=ChartType.LINE_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added line chart",
            app_id=app_id,
            chart_type=ChartType.LINE_CHART.value,
            operation="add_line_chart",
            data=response_data,
        )

    def update_line_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertLineChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a line chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_line_chart",
                chart_type=ChartType.LINE_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.LINE_CHART.value,
            **request.to_json(),
        }
        logger.info(f"Updating line chart for app_id: {app_id} at index {chart_index}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_line_chart",
                chart_type=ChartType.LINE_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated line chart",
            app_id=app_id,
            operation="update_line_chart",
            chart_type=ChartType.LINE_CHART.value,
            data=response_data,
        )

    def add_data_table_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertDataTableChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a data table chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_data_table_chart",
                chart_type=ChartType.DATA_TABLE.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.DATA_TABLE.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding data table chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_data_table_chart",
                chart_type=ChartType.DATA_TABLE.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added data table chart",
            app_id=app_id,
            chart_type=ChartType.DATA_TABLE.value,
            operation="add_data_table_chart",
            data=response_data,
        )

    def update_data_table_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertDataTableChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a data table chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_data_table_chart",
                chart_type=ChartType.DATA_TABLE.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.DATA_TABLE.value,
            **request.to_json(),
        }
        logger.info(
            f"Updating data table chart for app_id: {app_id} at index {chart_index}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_data_table_chart",
                chart_type=ChartType.DATA_TABLE.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated data table chart",
            app_id=app_id,
            operation="update_data_table_chart",
            chart_type=ChartType.DATA_TABLE.value,
            data=response_data,
        )

    def add_map_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertMapChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a map chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_map_chart",
                chart_type=ChartType.MAP_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.MAP_CHART.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding map chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_map_chart",
                chart_type=ChartType.MAP_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added map chart",
            app_id=app_id,
            chart_type=ChartType.MAP_CHART.value,
            operation="add_map_chart",
            data=response_data,
        )

    def update_map_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertMapChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a map chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_map_chart",
                chart_type=ChartType.MAP_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.MAP_CHART.value,
            **request.to_json(),
        }
        logger.info(f"Updating map chart for app_id: {app_id} at index {chart_index}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_map_chart",
                chart_type=ChartType.MAP_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated map chart",
            app_id=app_id,
            operation="update_map_chart",
            chart_type=ChartType.MAP_CHART.value,
            data=response_data,
        )

    def add_gantt_chart(
        self,
        app_id: str,
        chart_index: int,
        chart_title: str,
        request: UpsertGanttChartDefinitionRequest,
    ) -> ChartResponse:
        """Add a Gantt chart to an app.

        Args:
            app_id: The ID of the app to add the chart to
            chart_index: The index of the chart to add
            chart_title: The title of the chart
            request: The request object containing the chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="add_gantt_chart",
                chart_type=ChartType.GANTT_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartTitle": chart_title,
            "chartType": ChartType.GANTT_CHART.value,
            **request.to_json(),
        }

        logger.info(
            f"Adding Gantt chart for app_id: {app_id} at index {chart_index} with title {chart_title}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/addChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="add_gantt_chart",
                chart_type=ChartType.GANTT_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully added Gantt chart",
            app_id=app_id,
            chart_type=ChartType.GANTT_CHART.value,
            operation="add_gantt_chart",
            data=response_data,
        )

    def update_gantt_chart(
        self,
        app_id: str,
        chart_index: int,
        request: UpsertGanttChartDefinitionRequest,
    ) -> ChartResponse:
        """Update a Gantt chart in an app.

        Args:
            app_id: The ID of the app containing the chart
            chart_index: The index of the chart to update
            request: The request object containing the updated chart configuration

        Returns:
            ChartResponse: Response containing the result of the operation
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="update_gantt_chart",
                chart_type=ChartType.GANTT_CHART.value,
            )

        payload = {
            "appId": app_id,
            "chartIndex": chart_index,
            "chartType": ChartType.GANTT_CHART.value,
            **request.to_json(),
        }
        logger.info(f"Updating Gantt chart for app_id: {app_id} at index {chart_index}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/updateChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="update_gantt_chart",
                chart_type=ChartType.GANTT_CHART.value,
            )

        return ChartResponse(
            success=True,
            message="Successfully updated Gantt chart",
            app_id=app_id,
            operation="update_gantt_chart",
            chart_type=ChartType.GANTT_CHART.value,
            data=response_data,
        )

    def reorder_chart(
        self,
        app_id: str,
        source_index: int,
        target_index: int,
    ) -> ChartResponse:

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return ChartResponse(
                success=False, message=env_error, app_id=app_id, operation="reorder"
            )

        payload = {
            "appId": app_id,
            "sourceIndex": source_index,
            "targetIndex": target_index,
        }

        logger.info(
            f"Reordering chart for app_id: {app_id} from index {source_index} to {target_index}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="analytics/reorderChart", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return ChartResponse(
                success=False, message=error_message, app_id=app_id, operation="reorder"
            )

        return ChartResponse(
            success=True,
            message="Successfully reordered chart",
            app_id=app_id,
            operation="reorder",
            data=response_data,
        )

    def get_charts(self, app_id: str) -> BaseResponse:
        """Get all charts for a specific app.

        Args:
            app_id: The ID of the app to get charts for

        Returns:
            BaseResponse : Response containing the list of charts
        """
        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return BaseResponse(
                success=False, message=env_error, operation="get_charts"
            )
        params = {
            "appId": app_id,
        }

        logger.info(f"Getting charts for app_id: {app_id}")

        success, error_message, response_data = self.api_utils.make_request(
            method="GET", endpoint="analytics/getAppCharts", params=params
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return BaseResponse(
                success=False, message=error_message, operation="get_charts"
            )
        return BaseResponse(
            success=True,
            message="Successfully retrieved charts",
            operation="get_charts",
            data=response_data,
        )
