from pydantic import Field, BaseModel
from ..base import BaseUpsertPageRequest
from ..base import JsonSerializableMixin


class PageMetadata(BaseModel, JsonSerializableMixin):
    show_submit_button: bool = Field(
        default=True, description="Show submit button of the page"
    )
    previous_button_text: str = Field(
        default="Previous", description="Previous button text of the page"
    )
    next_button_text: str = Field(
        default="Next", description="Next button text of the page"
    )


class AddPageBreakRequest(BaseUpsertPageRequest):
    page_index: int = Field(ge=0, description="Page index where to add page break")
    section_index: int = Field(
        ge=0, description="Section index where to add page break"
    )
    page_metadata: PageMetadata = Field(
        default=PageMetadata(), description="Page metadata"
    )


class UpdatePageBreakRequest(BaseUpsertPageRequest):
    page_index: int = Field(ge=0, description="Page index to update")
    page_metadata: PageMetadata = Field(
        default=PageMetadata(), description="Page metadata"
    )
