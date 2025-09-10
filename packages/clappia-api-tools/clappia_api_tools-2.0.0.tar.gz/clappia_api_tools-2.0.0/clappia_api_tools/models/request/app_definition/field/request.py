from typing import Optional, List, Literal, Dict, Any, ClassVar
from pydantic import EmailStr, Field, field_validator, model_validator
import re
import json
from ..base import BaseUpsertFieldRequest, ValidatedString, UniqueListValidator
from ..model import SortField, FilterField, RestApiOutputField
from .....enums import (
    DatabaseType,
    WatermarkPosition,
    ValidationType,
    ImageQuality,
    AllowedFileTypes,
    ChipType,
)


class UpsertFieldTextRequest(BaseUpsertFieldRequest):
    validation: Optional[ValidationType] = Field(None, description="Validation type")
    custom_validation_condition: Optional[str] = Field(
        None,
        description="Custom validation condition, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10",
    )
    custom_validation_error_message: Optional[str] = Field(
        None, description="Custom validation error message"
    )

    @model_validator(mode="after")
    def validate_custom_validation_requirements(self):
        if self.validation == "custom" and (
            not self.custom_validation_condition
            or not self.custom_validation_condition.strip()
        ):
            raise ValueError(
                "Custom validation condition is required when validation type is 'custom'"
            )
        return self


class UpsertFieldTextAreaRequest(BaseUpsertFieldRequest):
    pass


class UpsertFieldDependencyAppRequest(BaseUpsertFieldRequest):
    dependency_app_id: str = Field(
        min_length=1,
        description="ID of the dependency app, the app from which the data will be fetched, mandatory",
    )
    skip_permission_check: Optional[bool] = Field(
        False,
        description="Whether to allow users to see all data of the dependency app",
    )
    key_field_names: List[str] = Field(
        min_length=1,
        description="Array of key field names for dependency app, Example: ['field_name'], These are the fields that you need to show to the end users so that they can identify the item to be selected",
    )
    other_field_names: Optional[List[str]] = Field(
        None,
        description="Array of other field names for dependency app, Example: ['field_name'], you can select the items that will be pulled against the main selection made by the user. For example, if the user selects a Customer from the dropdown, all the details selected below will be fetched against that customer.",
    )
    sort_fields: Optional[List[SortField]] = Field(
        None,
        max_length=3,
        description="Array of sort field configurations, Example: [{'sort_by': 'field_name', 'sort_direction': 'asc'}]",
    )
    no_submission_message: Optional[str] = Field(
        "No submissions found.", description="Message when no submissions found"
    )
    filters: Optional[List[FilterField]] = Field(None, description="Search filters")
    min_chars_to_query: Optional[int] = Field(
        0, ge=0, le=15, description="Minimum characters to trigger query"
    )
    max_search_options: Optional[int] = Field(
        10, ge=1, le=50, description="Maximum search options to display"
    )
    show_create_submission_option: Optional[bool] = Field(
        True,
        description="Whether to show create submission option, if no submission exists for the selected item, the user can create a new submission for that item",
    )
    enable_broad_search: Optional[bool] = Field(
        False,
        description="Whether to enable broad search, if enabled, the user can search for the item by typing the item name",
    )

    @field_validator("key_field_names")
    @classmethod
    def validate_unique_key_fields(cls, v: List[str]) -> List[str]:
        return UniqueListValidator.validate_unique_strings(v, "Key field names")

    @field_validator("other_field_names")
    @classmethod
    def validate_unique_other_fields(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        return UniqueListValidator.validate_unique_strings(v, "Other field names")

    @field_validator("sort_fields")
    @classmethod
    def validate_unique_sort_fields(
        cls, v: Optional[List[SortField]]
    ) -> Optional[List[SortField]]:
        if v is not None:
            sort_by_fields = [field.sort_by for field in v]
            if len(set(sort_by_fields)) != len(sort_by_fields):
                raise ValueError("Sort fields must have unique sortBy values")
        return v


class UpsertFieldRestApiRequest(BaseUpsertFieldRequest):
    server_url: str = Field(
        min_length=1,
        description="URL of the REST API endpoint, mandatory. Example: 'https://api.example.com/data' or 'https://api.example.com/data/{id} or {server_url}'",
    )
    method_type: Literal["GET", "POST", "PATCH", "DELETE"] = Field(
        description="HTTP method type"
    )
    body_type: Optional[Literal["JSON", "XML", "FORM-DATA"]] = Field(
        None, description="Type of request body"
    )
    headers: Optional[str] = Field(
        "{}",
        description="HTTP headers as JSON string, Example: {'Content-Type': 'application/json'}",
    )
    body: Optional[str] = Field(
        "{}",
        description="Request body as JSON string, Example: {'{field_name}': 'value'} or {'{field_name}': '{field_name}'}",
    )
    query_string: Optional[str] = Field(
        None,
        description="URL query parameters, Example: '?field_name=value' or '?field_name={field_name}'",
    )
    response_mapping: List[RestApiOutputField] = Field(
        min_length=1, description="Array of output field mappings for API response"
    )

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        return ValidatedString.url_validator(v)

    @field_validator("headers", "body")
    @classmethod
    def validate_json_strings(cls, v: Optional[str]) -> Optional[str]:
        return ValidatedString.json_string_validator(v)

    @field_validator("response_mapping")
    @classmethod
    def validate_unique_response_mapping_names(
        cls, v: List[RestApiOutputField]
    ) -> List[RestApiOutputField]:
        names = [field.name for field in v]
        if len(set(names)) != len(names):
            raise ValueError("Response mapping field names must be unique")
        return v

    @field_validator("query_string")
    @classmethod
    def validate_query_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^[\s\w%&.=[\]{}\-]*$", v):
            raise ValueError("Invalid query string format")
        return v

    @model_validator(mode="after")
    def validate_body_requirements(self):
        if self.method_type in ["POST", "PATCH"]:
            if not self.body_type:
                raise ValueError("Body type is required for POST and PATCH requests")
            if not self.body or self.body.strip() in ["{}", ""]:
                raise ValueError("Body is required for POST and PATCH requests")

            if self.body_type == "JSON":
                try:
                    json.loads(self.body)
                except json.JSONDecodeError:
                    raise ValueError("Body must be valid JSON when bodyType is JSON")
            elif self.body_type == "FORM-DATA":
                try:
                    form_data = json.loads(self.body)
                    if not isinstance(form_data, dict) or len(form_data) == 0:
                        raise ValueError("Form data must be a non-empty JSON object")
                except json.JSONDecodeError:
                    raise ValueError("Form data must be valid JSON")
        return self


class UpsertFieldAddressRequest(BaseUpsertFieldRequest):
    countries_list: Optional[List[str]] = Field(
        None,
        max_length=5,
        description="List of country codes to restrict address selection",
    )

    @field_validator("countries_list")
    @classmethod
    def validate_countries_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError("Countries list must contain unique country codes")
            for country_code in v:
                if not country_code or not country_code.strip():
                    raise ValueError("Country codes cannot be empty")
                if not re.match(r"^[A-Z]{2}$", country_code.strip()):
                    raise ValueError("Country codes must be 2-letter uppercase codes")
        return v


class UpsertFieldDatabaseRequest(BaseUpsertFieldRequest):
    database_type: DatabaseType = Field(description="Type of database to connect to")
    database_port: str = Field(min_length=1, description="Database port number")
    database_host: str = Field(min_length=1, description="Database host address")
    database_username: str = Field(
        min_length=1, description="Database username for authentication"
    )
    database_password: str = Field(
        min_length=1, description="Database password for authentication"
    )
    database_name: str = Field(min_length=1, description="Name of the database")
    database_query: str = Field(
        min_length=1,
        description="SQL query to execute, Example: 'SELECT * FROM users' where id = {number_inp}",
    )
    database_output_fields: List[str] = Field(
        default_factory=list,
        description="Array of output field names from the database query",
    )
    no_records_message: str = Field(
        "No records found", description="Message to display when no records are found"
    )

    @field_validator("database_port")
    @classmethod
    def validate_database_port(cls, v: str) -> str:
        if not v.isdigit() or not (1 <= int(v) <= 65535):
            raise ValueError(
                "Database port must be a valid port number between 1 and 65535"
            )
        return v

    @field_validator("database_host")
    @classmethod
    def validate_database_host(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9.-]+$", v):
            raise ValueError("Database host must be a valid hostname or IP Upsertress")
        return v

    @field_validator("database_output_fields")
    @classmethod
    def validate_unique_output_fields(cls, v: List[str]) -> List[str]:
        return UniqueListValidator.validate_unique_strings(v, "Database output fields")


class UpsertFieldDateRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        True, description="Whether to allow users to manually type dates"
    )
    default_to_current_date: bool = Field(
        False, description="Whether to default the field to the current date"
    )
    current_date_button_visible: bool = Field(
        True, description="Whether to show a button to set current date"
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date for date range restriction (YYYY-MM-DD format) or {start_date}, Example: '2021-01-01' or {start_date}",
    )
    end_date: Optional[str] = Field(
        None,
        description="End date for date range restriction (YYYY-MM-DD format) or {end_date}, Example: '2021-01-01' or {end_date}",
    )


