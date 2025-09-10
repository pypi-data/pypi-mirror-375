from typing import List, Any, Optional
from ....enums import (
    FilterOperator,
    LogicalOperator,
    DateToken,
    DimensionType,
    SortDirection,
    SortType,
    ChartDimensionInterval,
    AggregationType,
)
from datetime import datetime, date
from enum import Enum
from typing import Dict, Any
from pydantic import Field, BaseModel, ConfigDict
from ...json_serialized import JsonSerializableMixin



class ExternalCondition(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    """
    Represents a filter condition for external filter validation and conversion.

    This class defines the structure for filter conditions that can be applied to
    Clappia app submissions. It supports various field types including text, numeric,
    date, and selection fields with appropriate operator validation.

    Validation Rules:
    - Field must exist in app definition or be a reserved field
    - Field type must be searchable (text, numeric, date, selection fields)
    - Operator must be compatible with field type
    - Values must match field type requirements
    - Date BETWEEN operations require dateToken
    - Selection field values must match field options
    - Numeric field values must be valid numbers
    - Text field values must be non-empty strings
    - App-related field values must be string IDs

    Supported Field Types:
    - Text fields: TextInput, TextArea, EmailInput, UniqueSequential, CodeReader,
      Address, ManualAddress, Toggle, UrlInput, Formula, GoogleSheet, DependencyApp
    - Numeric fields: Counter, Slider, NumberInput, Emoji
    - Date fields: Date, DateV2
    - Selection fields: Select, Radio, Checkbox
    - Reserved fields: $submissionId, $status, $createdAt, $updatedAt

    Supported Operators by Field Type:
    - Text fields: CONTAINS, NOT_IN, STARTS_WITH, EQ, NEQ, EMPTY, NON_EMPTY
    - Numeric fields: CONTAINS, NOT_IN, EQ, NEQ, GT, GTE, LT, LTE, EMPTY, NON_EMPTY, STARTS_WITH
    - Date fields: BETWEEN, EMPTY, NON_EMPTY
    - Selection fields: EQ, NEQ, EMPTY, NON_EMPTY

    Examples:
        # Text field filter
        condition = ExternalCondition(
            condition_field_name="customerName",
            condition_field_operator=FilterOperator.CONTAINS,
            condition_field_values=["John"]
        )

        # Date field filter with token
        date_condition = ExternalCondition(
            condition_field_name="orderDate",
            condition_field_operator=FilterOperator.BETWEEN,
            condition_field_values=["2024-01-01", "2024-12-31"],
            condition_field_date_token=DateToken.CUSTOM
        )

        # Numeric field filter
        numeric_condition = ExternalCondition(
            condition_field_name="salary",
            condition_field_operator=FilterOperator.GT,
            condition_field_values=[50000]
        )
    """

    condition_field_name: str = Field(
        description="Name of the field to filter on. Can be a custom field or reserved field. "
        "Reserved fields: $submissionId, $status, $createdAt, $updatedAt, $owners, $all_fields. "
        "Example: 'customerName', '$status', '$createdAt'"
    )
    condition_field_operator: FilterOperator = Field(
        description="Operator to apply to the field. Text fields support: CONTAINS, NOT_IN, STARTS_WITH, "
        "EQ, NEQ, EMPTY, NON_EMPTY. Numeric fields support: CONTAINS, NOT_IN, EQ, NEQ, GT, "
        "GTE, LT, LTE, EMPTY, NON_EMPTY, STARTS_WITH. Date fields support: BETWEEN, EMPTY, "
        "NON_EMPTY. Selection fields support: EQ, NEQ, EMPTY, NON_EMPTY. "
        "Example: 'CONTAINS', 'EQ', 'BETWEEN', 'EMPTY'"
    )
    condition_field_values: List[Any] = Field(
        description="Array of values to filter by. Not required for EMPTY/NON_EMPTY operators. "
        "For BETWEEN date operations, requires exactly 2 values (start and end date). "
        "For selection fields, values must match field options. For numeric fields, "
        "values must be valid numbers. For text fields, values must be non-empty strings. "
        "For app-related fields, values must be string IDs. "
        "Example: ['John', 'Jane'], [100, 200], ['2024-01-01', '2024-12-31']"
    )
    condition_field_date_token: Optional[DateToken] = Field(
        default=None,
        description="Date token for date field filtering. Only valid for date fields with BETWEEN operator. "
        "Required for date BETWEEN operations. CUS = Custom date range, TOD = Today, YES = Yesterday. "
        "Example: 'CUS', 'TOD', 'YES'",
    )


class ExternalFilter(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    """
    Represents an external filter for Clappia app submissions with comprehensive validation.

    This class provides a complete filter structure that includes a condition and logical operator
    for combining multiple filters. It supports validation against field definitions and conversion
    to internal filter format.

    The filter validation ensures:
    - Filter and condition objects are present
    - Field names are valid strings
    - Operators are valid for the field type
    - Values match field type requirements
    - Date operations have proper date tokens
    - Selection values match field options
    - Numeric values are valid numbers
    - Text values are non-empty strings
    - Reserved fields follow specific validation rules

    Validation Errors:
    - BadRequestError when filter is null/undefined
    - BadRequestError when filter.condition is missing
    - BadRequestError when conditionFieldName is missing or not a string
    - BadRequestError when conditionFieldOperator is missing or invalid
    - BadRequestError when logicalOperator is invalid
    - BadRequestError when field doesn't exist in app definition or reserved fields
    - BadRequestError when field type is not searchable
    - BadRequestError when operator is incompatible with field type
    - BadRequestError when conditionFieldValues is missing/invalid for non-EMPTY operators
    - BadRequestError when date values are invalid for CUSTOM date tokens
    - BadRequestError when conditionFieldDateToken is missing for date BETWEEN operations
    - BadRequestError when conditionFieldDateToken is used on non-date fields
    - BadRequestError when numeric values are invalid for numeric field types
    - BadRequestError when toggle values are not alphanumeric
    - BadRequestError when email values are invalid for email fields
    - BadRequestError when selection values don't match field options
    - BadRequestError when app-related field values are not string IDs
    - BadRequestError when reserved field values don't match expected format

    Examples:
        # Basic text filter
        filter = ExternalFilter(
            condition=ExternalCondition(
                condition_field_name="customerName",
                condition_field_operator=FilterOperator.CONTAINS,
                condition_field_values=["John"]
            ),
            logical_operator=LogicalOperator.AND
        )

        # Date filter with token
        date_filter = ExternalFilter(
            condition=ExternalCondition(
                condition_field_name="orderDate",
                condition_field_operator=FilterOperator.BETWEEN,
                condition_field_values=["2024-01-01", "2024-12-31"],
                condition_field_date_token=DateToken.CUSTOM
            )
        )

        # Numeric range filter
        numeric_filter = ExternalFilter(
            condition=ExternalCondition(
                condition_field_name="salary",
                condition_field_operator=FilterOperator.BETWEEN,
                condition_field_values=[30000, 80000]
            ),
            logical_operator=LogicalOperator.OR
        )
    """

    condition: ExternalCondition = Field(
        description="Filter condition defining the field, operator, and values to filter by. "
        "Validation rules: Field must exist in app definition or be a reserved field. "
        "Field type must be searchable. Operator must be compatible with field type. "
        "Values must match field type requirements. Date BETWEEN operations require dateToken. "
        "Selection field values must match field options. Numeric field values must be valid numbers. "
        "Text field values must be non-empty strings. App-related field values must be string IDs. "
        "Reserved fields ($submissionId, $status, $createdAt, $updatedAt) have specific validation rules."
    )
    logical_operator: LogicalOperator = Field(
        default=LogicalOperator.AND,
        description="Logical operator to combine with other filters. Default: 'AND'. "
        "Used when multiple filters are applied to the same chart. "
        "Example: 'AND', 'OR'",
    )

class ExternalChartDimension(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    """
    Represents an external chart dimension for analytics with comprehensive validation.

    This class provides the external interface for chart dimensions, allowing users
    to specify field names instead of field IDs. It supports validation and conversion
    to internal chart dimension format.

    The dimension supports:
    - Custom and standard field dimensions
    - Date-based dimensions with time intervals
    - Configurable sorting (direction and type)
    - Missing value handling
    - Field name to field ID mapping

    Validation Rules:
    - Field name must exist in app definition or be a standard field
    - Date intervals only applicable for date fields
    - Sort type must match field data type
    - Missing value should be appropriate for field type

    Examples:
        # Basic external dimension
        external_dim = ExternalChartDimension(
            dimension_field_name="category",
            dimension_label="Product Category",
            dimension_type=DimensionType.CUSTOM
        )

        # Date dimension with interval and sorting
        date_external_dim = ExternalChartDimension(
            dimension_field_name="order_date",
            dimension_label="Order Date",
            dimension_type=DimensionType.CUSTOM,
            dimension_interval=ChartDimensionInterval.MONTH,
            dimension_sort_direction=SortDirection.ASC,
            dimension_sort_type=SortType.STRING
        )
    """

    dimension_field_name: str = Field(
        description="Name of the field to use as dimension. Can be a custom field or standard field. "
        "Example: 'category', 'region', 'date', 'status'"
    )
    dimension_label: Optional[str] = Field(
        default=None,
        description="Display label for the dimension. Example: 'Category', 'Region', 'Date Range'",
    )
    dimension_type: Optional[DimensionType] = Field(
        default=DimensionType.CUSTOM,
        description="Type of dimension field. Example: 'STANDARD', 'CUSTOM'",
    )
    dimension_interval: Optional[ChartDimensionInterval] = Field(
        default=None,
        description="Interval for date-based dimensions. Only applicable for date fields. "
        "Example: 'day', 'week', 'month', 'year'",
    )
    dimension_sort_direction: Optional[SortDirection] = Field(
        default=SortDirection.ASC,
        description="Sort direction for the dimension values. Example: 'asc', 'desc'",
    )
    dimension_sort_type: Optional[SortType] = Field(
        default=SortType.STRING,
        description="Type of sorting to apply to dimension values. Example: 'number', 'string'",
    )
    dimension_missing_value: Optional[str] = Field(
        default=None,
        description="Value to use when dimension field data is missing. Example: 'Unknown', 'N/A'",
    )


class ExternalAggregation(BaseModel, JsonSerializableMixin):
    model_config = ConfigDict(str_strip_whitespace=True, validate_assignment=True)
    """
    Represents an external aggregation for analytics with comprehensive validation.

    This class provides the external interface for aggregation operations, allowing users
    to specify field names instead of field IDs. It supports validation and conversion
    to internal aggregation format.

    The aggregation supports:
    - Various aggregation types (count, sum, average, minimum, maximum, unique)
    - Custom and standard field operands
    - Field name to field ID mapping
    - Validation of aggregation type compatibility with field types

    Validation Rules:
    - Aggregation type must be valid
    - Operand field must exist in app definition or be a standard field
    - Aggregation type must be compatible with field data type
    - Numeric aggregations (sum, average, min, max) require numeric fields
    - Count and unique aggregations work with any field type

    Examples:
        # Count aggregation
        count_external_agg = ExternalAggregation(
            aggregation_type=AggregationType.COUNT,
            aggregation_field=ExternalChartDimension(
                dimension_field_name="id",
                dimension_label="Count",
                dimension_type=DimensionType.STANDARD
            )
        )

        # Sum aggregation on custom field
        sum_external_agg = ExternalAggregation(
            aggregation_type=AggregationType.SUM,
            aggregation_field=ExternalChartDimension(
                dimension_field_name="amount",
                dimension_label="Total Amount",
                dimension_type=DimensionType.CUSTOM
            )
        )

        # Average aggregation with sorting
        avg_external_agg = ExternalAggregation(
            aggregation_type=AggregationType.AVERAGE,
            aggregation_field=ExternalChartDimension(
                dimension_field_name="rating",
                dimension_label="Average Rating",
                dimension_type=DimensionType.CUSTOM,
                dimension_sort_direction=SortDirection.DESC
            )
        )
    """

    aggregation_type: AggregationType = Field(
        description="Type of aggregation to perform on the data. "
        "Example: 'count', 'sum', 'average', 'minimum', 'maximum', 'unique'"
    )
    aggregation_field: ExternalChartDimension = Field(
        description="Field to aggregate on. Defines which field the aggregation will be performed on."
    )
