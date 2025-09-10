from typing import List, Optional, Literal, Any, Dict
from pydantic import Field, field_validator
from ..base import BaseUpsertChartRequest
from ..model import ExternalAggregation, ExternalChartDimension


class UpsertBarChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Bar Chart definition.

    Mirrors the ExternalBarChartDefinition from the TS code. Supports:
    - Aggregation dimensions (required, at least one)
    - Grouping dimensions (required, at least one)
    - Stacked configuration (optional)
    - Direction configuration (optional, Horizontal/Vertical)
    """

    aggregation_dimensions: List[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the bar chart. Defines what data to aggregate and how to display it."
    )
    dimensions: List[ExternalChartDimension] = Field(
        description="Array of dimensions for the bar chart. Defines how to group and categorize the data."
    )
    is_stacked: Optional[bool] = Field(
        default=None,
        description="Whether to display bars as stacked or grouped. Default: false. Example: true for stacked bars, false for grouped bars",
    )
    direction: Optional[Literal["Horizontal", "Vertical"]] = Field(
        default=None,
        description="Direction of the bar chart. Example: 'Horizontal' for horizontal bars, 'Vertical' for vertical bars",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_aggregation_dimensions(
        cls, v: List[ExternalAggregation]
    ) -> List[ExternalAggregation]:
        if not v or len(v) == 0:
            raise ValueError(
                "aggregation_dimensions must contain at least one aggregation"
            )
        return v

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions(
        cls, v: List[ExternalChartDimension]
    ) -> List[ExternalChartDimension]:
        if not v or len(v) == 0:
            raise ValueError("dimensions must contain at least one dimension")
        return v

    @field_validator("is_stacked")
    @classmethod
    def validate_is_stacked(cls, v: Optional[bool]) -> Optional[bool]:
        if v is not None and not isinstance(v, bool):
            raise ValueError("is_stacked should be a boolean if provided")
        return v


class UpsertDataTableChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Data Table chart definition.

    Mirrors the ExternalDataTableChartDefinition from the TS code. Supports:
    - Aggregation dimensions (required, at least one, maximum 4)
    - Grouping dimensions (required, at least one)
    """

    aggregation_dimensions: List[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the data table. Defines what data to aggregate and display in columns. Maximum 4 aggregations allowed."
    )
    dimensions: List[ExternalChartDimension] = Field(
        description="Array of dimensions for the data table. Defines how to group and categorize the data in rows."
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_aggregation_dimensions_dt(
        cls, v: List[ExternalAggregation]
    ) -> List[ExternalAggregation]:
        if not v or len(v) == 0:
            raise ValueError(
                "aggregation_dimensions must contain at least one aggregation"
            )
        if len(v) > 4:
            raise ValueError(
                "aggregation_dimensions cannot exceed 4 aggregations for data table charts"
            )
        return v


class UpsertDoughnutChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Doughnut chart definition.

    Mirrors the ExternalDoughnutChartDefinition from the TS code. Supports:
    - Exactly one aggregation dimension
    - Exactly one grouping dimension
    - Optional legend visibility flag
    """

    aggregation_dimensions: List[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the doughnut chart. Only one aggregation dimension is allowed."
    )
    dimensions: List[ExternalChartDimension] = Field(
        description="Array of dimensions for the doughnut chart. Only one dimension is allowed."
    )
    show_legend: Optional[bool] = Field(
        default=None,
        description="Whether to display the legend for the doughnut chart. Default: true. Example: true to show legend, false to hide legend",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_aggregation_dimensions_doughnut(
        cls, v: List[ExternalAggregation]
    ) -> List[ExternalAggregation]:
        if not v or len(v) == 0:
            raise ValueError(
                "aggregation_dimensions must contain exactly one aggregation"
            )
        if len(v) > 1:
            raise ValueError(
                "Only one aggregation dimension is allowed for doughnut charts"
            )
        return v

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions_doughnut(
        cls, v: List[ExternalChartDimension]
    ) -> List[ExternalChartDimension]:
        if not v or len(v) == 0:
            raise ValueError("dimensions must contain exactly one dimension")
        if len(v) > 1:
            raise ValueError("Only one dimension is allowed for doughnut charts")
        return v

    @field_validator("show_legend")
    @classmethod
    def validate_show_legend(cls, v: Optional[bool]) -> Optional[bool]:
        if v is not None and not isinstance(v, bool):
            raise ValueError("show_legend should be a boolean if provided")
        return v

    @field_validator("dimensions")
    @classmethod
    def validate_dimensions_dt(
        cls, v: List[ExternalChartDimension]
    ) -> List[ExternalChartDimension]:
        if not v or len(v) == 0:
            raise ValueError("dimensions must contain at least one dimension")
        return v


class UpsertGanttChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Gantt chart definition.

    Mirrors the ExternalGanttChartDefinition from the TS code. Supports:
    - Exactly 5 dimensions in order: task Id, resource, task name, start date, end date
    - Optional dependency, completion, milestone dimensions
    - Optional additional dimensions
    """

    dimensions: List[ExternalChartDimension] = Field(
        description=(
            "Array of 5 dimensions for the gantt chart in order of task Id, "
            "resource, task name, start date and end date."
        )
    )
    dependencies_dimension: Optional[ExternalChartDimension] = Field(
        default=None, description="Dimension for task dependencies."
    )
    completion_dimension: Optional[ExternalChartDimension] = Field(
        default=None, description="Dimension for task completion status."
    )
    milestone_dimension: Optional[ExternalChartDimension] = Field(
        default=None, description="Dimension for milestone information."
    )
    additional_dimensions: Optional[List[ExternalChartDimension]] = Field(
        default=None, description="Additional dimensions for the gantt chart."
    )

    @field_validator("dimensions")
    @classmethod
    def validate_gantt_dimensions(
        cls, v: List[ExternalChartDimension]
    ) -> List[ExternalChartDimension]:
        if not v or len(v) != 5:
            raise ValueError(
                "dimensions must be an array of exactly 5 items: task Id, resource, task name, start date and end date"
            )
        return v


class UpsertLineChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Line chart definition.

    Mirrors the ExternalLineChartDefinition from the TS code. Supports:
    - Aggregation dimensions (required, at least one; first used for Y axis)
    - Grouping dimensions (required, at least one; first used for X axis)
    - Optional fill area flag
    """

    aggregation_dimensions: List[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the line chart."
    )
    dimensions: List[ExternalChartDimension] = Field(
        description="Array of dimensions for the line chart."
    )
    fill: Optional[bool] = Field(
        default=None,
        description="Whether to fill the area under the line. Default: false.",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_line_aggregation_dimensions(
        cls, v: List[ExternalAggregation]
    ) -> List[ExternalAggregation]:
        if not v or len(v) == 0:
            raise ValueError(
                "aggregation_dimensions must contain at least one aggregation"
            )
        return v


class UpsertMapChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Map chart definition.

    Mirrors the ExternalMapChartDefinition from the TS code. Supports:
    - Exactly two dimensions: gps location and label (in this order)
    """

    dimensions: List[ExternalChartDimension] = Field(
        description=(
            "Array of 2 dimensions for the map chart in order of gps location and label."
        )
    )

    @field_validator("dimensions")
    @classmethod
    def validate_map_dimensions(
        cls, v: List[ExternalChartDimension]
    ) -> List[ExternalChartDimension]:
        if not v or len(v) != 2:
            raise ValueError(
                "dimensions must be an array of exactly 2 items: gps location and label"
            )
        return v


class UpsertPieChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Pie chart definition.

    Mirrors the ExternalPieChartDefinition from the TS code. Supports:
    - Exactly one aggregation dimension
    - Exactly one grouping dimension
    - Optional legend visibility flag
    """

    aggregation_dimensions: List[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the pie chart. Only one aggregation dimension is allowed."
    )
    dimensions: List[ExternalChartDimension] = Field(
        description="Array of dimensions for the pie chart. Only one dimension is allowed."
    )
    show_legend: Optional[bool] = Field(
        default=None,
        description="Whether to display the legend for the pie chart. Default: true.",
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_pie_aggregation_dimensions(
        cls, v: List[ExternalAggregation]
    ) -> List[ExternalAggregation]:
        if not v or len(v) == 0:
            raise ValueError(
                "aggregation_dimensions must contain exactly one aggregation"
            )
        if len(v) > 1:
            raise ValueError("Only one aggregation dimension is allowed for pie charts")
        return v

    @field_validator("dimensions")
    @classmethod
    def validate_pie_dimensions(
        cls, v: List[ExternalChartDimension]
    ) -> List[ExternalChartDimension]:
        if not v or len(v) == 0:
            raise ValueError("dimensions must contain exactly one dimension")
        if len(v) > 1:
            raise ValueError("Only one dimension is allowed for pie charts")
        return v

    @field_validator("show_legend")
    @classmethod
    def validate_pie_show_legend(cls, v: Optional[bool]) -> Optional[bool]:
        if v is not None and not isinstance(v, bool):
            raise ValueError("show_legend should be a boolean if provided")
        return v


class UpsertSummaryChartDefinitionRequest(BaseUpsertChartRequest):
    """Request model for configuring a Summary Card chart definition.

    Mirrors the ExternalSummaryChartDefinition from the TS code. Supports:
    - Exactly one aggregation dimension
    """

    aggregation_dimensions: List[ExternalAggregation] = Field(
        description="Array of aggregation dimensions for the summary chart. Only one aggregation dimension is allowed."
    )

    @field_validator("aggregation_dimensions")
    @classmethod
    def validate_summary_aggregation_dimensions(
        cls, v: List[ExternalAggregation]
    ) -> List[ExternalAggregation]:
        if not v or len(v) == 0:
            raise ValueError(
                "aggregation_dimensions must contain exactly one aggregation"
            )
        if len(v) > 1:
            raise ValueError(
                "Only one aggregation dimension is allowed for summary charts"
            )
        return v
