from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base_response import BaseResponse
from ...enums import ChartType


class ChartResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")
    chart_type: Optional[ChartType] = Field(None, description="Type of chart")
