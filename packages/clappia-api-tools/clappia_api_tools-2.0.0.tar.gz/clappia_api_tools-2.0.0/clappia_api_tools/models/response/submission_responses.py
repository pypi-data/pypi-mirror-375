from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .base_response import BaseResponse


class SubmissionResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")
    submission_id: Optional[str] = Field(None, description="Submission ID")


class SubmissionsResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadata")


class SubmissionsAggregationResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")


class SubmissionsExcelResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")
    url: Optional[str] = Field(None, description="Download URL for the exported file")
    format: Optional[str] = Field(None, description="Export format used")
    requesting_user_email_address: Optional[str] = Field(
        None, description="Email address where file was sent"
    )


class SubmissionsCountResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")
    total_count: int = Field(None, description="Total number of submissions")
    filtered_count: int = Field(
        None, description="Number of submissions after applying filters"
    )
