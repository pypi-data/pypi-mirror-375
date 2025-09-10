from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from pydantic import EmailStr
from ..base import JsonSerializableMixin
from .....enums import SectionType


class ExternalSectionDetails(BaseModel, JsonSerializableMixin):
    name: str = Field(description="Name of the section")
    description: Optional[str] = Field(None, description="Description of the section")
    add_section_text: str = Field(
        "Add another Section", description="Text to display for add section button"
    )
    add_section_text_position: Literal["right", "left", "center"] = Field(
        "right",
        description="Position of the add section button, allowed values: right, left, center",
    )
    display_condition: Optional[str] = Field(
        None,
        description="Display condition for the section, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10",
    )
    allow_copy: bool = Field(False, description="Allow copying of the section")
    allow_edit_copy_after_submission: bool = Field(
        True, description="Allow editing and copying of the section after submission"
    )
    allow_edit_copy_after_submission_condition: Optional[str] = Field(
        None,
        description="Display condition for the allow edit copy after submission, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10",
    )
    max_number_of_copies: Optional[str] = Field(
        None,
        description="Maximum number of copies allowed, can be a number or '{numberOfCopies}'",
    )
    child_section_indices: List[int] = Field(
        default_factory=list, description="Array of child section indices"
    )
    unique_field_names: List[str] = Field(
        default_factory=list,
        description="Array of unique field names, only when the copy is allowed, Example: ['field1', 'field2']",
    )
    retain_values: bool = Field(False, description="Retain values when hidden")
    keep_section_collapsed: bool = Field(False, description="Keep section collapsed")
    section_type: SectionType = Field(
        SectionType.SECTION, description="Type of the section"
    )
    initial_rows: int = Field(5, description="Initial number of rows")


class ExternalSectionDefinition(BaseModel, JsonSerializableMixin):
    section_details: ExternalSectionDetails = Field(
        description="Section details of the section"
    )
    # field_definitions: List[Any] = Field([], description="Field definitions of the section") # TODO: Handle the fields adding in the future, current issue is that its client wont able to generated payload for fields


class ExternalPageMetadata(BaseModel, JsonSerializableMixin):
    show_submit_button: bool = Field(
        default=True, description="Show submit button of the page"
    )
    prev_button_text: str = Field(
        default="Previous", description="Previous button text of the page"
    )
    next_button_text: str = Field(
        default="Next", description="Next button text of the page"
    )


class ExternalPageDefinition(BaseModel, JsonSerializableMixin):
    page_details: ExternalPageMetadata = Field(description="Page details of the page")
    sections: List[ExternalSectionDefinition] = Field(
        [], description="Sections of the page"
    )


class CreateAppRequest(BaseModel, JsonSerializableMixin):
    name: str = Field(description="Name of the app")
    requesting_user_email_address: EmailStr = Field(
        default="support@clappia.com",
        description="Email of requesting user, to which you want to make the owner of the app",
    )
    description: Optional[str] = Field(None, description="Description of the app")
    pages: List[ExternalPageDefinition] = Field(description="Pages of the app")
