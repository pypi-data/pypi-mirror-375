from typing import Optional, Literal, List, Dict, Any, Union
from ..base import BaseUpsertWorkflowStepRequest
from pydantic import Field, field_validator, model_validator, EmailStr, BaseModel
from .....enums import NodeType, DatabaseType
import re
import json
from urllib.parse import urlparse


class UpsertAiWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """
    Request model for configuring an AI workflow step.

    This request defines the instructions, model, and provider to be used
    for AI-based processing within a workflow step.

    **Allowed LLM Providers and Models:**
    - OpenAI:
        - gpt-4
        - gpt-4o
        - gpt-4o-mini
        - gpt-4-turbo-preview
        - o1-mini
        - o1-preview
        - gpt-3.5-turbo
    - Claude:
        - claude-2
        - claude-2.1
        - claude-3-haiku-20240307
        - claude-3-sonnet-20240229
        - claude-3-opus-latest
        - claude-3-5-sonnet-latest
        - claude-3-5-haiku-latest
        - claude-3-7-sonnet-latest
    - Gemini:
        - gemini-2.0-flash
        - gemini-2.0-flash-lite
        - gemini-1.5-flash
        - gemini-1.5-flash-8b
        - gemini-1.5-pro
    """

    instructions: str = Field(
        description="Instructions for the AI model to process. Can include field references for dynamic content. Example: 'Analyze the sentiment of {customerFeedback} and provide a summary'"
    )
    model: str = Field(
        description="The AI model to use for processing. Must match one of the allowed models listed in the class docstring."
    )
    llm: Literal["OpenAI", "Claude", "Gemini"] = Field(
        description="The Large Language Model provider to use. Allowed values: 'OpenAI', 'Claude', 'Gemini'."
    )

    @model_validator(mode="after")
    def validate_ai_configuration(self):
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

        if self.llm and self.model:
            if self.llm in model_options_map:
                if self.model not in model_options_map[self.llm]:
                    raise ValueError(
                        f"Model '{self.model}' is not supported for LLM provider '{self.llm}'"
                    )

        if not self.instructions or not self.instructions.strip():
            raise ValueError("Instructions are required for AI workflow step")

        return self


class UpsertApprovalWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for approval workflow step configuration"""

    approvers: List[str] = Field(
        description="Array of email addresses of approvers. Can include actual emails or field references. Example: ['manager@company.com', '{supervisorField}', 'finance@company.com']"
    )
    allowed_approval_statuses: List[str] = Field(
        description="Array of allowed approval statuses. Example: ['approved', 'rejected', 'pending']. This should be as same as the status present the definition of the app. Hence before using this field, you should check the statuses present in the app definition."
    )
    subject: str = Field(
        description="Subject line for the approval email. Can include field references. Example: 'Approval required for {requestType}'"
    )
    body: str = Field(
        description="Body content for the approval email. Can include field references and HTML formatting. Example: 'Please review and approve the {requestType} for {amount}'"
    )
    expiry: int = Field(
        ge=1, le=50, description="Expiry time in days (1-50). Example: 7 for 7 days"
    )
    print_template_indices: Optional[List[int]] = Field(
        None,
        description="Array of template indices to include as attachments. Example: [0, 2] for first and third templates",
    )

    @field_validator("approvers")
    @classmethod
    def validate_approvers(cls, v: List[str]) -> List[str]:
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        for approver in v:
            trimmed = approver.strip()
            is_valid_email = email_regex.match(trimmed)
            is_valid_field = field_name_regex.match(trimmed)

            if not (is_valid_email or is_valid_field):
                raise ValueError(
                    f"Approver '{approver}' must be a valid email address or field reference. "
                    f"Example: 'manager@company.com' or '{{supervisorField}}'"
                )

        return v

    @field_validator("allowed_approval_statuses")
    @classmethod
    def validate_allowed_approval_statuses(cls, v: List[str]) -> List[str]:
        if len(set(v)) != len(v):
            raise ValueError("Allowed approval statuses must be unique")

        return v


class UpsertCodeWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for code workflow step configuration"""

    output_fields: List[str] = Field(
        description="Array of output field names that the code will generate. Example: ['result', 'status', 'message']"
    )
    code: str = Field(
        default="""function main() {
    // Your code here
    output = {};
    var num1 = Math.round(Math.random()*10);
    var num2 = Math.round(Math.random()*10);
    output['sum'] = num1 + num2 ; // You can also use {field_name} to reference fields
    output['prod'] = num1 * num2; // You can also use {field_name} to reference fields
    return output;
}""",
        description="JavaScript code to execute. Should return an object with keys matching the output fields.",
    )

    @field_validator("output_fields")
    @classmethod
    def validate_output_fields(cls, v: List[str]) -> List[str]:
        if len(set(v)) != len(v):
            raise ValueError("Output fields must be unique")

        return v


class UpsertConditionWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for condition workflow step configuration"""

    condition: str = Field(
        description="Condition expression to evaluate, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10"
    )


class UpsertDatabaseWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for database workflow step configuration"""

    database_type: DatabaseType = Field(
        description="Type of database to connect to. Must be one of: MySql, PostgreSql, AzureSql. Example: 'MySql'"
    )
    database_host: str = Field(
        description="Database host address. Example: 'localhost' or 'db.example.com'"
    )
    database_port: str = Field(
        description="Database port number. Example: '3306' for MySQL, '5432' for PostgreSQL"
    )
    database_username: str = Field(
        description="Database username for authentication. Example: 'dbuser'"
    )
    database_password: str = Field(
        description="Database password for authentication. Example: 'password123'"
    )
    database_name: str = Field(
        description="Name of the database to connect to. Example: 'myapp_db'"
    )
    database_query: str = Field(
        description="SQL query to execute. Can include field references for dynamic queries. Example: 'SELECT * FROM users WHERE id = {userIdField}'"
    )
    database_output_fields: Optional[List[str]] = Field(
        None,
        description="Array of field names where query results will be stored. Can include field references. Example: ['resultField']",
    )

    @field_validator("database_port")
    @classmethod
    def validate_database_port(cls, v: str) -> str:
        # Check if it's a valid port number
        try:
            port_num = int(v.strip())
            if not (1 <= port_num <= 65535):
                raise ValueError("Database port must be between 1 and 65535")
        except ValueError:
            raise ValueError("Database port must be a valid number")

        return v.strip()

    @field_validator("database_host")
    @classmethod
    def validate_database_host(cls, v: str) -> str:
        # Basic hostname/IP validation
        host = v.strip()
        if not re.match(r"^[a-zA-Z0-9.-]+$", host):
            raise ValueError("Database host must be a valid hostname or IP address")

        return host

    @field_validator("database_output_fields")
    @classmethod
    def validate_database_output_fields(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        if v is not None:
            # Check for duplicates
            if len(set(v)) != len(v):
                raise ValueError("Database output fields must be unique")

        return v


class StaticAttachment(BaseModel):
    """Model for static file attachments"""

    base64: str = Field(
        description="Base64 encoded file data. Example: 'data:image/jpeg;base64,/9j/4AAQ...'"
    )
    content_type: str = Field(
        description="MIME type of the file. Example: 'image/jpeg', 'application/pdf'"
    )
    file_name: str = Field(
        description="Name of the file. Example: 'document.pdf', 'image.jpg'"
    )

    @field_validator("base64")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Base64 data cannot be empty")
        return v.strip()

    @field_validator("content_type")
    @classmethod
    def validate_content_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Content type cannot be empty")
        return v.strip()

    @field_validator("file_name")
    @classmethod
    def validate_file_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("File name cannot be empty")
        return v.strip()


class UpsertEmailWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for email workflow step configuration"""

    to_email_addresses: List[str] = Field(
        description="Array of email addresses to send the email to. Can include actual email addresses or field references. Example: ['user@example.com', '{fieldName}', 'admin@company.com']"
    )
    cc_email_addresses: Optional[List[str]] = Field(
        None,
        description="Array of email addresses to CC. Can include actual email addresses or field references. Example: ['manager@example.com', '{supervisorField}']",
    )
    bcc_email_addresses: Optional[List[str]] = Field(
        None,
        description="Array of email addresses to BCC. Can include actual email addresses or field references. Example: ['hr@example.com', '{hrField}']",
    )
    subject: str = Field(
        description="Email subject line. Can include field references for dynamic content. Example: 'Order Confirmation for {orderNumber}' or 'Welcome {customerName}'"
    )
    body: str = Field(
        description="Email body content. Can include HTML formatting and field references. Example: 'Dear {customerName}, your order {orderId} has been confirmed.'"
    )
    static_attachments: Optional[List[StaticAttachment]] = Field(
        None, description="Array of static file attachments. Maximum 10 attachments."
    )
    print_template_indices: Optional[List[int]] = Field(
        None,
        description="Array of template indices to include as attachments. Indices correspond to templates in the app. Example: [0, 2] for first and third templates",
    )
    dynamic_attachments: Optional[List[str]] = Field(
        None,
        description="Array of file field names that contain file attachments to include. Only works when app has file fields. Example: ['documentField', 'imageField']",
    )
    reply_to: Optional[str] = Field(
        None,
        description="Reply-to email address. Can be an actual email or field reference. Example: 'noreply@company.com' or '{supportField}'",
    )

    @field_validator("to_email_addresses")
    @classmethod
    def validate_to_email_addresses(cls, v: List[str]) -> List[str]:
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        for email in v:
            trimmed = email.strip()
            is_valid_email = email_regex.match(trimmed)
            is_valid_field = field_name_regex.match(trimmed)

            if not (is_valid_email or is_valid_field):
                raise ValueError(
                    f"Email address '{email}' must be a valid email address or field reference. "
                    f"Example: 'user@example.com' or '{{fieldName}}'"
                )

        return v

    @field_validator("cc_email_addresses")
    @classmethod
    def validate_cc_email_addresses(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            email_regex = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

            for email in v:
                trimmed = email.strip()
                is_valid_email = email_regex.match(trimmed)
                is_valid_field = field_name_regex.match(trimmed)

                if not (is_valid_email or is_valid_field):
                    raise ValueError(
                        f"CC email address '{email}' must be a valid email address or field reference. "
                        f"Example: 'manager@example.com' or '{{supervisorField}}'"
                    )

        return v

    @field_validator("bcc_email_addresses")
    @classmethod
    def validate_bcc_email_addresses(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        if v is not None:
            email_regex = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

            for email in v:
                trimmed = email.strip()
                is_valid_email = email_regex.match(trimmed)
                is_valid_field = field_name_regex.match(trimmed)

                if not (is_valid_email or is_valid_field):
                    raise ValueError(
                        f"BCC email address '{email}' must be a valid email address or field reference. "
                        f"Example: 'hr@example.com' or '{{hrField}}'"
                    )

        return v

    @field_validator("static_attachments")
    @classmethod
    def validate_static_attachments(
        cls, v: Optional[List[StaticAttachment]]
    ) -> Optional[List[StaticAttachment]]:
        if v is not None:
            if len(v) > 10:
                raise ValueError("Static attachments can have at most 10 attachments")

        return v

    @field_validator("print_template_indices")
    @classmethod
    def validate_print_template_indices(
        cls, v: Optional[List[int]]
    ) -> Optional[List[int]]:
        if v is not None:
            for index in v:
                if not isinstance(index, int):
                    raise ValueError("All print template indices must be integers")
                if index < 0:
                    raise ValueError("Print template indices must be non-negative")

        return v

    @field_validator("dynamic_attachments")
    @classmethod
    def validate_dynamic_attachments(
        cls, v: Optional[List[str]]
    ) -> Optional[List[str]]:
        if v is not None:
            for attachment in v:
                if not isinstance(attachment, str) or not attachment.strip():
                    raise ValueError(
                        "All dynamic attachments must be non-empty strings"
                    )

        return v

    @field_validator("reply_to")
    @classmethod
    def validate_reply_to(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            email_regex = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

            trimmed = v.strip()
            is_valid_email = email_regex.match(trimmed)
            is_valid_field = field_name_regex.match(trimmed)

            if not (is_valid_email or is_valid_field):
                raise ValueError(
                    f"Reply-to '{v}' must be a valid email address or field reference. "
                    f"Example: 'noreply@company.com' or '{{supportField}}'"
                )

        return v


class UpsertLoopWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for loop workflow step configuration"""

    no_of_times: Union[int, str] = Field(
        description="Number of times to execute the loop or field reference containing the count. Can be a number or field name. Example: 5 or {loopCountField}"
    )
    break_condition: str = Field(
        description="Condition to break the loop early, supports multiple arithmetic operations (SUM, DIFF, PRODUCT, LOG...), logical operations (IF/ELSE, AND, OR, XOR, ...), string operations (CONCATENATE, LEN, TRIM, ...) and DATE/TIME operations (TODAY, NOW, DATEDIF, FORMAT) that are supported by Microsoft Excel. Example: {field_name} <> 'value' or {field_name} > 10"
    )
    allow_system_workflow_triggered_execution: bool = Field(
        False,
        description="Whether to allow system workflow triggered execution within the loop. Default: false. Example: true",
    )

    @field_validator("no_of_times")
    @classmethod
    def validate_no_of_times(cls, v: Union[int, str]) -> Union[int, str]:
        if isinstance(v, int):
            if v < 1:
                raise ValueError("Number of times must be at least 1")
            return v
        elif isinstance(v, str):
            # Check if it's a valid field reference
            field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")
            if not field_name_regex.match(v.strip()):
                raise ValueError(
                    f"Field reference '{v}' must be a valid field name. "
                    f"Example: '{{loopCountField}}'"
                )
            return v.strip()
        else:
            raise ValueError(
                "Number of times must be either a number or a field reference string"
            )

    @field_validator("break_condition")
    @classmethod
    def validate_break_condition(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Break condition cannot be empty")
        return v.strip()


class UpsertMobileNotificationWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for mobile notification workflow step configuration"""

    users: List[str] = Field(
        description="Array of users to send mobile notifications to. Can include phone numbers, email addresses, or field references. Example: ['+91 1234567890', '{userField}', 'user@example.com', '{$allUsers}']"
    )
    subject: str = Field(
        description="Subject/title of the mobile notification. Can include field references. Example: 'Alert: {alertType}' or 'Order Update'"
    )
    body: str = Field(
        description="Body content of the mobile notification. Can include field references. Example: 'Your order {orderId} has been {status}'"
    )

    @field_validator("users")
    @classmethod
    def validate_users(cls, v: List[str]) -> List[str]:
        email_regex = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")
        phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
        special_user_regex = re.compile(
            r"^\{\$[a-zA-Z_][a-zA-Z0-9_]*\}$"
        )  # Special users like {$allUsers}

        for user in v:
            trimmed = user.strip()
            is_valid_email = email_regex.match(trimmed)
            is_valid_field = field_name_regex.match(trimmed)
            is_valid_phone = phone_regex.match(trimmed)
            is_valid_special = special_user_regex.match(trimmed)

            if not (
                is_valid_email or is_valid_field or is_valid_phone or is_valid_special
            ):
                raise ValueError(
                    f"User '{user}' must be a valid phone number, email address, field reference, or special user. "
                    f"Example: '+91 1234567890', 'user@example.com', '{{userField}}', or '{{$allUsers}}'"
                )

        return v


class RestApiOutputField(BaseModel):
    """Model for REST API output field mapping"""

    name: str = Field(description="Name of the output field")
    json_path_query: str = Field(
        description="JSONPath query to extract data from response"
    )
    x_path_query: str = Field(
        description="XPath query to extract data from XML response"
    )
    data_type: str = Field(
        description="Data type of the field (TEXT, DATE, LOCATION, etc.)"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Output field name cannot be empty")
        return v.strip()

    @field_validator("json_path_query")
    @classmethod
    def validate_json_path_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("JSONPath query cannot be empty")
        return v.strip()

    @field_validator("x_path_query")
    @classmethod
    def validate_x_path_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("XPath query cannot be empty")
        return v.strip()

    @field_validator("data_type")
    @classmethod
    def validate_data_type(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Data type cannot be empty")
        return v.strip()


class UpsertRestApiWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for REST API workflow step configuration"""

    server_url: str = Field(
        description="URL of the REST API endpoint. Example: 'https://api.example.com/data' or 'https://api.example.com/data/{id}' or {server_url}"
    )
    method_type: Literal["GET", "POST", "PATCH", "DELETE"] = Field(
        description="HTTP method type"
    )
    body_type: Optional[Literal["JSON", "XML", "FORM-DATA"]] = Field(
        None, description="Type of request body"
    )
    headers: Optional[str] = Field(
        "{}",
        description=(
            "HTTP headers as a JSON-formatted string. "
            "Keys are header names and values can be static strings or dynamic field references. "
            "Examples:\n"
            '- \'{"Content-Type": "application/json"}\'\n'
            '- \'{"Authorization": "{apiKey}"}\''
        ),
    )
    body: Optional[str] = Field(
        "{}",
        description='Request body as JSON string. Example: \'{"field_name": "value"}\' or \'{"field_name": "{field_name}"}\'',
    )
    query_string: Optional[str] = Field(
        None,
        description="URL query parameters. Example: '?field_name=value' or ?field_name={query_string}",
    )
    response_mapping: List[RestApiOutputField] = Field(
        description="Array of output field mappings for API response"
    )
    allow_system_workflow_triggered_execution: bool = Field(
        False, description="Whether to allow system workflow triggered execution"
    )

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Server URL cannot be empty")

        # Basic URL validation
        try:
            result = urlparse(v.strip())
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception:
            raise ValueError("Server URL must be a valid URL")

        return v.strip()

    @field_validator("headers", "body")
    @classmethod
    def validate_json_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            try:
                json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Must be valid JSON string")
        return v

    @field_validator("response_mapping")
    @classmethod
    def validate_response_mapping(
        cls, v: List[RestApiOutputField]
    ) -> List[RestApiOutputField]:
        if not v or len(v) == 0:
            raise ValueError("Response mapping is required")

        # Check for unique field names
        names = [field.name for field in v]
        if len(set(names)) != len(names):
            raise ValueError("Response mapping field names must be unique")

        return v

    @field_validator("query_string")
    @classmethod
    def validate_query_string(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not re.match(r"^[\s\w%&.=[\]{}\-]*$", v):
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
                    raise ValueError("Body must be valid JSON when body type is JSON")
            elif self.body_type == "FORM-DATA":
                try:
                    form_data = json.loads(self.body)
                    if not isinstance(form_data, dict) or len(form_data) == 0:
                        raise ValueError("Form data must be a non-empty JSON object")
                except json.JSONDecodeError:
                    raise ValueError("Form data must be valid JSON")
        return self


class UpsertSlackWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for Slack workflow step configuration"""

    slack_channel_id: str = Field(
        description="Slack webhook URL for the channel. Must be in the format https://hooks.slack.com/services/T123ABC456/B789DEF012/XYZ123WEBHOOK456"
    )
    subject: str = Field(
        description="Subject/title of the Slack message. Can include field references for dynamic content. Example: 'Alert: {alertType}' or 'Order Update for {orderId}'"
    )
    body: str = Field(
        description="Body content of the Slack message. Can include field references and formatting. Example: 'Order {orderId} has been {status} by {customerName}'"
    )

    @field_validator("slack_channel_id")
    @classmethod
    def validate_slack_channel_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Slack channel ID cannot be empty")

        # Slack webhook URL validation
        slack_webhook_regex = re.compile(
            r"https://hooks\.slack\.com/services/[A-Za-z0-9]+/[A-Za-z0-9]+/[A-Za-z0-9]+"
        )
        if not slack_webhook_regex.match(v.strip()):
            raise ValueError(
                "Slack channel ID must be a valid Slack webhook URL in the format "
                "https://hooks.slack.com/services/T123ABC456/B789DEF012/XYZ123WEBHOOK456"
            )

        return v.strip()


class UpsertSmsWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for SMS workflow step configuration"""

    phone_numbers: List[str] = Field(
        description="Array of phone numbers to send SMS to. Can include actual phone numbers or field references. Maximum 1 phone number. Example: ['+91 1234567890', '{phoneField}']"
    )
    sms_template_variables: Optional[List[Dict[str, str]]] = Field(
        None, description="Array of template variables for SMS template"
    )
    sms_template_id: Optional[str] = Field(
        None,
        description="SMS template ID for non-India workplaces. Required for non-India, not needed for India. Example: 'template_12345'",
    )
    body: Optional[str] = Field(
        None,
        description="SMS body content for India workplaces. Required for India, not needed for non-India. Can include field references. Example: 'Your order {orderId} has been confirmed'",
    )

    @field_validator("phone_numbers")
    @classmethod
    def validate_phone_numbers(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Phone numbers are required")

        if len(v) > 1:
            raise ValueError("Phone numbers can only have one phone number")

        phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        for phone in v:
            trimmed = phone.strip()
            is_valid_phone = phone_regex.match(trimmed)
            is_valid_field = field_name_regex.match(trimmed)

            if not (is_valid_phone or is_valid_field):
                raise ValueError(
                    f"Phone number '{phone}' must be a valid phone number or field reference. "
                    f"Example: '+91 1234567890' or '{{phoneField}}'"
                )

        return v

    @field_validator("sms_template_variables")
    @classmethod
    def validate_sms_template_variables(
        cls, v: Optional[List[Dict[str, str]]]
    ) -> Optional[List[Dict[str, str]]]:
        if v is not None:
            for i, variable in enumerate(v):
                if not isinstance(variable, dict) or len(variable) != 1:
                    raise ValueError(
                        f"SMS template variable at index {i} should be an object with a single key-value pair"
                    )

                key, value = next(iter(variable.items()))
                if (
                    not key
                    or not value
                    or not str(key).strip()
                    or not str(value).strip()
                ):
                    raise ValueError(
                        f"SMS template variable at index {i} should have non-empty key and value"
                    )

        return v

    @model_validator(mode="after")
    def validate_sms_requirements(self):
        if not self.sms_template_id and not self.body:
            raise ValueError(
                "Either SMS template ID or body is required. "
                "Body is required for India and Template ID is required for non-India, "
                "check the country of your workplace and provide the correct parameter"
            )
        return self


class UpsertWaitWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for wait workflow step configuration"""

    wait_till_date: Optional[str] = Field(
        None,
        description="Date to wait until (when using wait_till_date and wait_till_time). Can include field references. Example: '2024-12-31' or '{targetDateField}'",
    )
    wait_for: Optional[str] = Field(
        None,
        description="Duration to wait for in seconds. Can include field references. Example: '5000', '7200', '86400' or '{no_of_seconds}'",
    )
    wait_till_time: Optional[str] = Field(
        None,
        description="Time to wait until (when using wait_till_date and wait_till_time). Can include field references. Example: '14:30' or '{targetTimeField}'",
    )

    @model_validator(mode="after")
    def validate_wait_requirements(self):
        if not self.wait_for and (not self.wait_till_time or not self.wait_till_date):
            raise ValueError(
                "Either wait_for or both wait_till_date and wait_till_time are required"
            )
        return self


class UpsertWhatsAppWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for WhatsApp workflow step configuration"""

    phone_numbers: List[str] = Field(
        description="Array of phone numbers to send WhatsApp messages to. Can include actual phone numbers or field references. Example: ['+91 1234567890', '{phoneField}', '+911234567890', '{phoneField}']"
    )
    whatsapp_template_variables: Optional[List[Dict[str, str]]] = Field(
        None, description="Array of template variables for WhatsApp template"
    )
    whatsapp_template_id: str = Field(
        description="WhatsApp template ID. Example: 'template_12345'"
    )
    static_attachments: Optional[List[StaticAttachment]] = Field(
        None, description="Array of static file attachments. Maximum 1 attachment."
    )
    print_template_index: Optional[int] = Field(
        None,
        description="Index of template to include as attachment. Example: 0 for first template",
    )
    language: Optional[str] = Field(
        None,
        description="Language code for WhatsApp message. Example: 'en', 'es', 'fr'",
    )
    media_type: Optional[str] = Field(
        None,
        description="Type of media for WhatsApp message. Example: 'image', 'video', 'document'",
    )
    dynamic_image_field: Optional[str] = Field(
        None,
        description="Field name for file field used for dynamic image attachment. Example: 'imageField'",
    )

    @field_validator("phone_numbers")
    @classmethod
    def validate_phone_numbers(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Phone numbers are required")

        if len(v) > 1:
            raise ValueError("Phone numbers can have at most 1 phone number")

        phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
        field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

        for phone in v:
            trimmed = phone.strip()
            is_valid_phone = phone_regex.match(trimmed)
            is_valid_field = field_name_regex.match(trimmed)

            if not (is_valid_phone or is_valid_field):
                raise ValueError(
                    f"Phone number '{phone}' must be a valid phone number or field reference. "
                    f"Example: '+91 1234567890' or '{{phoneField}}'"
                )

        return v

    @field_validator("whatsapp_template_variables")
    @classmethod
    def validate_whatsapp_template_variables(
        cls, v: Optional[List[Dict[str, str]]]
    ) -> Optional[List[Dict[str, str]]]:
        if v is not None:
            for i, variable in enumerate(v):
                if not isinstance(variable, dict) or len(variable) != 1:
                    raise ValueError(
                        f"WhatsApp template variable at index {i} should be an object with a single key-value pair"
                    )

                key, value = next(iter(variable.items()))
                if (
                    not key
                    or not value
                    or not str(key).strip()
                    or not str(value).strip()
                ):
                    raise ValueError(
                        f"WhatsApp template variable at index {i} should have non-empty key and value"
                    )

        return v

    @field_validator("static_attachments")
    @classmethod
    def validate_static_attachments(
        cls, v: Optional[List[StaticAttachment]]
    ) -> Optional[List[StaticAttachment]]:
        if v is not None:
            if len(v) > 1:
                raise ValueError("Static attachments can have at most 1 attachment")

        return v

    @field_validator("print_template_index")
    @classmethod
    def validate_print_template_index(cls, v: Optional[int]) -> Optional[int]:
        if v is not None:
            if v < 0:
                raise ValueError("Print template index must be non-negative")

        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        WHATSAPP_LANGUAGE_CODES = [
            "af",
            "sq",
            "ar",
            "ar_EG",
            "ar_AE",
            "ar_LB",
            "ar_MA",
            "ar_QA",
            "az",
            "be_BY",
            "bn",
            "bn_IN",
            "bg",
            "ca",
            "zh_CN",
            "zh_HK",
            "zh_TW",
            "hr",
            "cs",
            "da",
            "prs_AF",
            "nl",
            "nl_BE",
            "en",
            "en_GB",
            "en_US",
            "en_AE",
            "en_AU",
            "en_CA",
            "en_GH",
            "en_IE",
            "en_IN",
            "en_JM",
            "en_MY",
            "en_NZ",
            "en_QA",
            "en_SG",
            "en_UG",
            "en_ZA",
            "et",
            "fil",
            "fi",
            "fr",
            "fr_BE",
            "fr_CA",
            "fr_CH",
            "fr_CI",
            "fr_MA",
            "ka",
            "de",
            "de_AT",
            "de_CH",
            "el",
            "gu",
            "ha",
            "he",
            "hi",
            "hu",
            "id",
            "ga",
            "it",
            "ja",
            "kn",
            "kk",
            "rw_RW",
            "ko",
            "ky_KG",
            "lo",
            "lv",
            "lt",
            "mk",
            "ms",
            "ml",
            "mr",
            "nb",
            "ps_AF",
            "fa",
            "pl",
            "pt_BR",
            "pt_PT",
            "pa",
            "ro",
            "ru",
            "sr",
            "si_LK",
            "sk",
            "sl",
            "es",
            "es_AR",
            "es_CL",
            "es_CO",
            "es_CR",
            "es_DO",
            "es_EC",
            "es_HN",
            "es_MX",
            "es_PA",
            "es_PE",
            "es_ES",
            "es_UY",
            "sw",
            "sv",
            "ta",
            "te",
            "th",
            "tr",
            "uk",
            "ur",
            "uz",
            "vi",
            "zu",
        ]
        if v is not None:
            if v not in WHATSAPP_LANGUAGE_CODES:
                raise ValueError(
                    f"Language must be one of: {', '.join(WHATSAPP_LANGUAGE_CODES)}"
                )

        return v

    @field_validator("media_type")
    @classmethod
    def validate_media_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_media_types = ["image", "video", "document", "audio"]
            if v.lower() not in valid_media_types:
                raise ValueError(
                    f"Media type must be one of: {', '.join(valid_media_types)}"
                )

        return v

    @model_validator(mode="after")
    def validate_whatsapp_requirements(self):
        # Validate that static_attachments and print_template_index are not provided together
        if (
            self.static_attachments
            and len(self.static_attachments) > 0
            and self.print_template_index is not None
        ):
            raise ValueError(
                "Static attachments and print template index cannot be provided together"
            )

        return self


class UpsertCreateSubmissionWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for create submission workflow step configuration"""

    target_app_id: str = Field(
        description="ID of the target app where the submission will be created. Example: 'app_12345'"
    )
    field_values_map: Dict[str, Any] = Field(
        description="Map of field names to values for the new submission, where the key is the field name of the target app and the value is the value to be set. Can include field references. Example: {'name': '{customerName}', 'email': 'customer@example.com'}"
    )
    submission_status: Optional[str] = Field(
        None,
        description="Initial status for the new submission. Can include field references. Example: 'pending' or '{initialStatusField}'",
    )
    comments: Optional[str] = Field(
        None,
        description="Comments to add to the new submission. Can include field references. Example: 'Created by workflow'",
    )
    submission_owners: Optional[List[str]] = Field(
        None,
        description="Array of email addresses or phone numbers for submission owners. Can include field references. Example: ['manager@company.com', '{ownerField}', '+911234567890']",
    )
    allow_system_workflow_triggered_execution: bool = Field(
        False,
        description="Whether to allow system workflow triggered execution. Default: false. Example: true",
    )

    @field_validator("target_app_id")
    @classmethod
    def validate_target_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Target app ID cannot be empty")
        return v.strip()

    @field_validator("field_values_map")
    @classmethod
    def validate_field_values_map(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v or len(v) == 0:
            raise ValueError("Field values map must contain at least one field")

        for key, value in v.items():
            if not key or not key.strip():
                raise ValueError("Field names in field values map cannot be empty")
            if value is None:
                raise ValueError(f"Field '{key}' value cannot be empty")

        return v

    @field_validator("submission_owners")
    @classmethod
    def validate_submission_owners(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            email_regex = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
            field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

            # Remove duplicates while preserving order
            unique_owners = list(dict.fromkeys(v))

            for owner in unique_owners:
                trimmed = owner.strip()
                is_valid_email = email_regex.match(trimmed)
                is_valid_phone = phone_regex.match(trimmed)
                is_valid_field = field_name_regex.match(trimmed)

                if not (is_valid_email or is_valid_phone or is_valid_field):
                    raise ValueError(
                        f"Submission owner '{owner}' must be a valid email address, phone number, or field reference. "
                        f"Example: 'manager@company.com', '+911234567890', or '{{ownerField}}'"
                    )

        return v


class UpsertDeleteSubmissionWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for delete submission workflow step configuration"""

    target_app_id: str = Field(
        description="ID of the target app where submissions will be deleted. Example: 'app_12345'"
    )
    filters: Dict[str, Any] = Field(
        description="Filters to find submissions to delete. Contains the keys value where the key is the field name of the target app and the value to be matched. Can include field references. Example: {'status': 'archived', 'userId': '{currentUserId}'}"
    )
    allow_multiple_deletes: bool = Field(
        False,
        description="Whether to allow deleting multiple submissions. Default: false. Example: true",
    )
    allow_system_workflow_triggered_execution: bool = Field(
        False,
        description="Whether to allow system workflow triggered execution. Default: false. Example: true",
    )

    @field_validator("target_app_id")
    @classmethod
    def validate_target_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Target app ID cannot be empty")
        return v.strip()

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v or len(v) == 0:
            raise ValueError("Filters must contain at least one field")

        for key, value in v.items():
            if not key or not key.strip():
                raise ValueError("Field names in filters cannot be empty")
            if value is None:
                raise ValueError(f"Filter field '{key}' value cannot be empty")

        return v


class SortField(BaseModel):
    """Model for sort field configuration"""

    sort_by: str = Field(
        description="Field name to sort by. Example: 'createdAt', 'name', 'status'"
    )
    direction: Literal["asc", "desc"] = Field(
        description="Sort direction. Must be 'asc' or 'desc'. Example: 'desc' for descending order"
    )


class UpsertFindSubmissionWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for find submission workflow step configuration"""

    target_app_id: str = Field(
        description="ID of the target app to search for submissions. Example: 'app_12345'"
    )
    filters: Dict[str, Any] = Field(
        description="Filters to find submissions, where the key is the field name of the target app and the value to be matched. Can include field references. Example: {'status': 'active', 'userId': '{currentUserId}'}"
    )
    selection_fields: List[str] = Field(
        description="Array of field names to include in the search results. Example: ['name', 'email', 'status']"
    )
    sort_fields: Optional[List[SortField]] = Field(
        None, description="Array of sort criteria. Maximum 3 fields."
    )

    @field_validator("target_app_id")
    @classmethod
    def validate_target_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Target app ID cannot be empty")
        return v.strip()

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v or len(v) == 0:
            raise ValueError("Filters must contain at least one field")

        for key, value in v.items():
            if not key or not key.strip():
                raise ValueError("Field names in filters cannot be empty")
            if value is None:
                raise ValueError(f"Filter field '{key}' value cannot be empty")

        return v

    @field_validator("selection_fields")
    @classmethod
    def validate_selection_fields(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("Selection fields must contain at least one field")

        for field in v:
            if not field or not field.strip():
                raise ValueError("Selection field names cannot be empty")

        return v

    @field_validator("sort_fields")
    @classmethod
    def validate_sort_fields(
        cls, v: Optional[List[SortField]]
    ) -> Optional[List[SortField]]:
        if v is not None:
            if len(v) > 3:
                raise ValueError("Sort fields should not have more than 3 fields")

            for i, sort_field in enumerate(v):
                if not isinstance(sort_field, SortField):
                    raise ValueError(
                        f"Sort field at index {i} must be a valid SortField object"
                    )

        return v


class UpsertEditSubmissionWorkflowStepRequest(BaseUpsertWorkflowStepRequest):
    """Request model for edit submission workflow step configuration"""

    target_app_id: str = Field(
        description="ID of the target app where submissions will be edited. Example: 'app_12345'"
    )
    filters: Dict[str, Any] = Field(
        description="Filters to find submissions to edit. Contains the keys value where the key is the field name of the target app and the value to be matched. Can include field references. Example: {'status': 'pending', 'userId': '{currentUserId}'}"
    )
    field_values_map: Dict[str, Any] = Field(
        description="Map of field names to new values, where the key is the field name of the target app and the value is the value to be set. Can include field references and cross-app references. Example: {'status': 'approved', 'approvedBy': '{sourceAppId_#_approverField}', 'name': '{sourceAppId_#_customerName}', 'email': '{targetAppId_#_customerEmail}'}"
    )
    submission_status: Optional[str] = Field(
        None,
        description="New status for the submission. Can include field references. Example: 'approved' or '{newStatusField}'",
    )
    comments: Optional[str] = Field(
        None,
        description="Comments to add to the submission. Can include field references. Example: 'Approved by {approverName}'",
    )
    submission_owners: Optional[List[str]] = Field(
        None,
        description="Array of email addresses or phone numbers for new submission owners. Can include field references. Example: ['manager@company.com', '{ownerField}', '+911234567890', '{phoneField}']",
    )
    keep_existing_owners: bool = Field(
        True,
        description="Whether to keep existing owners when adding new ones. Default: true. Example: false",
    )
    allow_multiple_edits: bool = Field(
        False,
        description="Whether to allow editing multiple submissions. Default: false. Example: true",
    )
    allow_system_workflow_triggered_execution: bool = Field(
        False,
        description="Whether to allow system workflow triggered execution. Default: false. Example: true",
    )

    @field_validator("target_app_id")
    @classmethod
    def validate_target_app_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Target app ID cannot be empty")
        return v.strip()

    @field_validator("filters")
    @classmethod
    def validate_filters(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v or len(v) == 0:
            raise ValueError("Filters must contain at least one field")

        for key, value in v.items():
            if not key or not key.strip():
                raise ValueError("Field names in filters cannot be empty")
            if value is None:
                raise ValueError(f"Filter field '{key}' value cannot be empty")

        return v

    @field_validator("field_values_map")
    @classmethod
    def validate_field_values_map(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        if not v or len(v) == 0:
            raise ValueError("Field values map must contain at least one field")

        for key, value in v.items():
            if not key or not key.strip():
                raise ValueError("Field names in field values map cannot be empty")
            if value is None:
                raise ValueError(f"Field '{key}' value cannot be empty")

        return v

    @field_validator("submission_owners")
    @classmethod
    def validate_submission_owners(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None:
            email_regex = re.compile(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            )
            phone_regex = re.compile(r"^\+?[1-9]\d{1,14}$")  # E.164 format
            field_name_regex = re.compile(r"^\{[a-zA-Z_][a-zA-Z0-9_]*\}$")

            # Remove duplicates while preserving order
            unique_owners = list(dict.fromkeys(v))

            for owner in unique_owners:
                trimmed = owner.strip()
                is_valid_email = email_regex.match(trimmed)
                is_valid_phone = phone_regex.match(trimmed)
                is_valid_field = field_name_regex.match(trimmed)

                if not (is_valid_email or is_valid_phone or is_valid_field):
                    raise ValueError(
                        f"Submission owner '{owner}' must be a valid email address, phone number, or field reference. "
                        f"Example: 'manager@company.com', '+911234567890', or '{{ownerField}}'"
                    )

        return v