class UpsertFieldAIRequest(BaseUpsertFieldRequest):
    instructions: Optional[str] = Field(
        None,
        description="Instructions for the AI model, Example: 'Analyze the sentiment of {customerFeedback} and provide a summary'",
    )
    model: Optional[str] = Field(None, description="Specific AI model to use")
    llm: Optional[Literal["OpenAI", "Claude", "Gemini"]] = Field(
        None, description="Large Language Model provider"
    )

    @model_validator(mode="after")
    def validate_ai_configuration(self):
        if self.llm and self.model:
            model_options_map = {
                "OpenAI": [
                    "gpt-4",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo-preview",
                    "o1-mini",
                    "o1-preview",
                    "gpt-3.5-turbo",
                ],
                "Claude": [
                    "claude-2",
                    "claude-2.1",
                    "claude-3-haiku-20240307",
                    "claude-3-sonnet-20240229",
                    "claude-3-opus-latest",
                    "claude-3-5-sonnet-latest",
                    "claude-3-5-haiku-latest",
                    "claude-3-7-sonnet-latest",
                ],
                "Gemini": [
                    "gemini-2.0-flash",
                    "gemini-2.0-flash-lite",
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-8b",
                    "gemini-1.5-pro",
                ],
            }

            if self.llm in model_options_map:
                if self.model not in model_options_map[self.llm]:
                    raise ValueError(
                        f"Model '{self.model}' is not supported for LLM provider '{self.llm}'"
                    )

        if not self.instructions and not self.llm:
            raise ValueError(
                "Either instructions or LLM provider must be specified for AI field"
            )

        return self


