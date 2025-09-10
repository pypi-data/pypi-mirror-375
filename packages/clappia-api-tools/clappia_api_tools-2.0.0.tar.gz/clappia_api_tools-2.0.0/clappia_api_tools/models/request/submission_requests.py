from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from ..submission import (
    SubmissionFilters,
    AggregationDimension,
    AggregationMetric,
    SubmissionQuery,
)


class BaseSubmissionRequest(BaseModel):
    app_id: str = Field(description="App Id")

    @field_validator("app_id")
    def validate_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("App ID is required and cannot be empty")
        if not re.match(r"^[A-Z0-9]+$", v.strip()):
            raise ValueError("App ID must contain only uppercase letters and numbers")
        return v.strip()


class GetSubmissionsRequest(BaseSubmissionRequest):
    page_size: int = Field(
        default=10, ge=1, le=1000, description="Number of submissions per page"
    )
    forward: bool = Field(default=True, description="Direction for pagination")
    filters: Optional[SubmissionFilters] = Field(None, description="Optional filters")
    last_submission_id: Optional[str] = Field(
        None, description="Last submission ID, next page will be fetched from this ID"
    )
    fields: Optional[List[str]] = Field(
        None,
        description="List of fields to include in the response, both standard and custom fields",
    )


class GetSubmissionsAggregationRequest(BaseSubmissionRequest):
    forward: bool = Field(default=True, description="Direction for pagination")
    dimensions: Optional[List[AggregationDimension]] = Field(
        None, description="Fields to group by"
    )
    aggregation_dimensions: Optional[List[AggregationMetric]] = Field(
        None, description="Aggregation calculations"
    )
    x_axis_labels: Optional[List[str]] = Field(
        None, description="X-axis labels for charts"
    )
    page_size: int = Field(
        default=1000, ge=1, le=1000, description="Number of results per page"
    )
    filters: Optional[SubmissionFilters] = Field(None, description="Optional filters")


class CreateSubmissionRequest(BaseSubmissionRequest):
    data: Dict[str, Any] = Field(
        description="Submission data, in the format of a dictionary. Example {'employee_name': 'Jane Doe', 'department': 'HR', 'salary': 60000, 'start_date': '10-02-2024', 'location':'23.456789, 45.678901', 'image_field_name': [{\"s3Path\": {\"bucket\": \"my-files-bucket\", \"key\": \"images/photo.jpg\", \"makePublic\": false}}]}"
    )


class EditSubmissionRequest(BaseSubmissionRequest):
    submission_id: str = Field(description="Submission Id to edit")
    data: Dict[str, Any] = Field(
        description="Updated submission data, in the format of a dictionary. Example {'employee_name': 'Jane Doe', 'department': 'HR', 'salary': 60000, 'start_date': '10-02-2024', 'location':'23.456789, 45.678901', 'image_field_name': [{\"s3Path\": {\"bucket\": \"my-files-bucket\", \"key\": \"images/photo.jpg\", \"makePublic\": false}}]}"
    )

    @field_validator("submission_id")
    def validate_submission_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Submission ID is required and cannot be empty")
        if not re.match(r"^[A-Z0-9]+$", v.strip()):
            raise ValueError(
                "Submission ID must contain only uppercase letters and numbers"
            )
        return v.strip()


class UpdateSubmissionStatusRequest(BaseSubmissionRequest):
    submission_id: str = Field(description="Submission Id")
    status_name: str = Field(description="New status name")
    comments: Optional[str] = Field(None, description="Optional comments")

    @field_validator("submission_id")
    def validate_submission_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Submission ID is required and cannot be empty")
        if not re.match(r"^[A-Z0-9]+$", v.strip()):
            raise ValueError(
                "Submission ID must contain only uppercase letters and numbers"
            )
        return v.strip()


class UpdateSubmissionOwnersRequest(BaseSubmissionRequest):
    submission_id: str = Field(description="Submission Id")
    email_ids: List[EmailStr] = Field(
        min_length=1,
        description="List of email addresses, cannot pass both email_ids and phone_numbers",
    )
    phone_numbers: Optional[List[str]] = Field(
        None,
        description="List of phone numbers, cannot pass both email_ids and phone_numbers",
    )

    @field_validator("submission_id")
    def validate_submission_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Submission ID is required and cannot be empty")
        if not re.match(r"^[A-Z0-9]+$", v.strip()):
            raise ValueError(
                "Submission ID must contain only uppercase letters and numbers"
            )
        return v.strip()


class GetSubmissionsInExcelRequest(BaseSubmissionRequest):
    filters: Optional[SubmissionFilters] = Field(None, description="Optional filters")
    requesting_user_email_address: EmailStr = Field(
        description="Email of requesting user"
    )
    field_names: Optional[List[str]] = Field(
        None,
        description="List of field names to include in export, both standard and custom fields",
    )
    format: Literal["Excel", "Csv"] = Field(
        default="Excel", description="Export format, Example: 'Excel' or 'Csv'"
    )


class GetSubmissionsCountRequest(BaseSubmissionRequest):
    filters: Optional[SubmissionQuery] = Field(None, description="Optional filters")
