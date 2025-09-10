from pydantic import BaseModel, Field
from typing import Dict, Any


class Permission(BaseModel):
    can_submit_data: bool = Field(default=False, description="Can submit data")
    can_edit_data: bool = Field(default=False, description="Can edit data")
    can_view_data: bool = Field(default=False, description="Can view data")
    can_change_status: bool = Field(default=False, description="Can change status")
    can_edit_app: bool = Field(default=False, description="Can edit app")
    can_bulk_upload: bool = Field(default=False, description="Can bulk upload")
    can_view_analytics: bool = Field(default=False, description="Can view analytics")
    can_delete_data: bool = Field(default=False, description="Can delete data")

    @classmethod
    def from_json(cls, json_data: Dict[str, Any]) -> "Permission":
        return cls(**json_data)

    def to_dict(self) -> Dict[str, bool]:
        return {
            "canSubmitData": self.can_submit_data,
            "canEditData": self.can_edit_data,
            "canViewData": self.can_view_data,
            "canChangeStatus": self.can_change_status,
            "canEditApp": self.can_edit_app,
            "canBulkUpload": self.can_bulk_upload,
            "canViewAnalytics": self.can_view_analytics,
            "canDeleteData": self.can_delete_data,
        }