class UpsertFieldCodeRequest(BaseUpsertFieldRequest):
    code: str = Field(
        default="""function main() {
    // Your code here
    output = {};
    var num1 = Math.round(Math.random()*10);
    var num2 = Math.round(Math.random()*10);
    output['sum'] = num1 + num2;
    output['prod'] = num1 * num2;
    return output;
}""",
        description="JavaScript code to execute",
    )
    output_fields: List[str] = Field(
        default=["sum", "prod"],
        description="Array of output field names that the code will generate",
    )

    @field_validator("output_fields")
    @classmethod
    def validate_unique_output_fields(cls, v: List[str]) -> List[str]:
        return UniqueListValidator.validate_unique_strings(v, "Code output fields")


class UpsertFieldGpsLocationRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        False, description="Whether to allow manual location input"
    )
    default_to_current_location: bool = Field(
        True, description="Whether to default to current GPS location"
    )
    target_locations: List[str] = Field(
        default_factory=list,
        description="Array of target location coordinates for geofencing, Example: ['22.66, 77.5946', {target_location}]",
    )
    radius: float = Field(
        1.0, description="Geofencing radius in kilometers (also called boundary)"
    )
    show_map_view: bool = Field(
        True, description="Whether to show map view for location selection"
    )
    enable_geo_fencing: Optional[bool] = Field(
        None, description="Whether to enable geofencing functionality"
    )
    enable_reverse_geocoding: Optional[bool] = Field(
        None, description="Whether to enable reverse geocoding functionality"
    )

    @field_validator("radius")
    @classmethod
    def validate_radius(cls, v: float) -> float:
        if not (1 <= v <= 20000000):
            raise ValueError("Radius must be between 1 and 20,000,000")
        return v

    @model_validator(mode="after")
    def validate_geo_fencing_requirements(self):
        if self.enable_geo_fencing:
            if not self.target_locations:
                raise ValueError(
                    "Target locations are required when geofencing is enabled"
                )
        return self


class UpsertFieldLiveTrackingRequest(BaseUpsertFieldRequest):
    auto_complete_duration_in_hours: int = Field(
        8, description="Duration in hours after which location tracking auto-completes"
    )

    @field_validator("auto_complete_duration_in_hours")
    @classmethod
    def validate_duration(cls, v: int) -> int:
        if not (1 <= v <= 12):
            raise ValueError("Auto complete duration must be between 1 and 12 hours")
        return v


