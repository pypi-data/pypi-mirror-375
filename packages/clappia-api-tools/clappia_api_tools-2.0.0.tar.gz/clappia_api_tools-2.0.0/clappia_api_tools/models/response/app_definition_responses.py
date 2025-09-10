from typing import Optional
from pydantic import BaseModel, Field
from .base_response import BaseResponse


class AppDefinitionResponse(BaseResponse):
    app_id: str = Field(None, description="App ID")


class AppCreationResponse(BaseResponse):
    app_id: str = Field(None, description="Generated app ID")
    name: Optional[str] = Field(None, description="Name of created app")


class FieldOperationResponse(BaseResponse):
    app_id: str = Field(description="App ID where field was modified")
    field_name: Optional[str] = Field(None, description="Name of the field")


class PageBreakOperationResponse(BaseResponse):
    app_id: str = Field(description="App ID where page break was modified")
    page_index: Optional[int] = Field(None, description="Page index")


class ReorderSectionOperationResponse(BaseResponse):
    app_id: str = Field(description="App ID where section was modified")
    source_section_index: Optional[int] = Field(
        None, description="Source section index"
    )
    target_section_index: Optional[int] = Field(
        None, description="Target section index"
    )
    source_page_index: Optional[int] = Field(None, description="Source page index")
    target_page_index: Optional[int] = Field(None, description="Target page index")


class UpsertSectionOperationResponse(BaseResponse):
    app_id: str = Field(description="App ID where section was added")
    section_index: Optional[int] = Field(
        None, description="Index where section was added"
    )
    page_index: Optional[int] = Field(
        None, description="Page index where section was added"
    )
