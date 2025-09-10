from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base_response import BaseResponse
from ...enums import TriggerType


class WorkflowResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")


class WorkflowStepResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")
    trigger_type: TriggerType = Field(None, description="Trigger type")
    step_variable_name: Optional[str] = Field(
        None, description="Variable name of the affected step"
    )
    parent_step_variable_name: Optional[str] = Field(
        None, description="Parent step variable name"
    )