class UpsertFieldManualAddressRequest(BaseUpsertFieldRequest):
    countries_list: Optional[List[str]] = Field(
        None,
        max_length=5,
        description="Array of country codes to restrict address input",
    )
    default_country: Optional[str] = Field(
        None, description="Default country code for address input"
    )

    @field_validator("countries_list")
    @classmethod
    def validate_countries_list(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            if len(set(v)) != len(v):
                raise ValueError("Countries list must contain unique country codes")
            for country_code in v:
                if not country_code or not country_code.strip():
                    raise ValueError("Country codes cannot be empty")
                if not re.match(r"^[A-Z]{2}$", country_code.strip()):
                    raise ValueError("Country codes must be 2-letter uppercase codes")
        return v

    @field_validator("default_country")
    @classmethod
    def validate_default_country(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Default country code cannot be empty")
            if not re.match(r"^[A-Z]{2}$", v.strip()):
                raise ValueError(
                    "Default country code must be a 2-letter uppercase code"
                )
        return v


class UpsertFieldPhoneNumberRequest(BaseUpsertFieldRequest):
    default_country_code: Optional[str] = Field(
        None, description="Default country code (ISO format)"
    )
    is_country_code_editable: Optional[bool] = Field(
        None, description="Whether the country code can be edited"
    )
    allow_manual_input: Optional[bool] = Field(
        None, description="Whether to allow manual phone number input"
    )

    @field_validator("default_country_code")
    @classmethod
    def validate_country_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("Country code cannot be empty")
            if not re.match(r"^[A-Z]{2}$", v.strip()):
                raise ValueError("Country code must be a 2-letter uppercase code")
        return v


class UpsertFieldProgressBarRequest(BaseUpsertFieldRequest):
    progress_formula: Optional[str] = Field(
        None,
        description="Formula to calculate progress percentage, Example: {progress_field_name} / {total_field_name} * 100",
    )
    progress_text: Optional[str] = Field(
        None, description="Text to display with progress, Example: 'Progress'"
    )


class UpsertFieldSignatureRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        True, description="Whether to allow manual signature input"
    )
    file_display_name: str = Field(
        "",
        description="Display name for the signature file, Example: 'Signature' or {field_name}",
    )


class UpsertFieldRangeRequest(BaseUpsertFieldRequest):
    minimum_value: float = Field(1.0, description="Minimum value for the range slider")
    maximum_value: float = Field(5.0, description="Maximum value for the range slider")
    step_size: float = Field(1.0, description="Step size for the range slider")
    default_counter_slider: float = Field(
        1.0, description="Default value for the range slider"
    )
    allow_manual_input: bool = Field(False, description="Allow manual input of values")

    @field_validator("minimum_value")
    @classmethod
    def validate_minimum_value(cls, v: float) -> float:
        if v < 0 or v > 9007199254740991:  # Number.MAX_SAFE_INTEGER
            raise ValueError(
                "Minimum value must be greater than 0 and less than 9007199254740991"
            )
        return v

    @field_validator("maximum_value")
    @classmethod
    def validate_maximum_value(cls, v: float) -> float:
        if v < 0 or v > 9007199254740991:  # Number.MAX_SAFE_INTEGER
            raise ValueError(
                "Maximum value must be greater than 0 and less than 9007199254740991"
            )
        return v

    @field_validator("step_size")
    @classmethod
    def validate_step_size(cls, v: float) -> float:
        if v <= 0 or v > 9007199254740991:  # Number.MAX_SAFE_INTEGER
            raise ValueError(
                "Step size must be greater than 0 and less than 9007199254740991"
            )
        return v

    @model_validator(mode="after")
    def validate_range_consistency(self):
        if self.minimum_value >= self.maximum_value:
            raise ValueError("Minimum value must be less than maximum value")

        if (
            self.default_counter_slider < self.minimum_value
            or self.default_counter_slider > self.maximum_value
        ):
            raise ValueError("Default value must be between minimum and maximum values")

        if self.step_size > (self.maximum_value - self.minimum_value):
            raise ValueError(
                "Step size cannot exceed the range between minimum and maximum values"
            )

        return self


class UpsertFieldCounterRequest(UpsertFieldRangeRequest):
    pass


class UpsertFieldSliderRequest(UpsertFieldRangeRequest):
    pass


class UpsertFieldTimeRequest(BaseUpsertFieldRequest):
    allow_manual_input: bool = Field(
        True, description="Whether to allow manual time input"
    )
    default_to_current_time: bool = Field(
        False, description="Whether to default to current time"
    )
    start_time: Optional[str] = Field(
        None,
        description="Minimum allowed time (HH:mm format) or {start_time} Example: '09:00' or {start_time}",
    )
    end_time: Optional[str] = Field(
        None,
        description="Maximum allowed time (HH:mm format) or {end_time} Example: '18:00' or {end_time}",
    )


class UpsertFieldToggleRequest(BaseUpsertFieldRequest):
    default_toggle_value: bool = Field(False, description="Default state of the toggle")
    true_value: Optional[str] = Field(
        None, description="Value to store when toggle is ON"
    )
    false_value: Optional[str] = Field(
        None, description="Value to store when toggle is OFF"
    )


class UpsertFieldValidationRequest(BaseUpsertFieldRequest):
    validation_type: Literal["duplicate", "custom"] = Field(
        "duplicate", description="Type of validation to perform"
    )
    validation_message: str = Field(
        "Validation message", description="Message to display for validation result"
    )
    unique_field_names: Optional[List[str]] = Field(
        None, description="Array of field names to check for duplicates"
    )
    validation_condition: Optional[str] = Field(
        None,
        description="Custom validation condition, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10",
    )
    validation_level: Literal["success", "warning", "error"] = Field(
        "success", description="Level of validation result"
    )

    @field_validator("unique_field_names")
    @classmethod
    def validate_unique_field_names(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            return UniqueListValidator.validate_unique_strings(v, "Unique field names")
        return v

    @model_validator(mode="after")
    def validate_validation_configuration(self):
        if self.validation_type == "duplicate":
            if not self.unique_field_names or len(self.unique_field_names) == 0:
                raise ValueError(
                    "Unique field names are required for duplicate validation type"
                )
            if self.validation_condition:
                raise ValueError(
                    "Validation condition cannot be used with duplicate validation type"
                )
        elif self.validation_type == "custom":
            if not self.validation_condition or not self.validation_condition.strip():
                raise ValueError(
                    "Validation condition is required for custom validation type"
                )
            if self.unique_field_names:
                raise ValueError(
                    "Unique field names cannot be used with custom validation type"
                )

        return self


class UpsertFieldReadOnlyFileRequest(BaseUpsertFieldRequest):
    static_attachment: Dict[str, str] = Field(
        description="Static attachment object with base64, contentType and fileName"
    )

    @field_validator("static_attachment")
    @classmethod
    def validate_static_attachment(cls, v: Dict[str, str]) -> Dict[str, str]:
        required_keys = ["base64", "contentType", "fileName"]
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Static attachment must contain '{key}'")
            if not v[key] or not str(v[key]).strip():
                raise ValueError(f"Static attachment '{key}' cannot be empty")
        return v


class UpsertFieldVideoViewerRequest(UpsertFieldReadOnlyFileRequest):
    pass


class UpsertFieldImageViewerRequest(UpsertFieldReadOnlyFileRequest):
    pass


class UpsertFieldPdfViewerRequest(UpsertFieldReadOnlyFileRequest):
    pass


class UpsertFieldVoiceRequest(BaseUpsertFieldRequest):
    max_length: int = Field(
        60, description="Maximum length of voice recording in seconds (1-300)"
    )
    file_upload_limit: int = Field(
        10, description="Maximum number of voice files that can be uploaded (1-10)"
    )
    file_display_name: str = Field(
        "",
        description="Display name for the voice file, Example: 'Voice' or {field_name}",
    )

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, v: int) -> int:
        if not (1 <= v <= 300):
            raise ValueError("Max length must be between 1 and 300 seconds")
        return v

    @field_validator("file_upload_limit")
    @classmethod
    def validate_file_upload_limit(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("File upload limit must be between 1 and 10")
        return v


class UpsertFieldFormulaRequest(BaseUpsertFieldRequest):
    formula: str = Field(
        "",
        description="Formula expression with field references. Clappia supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: '=SUM({field_name1,field_name2}) + IF({field_name3}>10, 'Yes', 'No')'",
    )

    @field_validator("formula")
    @classmethod
    def validate_formula(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Formula cannot be empty")
        return v


class UpsertFieldRichTextEditorRequest(BaseUpsertFieldRequest):
    pass


class UpsertFieldCodeReaderRequest(BaseUpsertFieldRequest):
    field_type: Literal["codeScanner"] = Field(default="codeScanner")
    allow_manual_input: bool = Field(
        False, description="Whether to allow manual input of codes"
    )
    key_field_name: Optional[str] = Field(
        None,
        description="Name of the key field for dependency app integration, Example: 'field_name', mandatory if the dependency app ID is provided",
    )
    other_field_names: Optional[List[str]] = Field(
        None,
        description="Array of other field names for dependency app integration, Example: ['field_name']",
    )
    skip_permission_check: bool = Field(
        True, description="Whether to allow users to see all data of the dependency app"
    )
    open_camera_automatically: bool = Field(
        False,
        description="Whether to open camera automatically when app home screen is opened",
    )
    dependency_app_id: Optional[str] = Field(
        None, description="ID of the dependency app for code scanning integration"
    )

    @field_validator("other_field_names")
    @classmethod
    def validate_unique_other_fields(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        return UniqueListValidator.validate_unique_strings(v, "Other field names")

    @field_validator("other_field_names")
    @classmethod
    def validate_other_field_names_not_empty(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        if v and len(v) == 0:
            raise ValueError(
                "Other field names should be an array of at least one field name"
            )
        return v

    @model_validator(mode="after")
    def validate_dependency_app_requirements(self):
        if self.dependency_app_id:
            if not self.key_field_name:
                raise ValueError(
                    "Key field name is required when dependency app ID is provided"
                )
        return self


class UpsertFieldNfcReaderRequest(UpsertFieldCodeReaderRequest):
    pass


class UpsertFieldNumberInputRequest(BaseUpsertFieldRequest):
    min_value: Optional[float] = Field(None, description="Minimum allowed value")
    max_value: Optional[float] = Field(None, description="Maximum allowed value")
    default_input_value: Optional[float] = Field(
        None, description="Default value for the number input"
    )

    @model_validator(mode="after")
    def validate_number_range(self):
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("Minimum value cannot be greater than maximum value")

        if self.default_input_value is not None:
            if self.min_value is not None and self.default_input_value < self.min_value:
                raise ValueError("Default value cannot be less than the minimum value")
            if self.max_value is not None and self.default_input_value > self.max_value:
                raise ValueError(
                    "Default value cannot be greater than the maximum value"
                )

        return self


class UpsertFieldReadOnlyTextRequest(BaseUpsertFieldRequest):
    rich_text: Optional[str] = Field(None, description="Rich text content for display, can include field references. Example: 'Hello {field_name}'")


class UpsertFieldTagsRequest(BaseUpsertFieldRequest):
    tag_names: List[str] = Field(default_factory=list, description="Array of tag names")

    @field_validator("tag_names")
    @classmethod
    def validate_tag_names(cls, v: List[str]) -> List[str]:
        if v:
            for tag in v:
                if not tag or not str(tag).strip():
                    raise ValueError("Tag names cannot be empty")
        return UniqueListValidator.validate_unique_strings(v, "Tag names")


class UpsertFieldDropdownRequest(BaseUpsertFieldRequest):
    options: List[str] = Field(
        default_factory=list,
        description=(
            "List of dropdown options. For dependent dropdowns, use '||' to separate hierarchy levels.\n\n"
            "Examples:\n"
            "• Simple dropdown: ['Red', 'Blue', 'Green']\n"
            "• Dependent dropdown: ['Shirt||Formal', 'Shirt||Casual', 'T-Shirt||Round Neck']\n"
            "• Three-level: ['Shirt||Formal||S', 'Shirt||Formal||M', 'T-Shirt||V-Neck||L']"
        ),
    )

    dependency_field_names: Optional[List[str]] = Field(
        None,
        description=(
            "Names of parent dropdown fields that control which options are shown in this dropdown.\n"
            "Must be listed in dependency order (root parent first).\n\n"
            "How filtering works:\n"
            "• User selects 'Shirt' in Category field\n"
            "• Only options starting with 'Shirt||' are shown in dependent Type field\n"
            "• User selects 'Formal' in Type field\n"
            "• Only options starting with 'Shirt||Formal||' are shown in dependent Size field\n\n"
            "Examples:\n"
            "• Two-level: ['category_field'] - depends on one parent\n"
            "• Three-level: ['category_field', 'type_field'] - depends on two parents in order"
        ),
    )
    selecting_multiple_options_allowed: bool = Field(
        False, description="Whether multiple selections are allowed"
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Options are required and should be an array of strings")
        if not all(isinstance(option, str) and option.strip() for option in v):
            raise ValueError("All options must be non-empty strings")
        return v

    @field_validator("dependency_field_names")
    @classmethod
    def validate_dependency_fields(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            if not all(isinstance(field, str) and field.strip() for field in v):
                raise ValueError("All dependency field names must be non-empty strings")
        return v


class UpsertFieldRadioRequest(BaseUpsertFieldRequest):
    options: List[str] = Field(
        default_factory=lambda: ["value one", "value two"],
        description=(
            "List of radio button options. For dependent radio buttons, use '||' to separate hierarchy levels.\n\n"
            "Examples:\n"
            "• Simple radio: ['Yes', 'No', 'Maybe']\n"
            "• Dependent radio: ['Shirt||Small', 'Shirt||Medium', 'T-Shirt||Large']\n"
            "• Three-level: ['Clothing||Shirt||Cotton', 'Clothing||Pants||Denim']"
        ),
    )

    number_of_cols: Optional[int] = Field(
        None,
        description=(
            "Number of columns to display radio buttons in (1-3).\n"
            "Controls the grid layout of radio button options.\n\n"
            "Examples:\n"
            "• 1 = Vertical single column\n"
            "• 2 = Two-column grid\n"
            "• 3 = Three-column grid"
        ),
    )

    style: ChipType = Field(
        ChipType.CHIPS,
        description="Visual style for radio buttons (CHIPS for modern chip-style, or other ChipType values)",
    )

    dependency_field_names: Optional[List[str]] = Field(
        None,
        description=(
            "Names of parent fields that control which radio options are shown.\n"
            "Must be listed in dependency order (root parent first).\n\n"
            "How filtering works:\n"
            "• User selects 'Clothing' in Category field\n"
            "• Only radio options starting with 'Clothing||' become available\n"
            "• User selects 'Shirt' in Type field\n"
            "• Only options starting with 'Clothing||Shirt||' are shown\n\n"
            "Examples:\n"
            "• Single dependency: ['category_field']\n"
            "• Multi-level: ['category_field', 'subcategory_field']"
        ),
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Options are required and should be an array of strings")
        if not all(isinstance(option, str) and option.strip() for option in v):
            raise ValueError("All options must be non-empty strings")
        return v

    @field_validator("number_of_cols")
    @classmethod
    def validate_number_of_cols(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 3):
            raise ValueError("Number of columns must be between 1 and 3")
        return v

    @field_validator("dependency_field_names")
    @classmethod
    def validate_dependency_fields(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v:
            if not all(isinstance(field, str) and field.strip() for field in v):
                raise ValueError("All dependency field names must be non-empty strings")
        return v


class UpsertFieldUrlInputRequest(BaseUpsertFieldRequest):
    default_value: Optional[str] = Field(
        None, description="Default URL value. Must be a valid URL format"
    )


class UpsertFieldCheckboxRequest(BaseUpsertFieldRequest):
    options: List[str] = Field(
        default_factory=lambda: ["value one", "value two"],
        description="Array of checkbox options, Example: ['value one', 'value two']",
    )
    number_of_cols: Optional[int] = Field(
        None, description="Number of columns for checkbox layout (1-3), Example: 1 or 2 or 3"
    )
    style: Literal["Standard", "Chips"] = Field(
        "Chips", description="Display style for checkboxes, Example: 'Standard' or 'Chips'"
    )
    show_not_applicable_option: bool = Field(
        True, description="Whether to show 'Not Applicable' option"
    )
    name_of_not_applicable_option: str = Field(
        "Not Applicable", description="Text for 'Not Applicable' option"
    )

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Options are required and should be an array of strings")
        if not all(isinstance(option, str) and option.strip() for option in v):
            raise ValueError("All options must be non-empty strings")
        return v

    @field_validator("number_of_cols")
    @classmethod
    def validate_number_of_cols(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 1 or v > 3):
            raise ValueError("Number of columns must be between 1 and 3")
        return v


class UpsertFieldPaymentGatewayRequest(BaseUpsertFieldRequest):
    payment_gateway: Literal["Razorpay", "Stripe", "Paypal", "Eazypay"] = Field(
        description="Payment gateway provider"
    )
    currency: str = Field(
        description="Currency code, Example: 'INR' or 'USD' or {currency}"
    )
    amount: str = Field(
        description="Payment amount. Can include field references, Example: '100' or {amount}"
    )

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Currency is required and must be a string")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Amount is required and must be a string")
        return v


class UpsertFieldRazorpayPaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    key_id: str = Field(description="Razorpay API key ID")
    key_secret: str = Field(description="Razorpay API key secret")
    company_name: Optional[str] = Field(
        None, description="Company name for payment display"
    )
    image_link: Optional[str] = Field(
        None, description="Company logo image link for payment display"
    )
    metadata: Optional[List[Dict[str, str]]] = Field(
        None, description="Array of key-value pairs for Upsertitional metadata"
    )

    @field_validator("key_id")
    @classmethod
    def validate_key_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Razorpay Key ID is required and must be a string")
        return v

    @field_validator("key_secret")
    @classmethod
    def validate_key_secret(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Razorpay Key Secret is required and must be a string")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(
        cls, v: Optional[List[Dict[str, str]]]
    ) -> Optional[List[Dict[str, str]]]:
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Metadata must be an array")
            keys = [item.get("key") for item in v if item.get("key")]
            if len(keys) != len(set(keys)):
                raise ValueError("Metadata must have unique keys")
            for item in v:
                if not item.get("key") or not item.get("value"):
                    raise ValueError(
                        "All metadata entries must have non-empty key and value"
                    )
        return v


class UpsertFieldEazypayPaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    merchant_id: str = Field(description="Eazypay merchant ID")
    submerchant_id: str = Field(description="Eazypay submerchant ID")
    reference_no: str = Field(
        description="Reference number for payment. Can include field references"
    )
    optional_fields: List[str] = Field(
        description="Array of optional field names, Example: ['{field_name1}', '{field_name2}']"
    )
    mandatory_fields: List[str] = Field(
        description="Array of mandatory field names, Example: ['{field_name1}', '{field_name2}']"
    )
    encryption_key: str = Field(description="Encryption key for secure payments")

    @field_validator("merchant_id")
    @classmethod
    def validate_merchant_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Eazypay Merchant ID is required and must be a string")
        return v

    @field_validator("submerchant_id")
    @classmethod
    def validate_submerchant_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Eazypay Submerchant ID is required and must be a string")
        return v

    @field_validator("reference_no")
    @classmethod
    def validate_reference_no(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "Eazypay Reference Number is required and must be a string"
            )
        return v

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Eazypay Encryption Key is required and must be a string")
        return v

    @field_validator("optional_fields")
    @classmethod
    def validate_optional_fields(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one optional field is required")
        if not all(isinstance(field, str) and field.strip() for field in v):
            raise ValueError("All optional fields must be strings")
        return v

    @field_validator("mandatory_fields")
    @classmethod
    def validate_mandatory_fields(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one mandatory field is required")
        if not all(isinstance(field, str) and field.strip() for field in v):
            raise ValueError("All mandatory fields must be strings")
        return v


class UpsertFieldPaypalPaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    paypal_client_id: str = Field(description="PayPal client ID for API authentication")
    paypal_client_secret: str = Field(
        description="PayPal client secret for API authentication"
    )

    @field_validator("paypal_client_id")
    @classmethod
    def validate_paypal_client_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("PayPal Client ID is required and must be a string")
        return v

    @field_validator("paypal_client_secret")
    @classmethod
    def validate_paypal_client_secret(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("PayPal Client Secret is required and must be a string")
        return v


class UpsertFieldStripePaymentGatewayRequest(UpsertFieldPaymentGatewayRequest):
    publishable_key: str = Field(
        description="Stripe publishable key for client-side integration"
    )
    secret_key: str = Field(description="Stripe secret key for server-side integration")
    metadata: Optional[List[Dict[str, str]]] = Field(
        None, description="Array of key-value pairs for Upsertitional metadata"
    )

    @field_validator("publishable_key")
    @classmethod
    def validate_publishable_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Stripe Publishable Key is required and must be a string")
        return v

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Stripe Secret Key is required and must be a string")
        return v

    @field_validator("metadata")
    @classmethod
    def validate_metadata(
        cls, v: Optional[List[Dict[str, str]]]
    ) -> Optional[List[Dict[str, str]]]:
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("Metadata must be an array")
            keys = [item.get("key") for item in v if item.get("key")]
            if len(keys) != len(set(keys)):
                raise ValueError("Metadata must have unique keys")
            for item in v:
                if not item.get("key") or not item.get("value"):
                    raise ValueError(
                        "All metadata entries must have non-empty key and value"
                    )
        return v


class UpsertFieldButtonRequest(BaseUpsertFieldRequest):
    button_position: Literal["left", "center", "right"] = Field(
        "left", description="Position of the button"
    )
    open_link: Literal["sameTab", "newTab", "modalTab"] = Field(
        description="How to open links"
    )
    placement: Optional[str] = Field(None, description="Button placement on the form")
    action_details: Dict[str, Any] = Field(
        description="Action details for button click behavior"
    )

    @field_validator("action_details")
    @classmethod
    def validate_action_details(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v:
            raise ValueError("Action details are required")

        action_type = v.get("actionType")
        if not action_type or action_type not in [
            "openClappiaApp",
            "openLink",
            "timer",
            "code",
        ]:
            raise ValueError(
                "Action type is required and must be one of: openClappiaApp, openLink, timer, code"
            )

        if action_type == "openClappiaApp":
            if not v.get("appId"):
                raise ValueError("App ID is required for OpenClappiaApp action")
            if not v.get("viewType") or v.get("viewType") not in [
                "home",
                "submissions",
                "analytics",
            ]:
                raise ValueError(
                    "View type is required and must be one of: home, submissions, analytics"
                )
            if v.get("viewType") == "home":
                if not v.get("navigationType") or v.get("navigationType") not in [
                    "section",
                    "page",
                    "field",
                ]:
                    raise ValueError(
                        "Navigation type is required for Home view and must be one of: section, page, field"
                    )
                if not v.get("idToNavigate"):
                    raise ValueError("ID to navigate is required for Home view")

        elif action_type == "openLink":
            if not v.get("redirectLink"):
                raise ValueError("Redirect link is required for OpenLink action")

        elif action_type == "timer":
            if not v.get("waitForSeconds"):
                raise ValueError("Wait for seconds is required for Timer action")

        elif action_type == "code":
            if not v.get("code"):
                raise ValueError("Code is required for Code action")

        return v


class UpsertFieldUniqueSequentialRequest(BaseUpsertFieldRequest):
    prefix: Optional[str] = Field(
        None,
        description="Prefix for the sequential number. Can include field references, Example: 'INV' or {prefix}",
    )
    minimum_length: int = Field(
        1, description="Minimum length of the sequential number part"
    )
    starting_sequence_number: int = Field(
        1, description="Starting number for the sequence"
    )

    @field_validator("minimum_length")
    @classmethod
    def validate_minimum_length(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Minimum length must be at least 1")
        return v

    @field_validator("starting_sequence_number")
    @classmethod
    def validate_starting_sequence_number(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Starting sequence number must be non-negative")
        return v


class UpsertFieldEmailInputRequest(BaseUpsertFieldRequest):
    default_value: Optional[EmailStr] = Field(
        None, description="Default email value for the field"
    )


class UpsertFieldEmojiRequest(BaseUpsertFieldRequest):
    emojis: List[Dict[str, str]] = Field(
        default_factory=lambda: [
            {"value": "⭐", "score": "1"},
            {"value": "⭐", "score": "2"},
            {"value": "⭐", "score": "3"},
            {"value": "⭐", "score": "4"},
            {"value": "⭐", "score": "5"},
        ],
        description="Array of emoji objects with value and score",
    )
    show_not_applicable_option: bool = Field(
        True, description="Whether to show 'Not applicable' option"
    )
    not_applicable_string: str = Field(
        "Not applicable", description="Text for the not applicable option"
    )
    not_applicable_value: str = Field(
        "0", description="Value for the not applicable option"
    )
    emoji_size: int = Field(1, description="Size multiplier for emoji display (1-3)")

    VALID_EMOJIS: ClassVar[List[str]] = [
        "⭐",
        "🌟",
        "😀",
        "😛",
        "😡",
        "☹",
        "🤐",
        "🤩",
        "😐",
        "👏",
        "👍",
        "👎",
        "🙏",
        "💥",
        "🔥",
        "♥",
        "💘",
        "💙",
        "💚",
        "💛",
        "💜",
        "🧡",
        "❎",
        "🆒",
        "0️⃣",
        "1️⃣",
        "2️⃣",
        "3️⃣",
        "4️⃣",
        "5️⃣",
        "6️⃣",
        "7️⃣",
        "8️⃣",
        "9️⃣",
        "🔟",
        "✔",
        "☑",
        "✅",
        "🔵",
        "🟠",
        "🟡",
        "🟢",
        "◾",
        "◽",
        "⬛",
        "⬜",
        "🟥",
        "🟧",
        "🟨",
        "🟩",
        "🟪",
        "🟦",
        "🟫",
        "🔔",
        "🔕",
    ]

    @field_validator("emojis")
    @classmethod
    def validate_emojis(cls, v: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if not v:
            raise ValueError("Emojis list cannot be empty")

        for emoji in v:
            if "value" not in emoji or "score" not in emoji:
                raise ValueError("Each emoji must have 'value' and 'score' properties")
            if not emoji["value"] or not emoji["score"]:
                raise ValueError("Emoji value and score cannot be empty")

            if emoji["value"] not in cls.VALID_EMOJIS:
                raise ValueError(
                    f"Emoji '{emoji['value']}' is not in the allowed list. Allowed emojis: {', '.join(cls.VALID_EMOJIS)}"
                )

            try:
                score_num = float(emoji["score"])
                if score_num < 0:
                    raise ValueError(
                        f"Score '{emoji['score']}' must be a non-negative number"
                    )
            except ValueError:
                raise ValueError(f"Score '{emoji['score']}' must be a valid number")

        return v

    @field_validator("emoji_size")
    @classmethod
    def validate_emoji_size(cls, v: int) -> int:
        if not (1 <= v <= 3):
            raise ValueError("Emoji size must be between 1 and 3")
        return v


class UpsertFieldFileRequest(BaseUpsertFieldRequest):
    allowed_file_types: List[str] = Field(
        default_factory=list, description="Array of allowed file types"
    )
    file_upload_limit: int = Field(
        10, description="Maximum number of files allowed (1-10)"
    )
    image_quality: ImageQuality = Field(
        ImageQuality.MEDIUM, description="Image quality for camera captures"
    )
    image_text: Optional[str] = Field(
        None,
        description="Text watermark on captured images, Example: 'Watermark' or {field_name}",
    )
    image_text_position: Optional[WatermarkPosition] = Field(
        None, description="Position of text watermark"
    )
    logo: Optional[str] = Field(None, description="Logo watermark on captured images")
    logo_position: Optional[WatermarkPosition] = Field(
        None, description="Position of logo watermark"
    )
    file_name_prefix: str = Field(
        "", description="Prefix for uploaded file names, Example: 'IMG' or {prefix}"
    )
    save_to_gallery: bool = Field(
        False, description="Whether to save captured images to device gallery"
    )
    allow_editing_camera_image: bool = Field(
        False, description="Whether to allow editing captured images"
    )

    @field_validator("allowed_file_types")
    @classmethod
    def validate_allowed_file_types(cls, v: List[str]) -> List[str]:
        valid_types = [
            allowed_file_type.value for allowed_file_type in AllowedFileTypes
        ]
        for file_type in v:
            if file_type not in valid_types:
                raise ValueError(
                    f"Invalid file type: {file_type}. Allowed types: {', '.join(valid_types)}"
                )
        return UniqueListValidator.validate_unique_strings(v, "Allowed file types")

    @field_validator("file_upload_limit")
    @classmethod
    def validate_file_upload_limit(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError("File upload limit must be between 1 and 10")
        return v

    @model_validator(mode="after")
    def validate_watermark_positions(self):
        if self.image_text_position and self.logo_position:
            if self.image_text_position == self.logo_position:
                raise ValueError("Logo and Image text position cannot be the same")
        return self

    @model_validator(mode="after")
    def validate_image_related_fields(self):
        has_image_upload = (
            not self.allowed_file_types
            or "images_camera_upload" in self.allowed_file_types
            or "images_gallery_upload" in self.allowed_file_types
        )

        if not has_image_upload:
            if self.image_text or self.image_text_position:
                raise ValueError(
                    "Image text fields are only applicable when image upload is allowed"
                )
            if self.logo or self.logo_position:
                raise ValueError(
                    "Logo fields are only applicable when image upload is allowed"
                )
            if self.save_to_gallery or self.allow_editing_camera_image:
                raise ValueError(
                    "Gallery and editing options are only applicable when image upload is allowed"
                )

        return self
