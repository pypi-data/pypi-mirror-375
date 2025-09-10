from typing import Dict, Any, List, Optional
from .base_client import BaseClappiaClient
from clappia_api_tools.utils.logging_utils import get_logger
from clappia_api_tools.models.request import (
    GetSubmissionsRequest,
    GetSubmissionsAggregationRequest,
    CreateSubmissionRequest,
    EditSubmissionRequest,
    UpdateSubmissionStatusRequest,
    UpdateSubmissionOwnersRequest,
    GetSubmissionsInExcelRequest,
    GetSubmissionsCountRequest,
)
from clappia_api_tools.models.submission import (
    SubmissionFilters,
    AggregationDimension,
    AggregationMetric,
)
from clappia_api_tools.models.response import (
    SubmissionsAggregationResponse,
    SubmissionsResponse,
    SubmissionResponse,
    SubmissionsExcelResponse,
    SubmissionsCountResponse,
)

logger = get_logger(__name__)


class SubmissionClient(BaseClappiaClient):
    """Client for managing Clappia submissions.

    This client handles retrieving and managing submissions, including
    getting submissions, getting submissions aggregation, creating submissions,
    editing submissions, updating submission status, updating submission owners.
    """

    def get_submissions(
        self,
        app_id: str,
        fields: Optional[List[str]] = None,
        page_size: int = 10,
        forward: bool = True,
        filters: Optional[SubmissionFilters] = None,
        last_submission_id: Optional[str] = None,
    ) -> SubmissionsResponse:
        try:
            request = GetSubmissionsRequest(
                app_id=app_id,
                page_size=page_size,
                forward=forward,
                filters=filters,
                last_submission_id=last_submission_id,
                fields=fields,
            )
        except Exception as e:
            return SubmissionsResponse(success=False, message=str(e), app_id=app_id)

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionsResponse(success=False, message=env_error, app_id=app_id)

        payload = {
            "appId": request.app_id,
            "pageSize": request.page_size,
            "forward": request.forward,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()

        logger.info(
            f"Getting submissions for app_id: {app_id} with page_size: {page_size}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/getSubmissions", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionsResponse(
                success=False, message=error_message, app_id=app_id
            )

        submissions_count = (
            len(response_data.get("submissions", [])) if response_data else 0
        )

        return SubmissionsResponse(
            success=True,
            message=f"Successfully retrieved {submissions_count} submissions",
            app_id=app_id,
            metadata=response_data.get("metadata", {}),
            data=response_data.get("submissions", []),
        )

    def get_submissions_aggregation(
        self,
        app_id: str,
        dimensions: Optional[List[AggregationDimension]] = None,
        aggregation_dimensions: Optional[List[AggregationMetric]] = None,
        x_axis_labels: Optional[List[str]] = None,
        forward: bool = True,
        page_size: int = 1000,
        filters: Optional[SubmissionFilters] = None,
    ) -> SubmissionsAggregationResponse:
        try:
            request = GetSubmissionsAggregationRequest(
                app_id=app_id,
                dimensions=dimensions,
                aggregation_dimensions=aggregation_dimensions,
                x_axis_labels=x_axis_labels,
                forward=forward,
                page_size=page_size,
                filters=filters,
            )
        except Exception as e:
            return SubmissionsAggregationResponse(
                success=False, message=str(e), app_id=app_id
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionsAggregationResponse(
                success=False, message=env_error, app_id=app_id
            )

        if not request.dimensions and not request.aggregation_dimensions:
            return SubmissionsAggregationResponse(
                success=False,
                message="At least one dimension or aggregation dimension must be provided",
                app_id=app_id,
            )

        payload = {
            "appId": request.app_id,
            "forward": request.forward,
            "pageSize": request.page_size,
            "xAxisLabels": request.x_axis_labels or [],
        }

        if request.dimensions:
            payload["dimensions"] = [dim.to_dict() for dim in request.dimensions]
        if request.aggregation_dimensions:
            payload["aggregationDimensions"] = [
                agg.to_dict() for agg in request.aggregation_dimensions
            ]
        if request.filters:
            payload["filters"] = request.filters.to_dict()

        logger.info(
            f"Getting submissions aggregation for app_id: {app_id} with {len(request.dimensions or [])} dimensions and {len(request.aggregation_dimensions or [])} aggregation dimensions"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST",
            endpoint="submissions/getSubmissionsAggregation",
            data=payload,
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionsAggregationResponse(
                success=False, message=error_message, app_id=app_id
            )

        return SubmissionsAggregationResponse(
            success=True,
            message="Successfully retrieved aggregated data",
            app_id=app_id,
            data=response_data,
        )

    def create_submission(
        self,
        app_id: str,
        data: Dict[str, Any],
    ) -> SubmissionResponse:
        try:
            request = CreateSubmissionRequest(
                app_id=app_id,
                data=data,
            )
        except Exception as e:
            return SubmissionResponse(
                success=False,
                message=str(e),
                app_id=app_id,
                operation="create_submission",
            )

        if not data:
            return SubmissionResponse(
                success=False,
                message="data cannot be empty - at least one field is required",
                app_id=app_id,
                operation="create_submission",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                operation="create_submission",
            )

        payload = {
            "appId": request.app_id,
            "data": request.data,
        }

        logger.info(f"Creating submission for app_id: {app_id} with data: {data}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/create", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                operation="create_submission",
            )

        submission_id = response_data.get("submissionId") if response_data else None

        return SubmissionResponse(
            success=True,
            message="Successfully created submission",
            app_id=app_id,
            submission_id=submission_id,
            data=response_data,
            operation="create_submission",
        )

    def edit_submission(
        self,
        app_id: str,
        submission_id: str,
        data: Dict[str, Any],
    ) -> SubmissionResponse:
        try:
            request = EditSubmissionRequest(
                app_id=app_id,
                submission_id=submission_id,
                data=data,
            )
        except Exception as e:
            return SubmissionResponse(
                success=False,
                message=str(e),
                app_id=app_id,
                submission_id=submission_id,
                operation="edit_submission",
            )

        if not data:
            return SubmissionResponse(
                success=False,
                message="data cannot be empty - at least one field is required",
                app_id=app_id,
                submission_id=submission_id,
                operation="edit_submission",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                submission_id=submission_id,
                operation="edit_submission",
            )

        payload = {
            "appId": request.app_id,
            "submissionId": request.submission_id,
            "data": request.data,
        }

        logger.info(
            f"Editing submission {submission_id} for app_id: {app_id} with data: {data}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/edit", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                submission_id=submission_id,
                operation="edit_submission",
            )

        return SubmissionResponse(
            success=True,
            message=f"Successfully edited submission",
            app_id=app_id,
            submission_id=submission_id,
            data=response_data,
            operation="edit_submission",
        )

    def update_status(
        self,
        app_id: str,
        submission_id: str,
        status_name: str,
        comments: Optional[str] = None,
    ) -> SubmissionResponse:
        try:
            request = UpdateSubmissionStatusRequest(
                app_id=app_id,
                submission_id=submission_id,
                status_name=status_name,
                comments=comments,
            )
        except Exception as e:
            return SubmissionResponse(
                success=False,
                message=str(e),
                app_id=app_id,
                submission_id=submission_id,
                operation="update_status",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                submission_id=submission_id,
                operation="update_status",
            )

        status = {
            "name": request.status_name.strip(),
            "comments": request.comments.strip() if request.comments else None,
        }

        payload = {
            "appId": request.app_id,
            "submissionId": request.submission_id,
            "status": status,
        }

        logger.info(f"Updating status for submission {submission_id} to {status_name}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/updateStatus", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                submission_id=submission_id,
                operation="update_status",
            )

        return SubmissionResponse(
            success=True,
            message=f"Successfully updated status to '{status_name} and added comments '{comments}'",
            app_id=app_id,
            submission_id=submission_id,
            data=response_data,
            operation="update_status",
        )

    def update_owners(
        self,
        app_id: str,
        submission_id: str,
        email_ids: List[str],
        phone_numbers: Optional[List[str]] = None,
    ) -> SubmissionResponse:
        try:
            request = UpdateSubmissionOwnersRequest(
                app_id=app_id,
                submission_id=submission_id,
                email_ids=email_ids,
                phone_numbers=phone_numbers,
            )
        except Exception as e:
            return SubmissionResponse(
                success=False,
                message=str(e),
                app_id=app_id,
                submission_id=submission_id,
                operation="update_owners",
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionResponse(
                success=False,
                message=env_error,
                app_id=app_id,
                submission_id=submission_id,
                operation="update_owners",
            )

        payload = {
            "appId": request.app_id,
            "submissionId": request.submission_id,
            "emailIds": [str(email) for email in request.email_ids],
        }

        logger.info(f"Updating owners for submission {submission_id}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/updateSubmissionOwners", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionResponse(
                success=False,
                message=error_message,
                app_id=app_id,
                submission_id=submission_id,
                operation="update_owners",
            )

        return SubmissionResponse(
            success=True,
            message=f"Successfully updated owners for owners {', '.join(request.email_ids)}",
            app_id=app_id,
            submission_id=submission_id,
            data=response_data,
            operation="update_owners",
        )

    def get_submissions_in_excel(
        self,
        app_id: str,
        requesting_user_email_address: str,
        filters: Optional[SubmissionFilters] = None,
        field_names: Optional[List[str]] = None,
        format: str = "Excel",
    ) -> SubmissionsExcelResponse:
        try:
            request = GetSubmissionsInExcelRequest(
                app_id=app_id,
                requesting_user_email_address=requesting_user_email_address,
                filters=filters,
                field_names=field_names,
                format=format,
            )
        except Exception as e:
            return SubmissionsExcelResponse(
                success=False, message=str(e), app_id=app_id
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionsExcelResponse(
                success=False, message=env_error, app_id=app_id
            )

        payload = {
            "appId": request.app_id,
            "requestingUserEmailAddress": str(request.requesting_user_email_address),
            "format": request.format,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()
        if request.field_names:
            payload["fieldNames"] = request.field_names

        logger.info(
            f"Getting submissions in Excel for app_id: {app_id} with format: {format}"
        )

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/getSubmissionsExcel", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionsExcelResponse(
                success=False, message=error_message, app_id=app_id
            )

        if response_data.get("statusCode") == 202:
            return SubmissionsExcelResponse(
                success=True,
                message=f"The {format} file has been sent to {requesting_user_email_address}",
                app_id=app_id,
                format=format,
                requesting_user_email_address=requesting_user_email_address,
            )
        else:
            return SubmissionsExcelResponse(
                success=True,
                message="Excel file generated successfully and will be sent to the requesting user email address since the submissions are large in number",
                app_id=app_id,
                url=response_data.get("url"),
                format=format,
                requesting_user_email_address=requesting_user_email_address,
            )

    def get_submissions_count(
        self,
        app_id: str,
        filters: Optional[SubmissionFilters] = None,
    ) -> SubmissionsCountResponse:
        try:
            request = GetSubmissionsCountRequest(
                app_id=app_id,
                filters=filters,
            )
        except Exception as e:
            return SubmissionsCountResponse(
                success=False, message=str(e), app_id=app_id
            )

        env_valid, env_error = self.api_utils.validate_environment()
        if not env_valid:
            return SubmissionsCountResponse(
                success=False, message=env_error, app_id=app_id
            )

        payload = {
            "appId": request.app_id,
        }

        if request.filters:
            payload["filters"] = request.filters.to_dict()

        logger.info(f"Getting submissions count for app_id: {app_id}")

        success, error_message, response_data = self.api_utils.make_request(
            method="POST", endpoint="submissions/getSubmissionsCount", data=payload
        )

        if not success:
            logger.error(f"Error: {error_message}")
            return SubmissionsCountResponse(
                success=False, message=error_message, app_id=app_id
            )

        return SubmissionsCountResponse(
            success=True,
            message="Successfully retrieved submissions count",
            app_id=app_id,
            total_count=response_data.get("totalCount"),
            filtered_count=response_data.get("filteredCount"),
        )
