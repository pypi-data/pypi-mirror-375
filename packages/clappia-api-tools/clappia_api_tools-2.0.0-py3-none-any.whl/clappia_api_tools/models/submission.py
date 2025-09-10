from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationInfo
import re
from ..enums import (
    FilterOperator,
    FilterKeyType,
    LogicalOperator,
    DimensionType,
    SortDirection,
    AggregationType,
)

standard_fields = {
    "$submissionId",
    "$owner",
    "$status",
    "$lastUpdatedAt",
    "$lastModifiedAt",
    "$createdAt",
    "$updatedAt",
    "$state",
}


class FilterCondition(BaseModel):
    operator: FilterOperator = Field(
        description="Filter operator to apply, possible values are CONTAINS, NOT_IN, EQ, NEQ, EMPTY, NON_EMPTY, STARTS_WITH, BETWEEN, GT, LT, GTE, LTE",
    )
    filter_key_type: FilterKeyType = Field(
        description="Type of field being filtered, possible values are STANDARD, CUSTOM",
    )
    key: str = Field(
        min_length=1,
        description="Field key to filter on, use $submissionId, $owner, $status, $lastUpdatedAt, $lastModifiedAt, $createdAt, $updatedAt, $state for standard fields or the field name for custom fields",
    )
    value: Any = Field(description="Value to filter by")

    @field_validator("key")
    def validate_key(cls, v: str, values: ValidationInfo) -> str:
        filter_key_type = values.data.get("filter_key_type")
        if filter_key_type == "STANDARD":
            standard_fields = {
                "$submissionId",
                "$owner",
                "$status",
                "$lastUpdatedAt",
                "$lastModifiedAt",
                "$createdAt",
                "$updatedAt",
                "$state",
            }
            if v not in standard_fields:
                raise ValueError(
                    f"Standard filterKeyType used but key '{v}' is not a standard field"
                )
        return v

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator": self.operator,
            "filterKeyType": self.filter_key_type,
            "key": self.key,
            "value": self.value,
        }


class SubmissionQuery(BaseModel):
    conditions: List[FilterCondition] = Field(
        min_length=1, description="Array of filter conditions"
    )
    operator: LogicalOperator = Field(
        default="AND", description="Logical operator, possible values are AND, OR"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conditions": [condition.to_dict() for condition in self.conditions],
            "operator": self.operator,
        }


class SubmissionQueryGroup(BaseModel):
    queries: List[SubmissionQuery] = Field(
        min_length=1, description="Array of individual queries"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {"queries": [query.to_dict() for query in self.queries]}


class SubmissionFilters(BaseModel):
    queries: List[SubmissionQueryGroup] = Field(
        min_length=1, description="Array of query groups"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {"queries": [query_group.to_dict() for query_group in self.queries]}


class AggregationOperand(BaseModel):
    field_name: str = Field(description="Name of the field to aggregate")
    label: str = Field(description="Display label for the operand")
    data_type: str = Field(
        description="Data type of the operand field, use text, number, date, boolean, select for standard fields or the field type for custom fields"
    )
    dimension_type: DimensionType = Field(
        default="CUSTOM",
        description="Type of operand field, possible values are STANDARD, CUSTOM",
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fieldName": self.field_name,
            "label": self.label,
            "dataType": self.data_type,
            "dimensionType": self.dimension_type,
        }


class AggregationDimension(BaseModel):
    field_name: str = Field(description="Name of the field to group by")
    label: str = Field(description="Display label for the dimension")
    data_type: str = Field(
        description="Data type of the field, use text, number, date, boolean, select for standard fields or the field type for custom fields"
    )
    dimension_type: DimensionType = Field(
        default="CUSTOM",
        description="Type of dimension field, possible values are STANDARD, CUSTOM",
    )
    sort_direction: Optional[SortDirection] = Field(
        None, description="Sort direction, possible values are asc, desc"
    )
    sort_type: Optional[str] = Field(
        None, description="Type of sorting, possible values are number, string"
    )
    missing_value: Optional[str] = Field(
        None, description="Value when field data is missing"
    )
    interval: Optional[str] = Field(
        None, description="Interval for date/time grouping, use day, week, month, year"
    )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "fieldName": self.field_name,
            "label": self.label,
            "dataType": self.data_type,
            "dimensionType": self.dimension_type,
        }
        if self.sort_direction:
            result["sortDirection"] = self.sort_direction
        if self.sort_type:
            result["sortType"] = self.sort_type
        if self.missing_value is not None:
            result["missingValue"] = self.missing_value
        if self.interval:
            result["interval"] = self.interval
        return result


class AggregationMetric(BaseModel):
    type: AggregationType = Field(
        description="Type of aggregation, possible values are count, sum, average, minimum, maximum, unique"
    )
    operand: Optional[AggregationOperand] = Field(
        None, description="Field to aggregate"
    )

    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        if self.operand:
            result["operand"] = self.operand.to_dict()
        return result
