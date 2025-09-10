from typing import Optional, List, Literal
from pydantic import Field
from ..base import BaseUpsertSectionRequest
from .....enums import SectionType


class ReorderSectionRequest(BaseUpsertSectionRequest):
    source_section_index: int = Field(ge=0, description="Source section index")
    target_section_index: int = Field(ge=0, description="Target section index")
    source_page_index: int = Field(ge=0, description="Source page index")
    target_page_index: int = Field(ge=0, description="Target page index")


class UpsertSectionRequest(BaseUpsertSectionRequest):
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
        description="Array of unique field names, only when the copy is allowed",
    )
    retain_values: bool = Field(False, description="Retain values when hidden")
    keep_section_collapsed: bool = Field(False, description="Keep section collapsed")
    section_type: SectionType = Field(
        SectionType.SECTION, description="Type of the section"
    )
    initial_rows: int = Field(5, description="Initial number of rows")
