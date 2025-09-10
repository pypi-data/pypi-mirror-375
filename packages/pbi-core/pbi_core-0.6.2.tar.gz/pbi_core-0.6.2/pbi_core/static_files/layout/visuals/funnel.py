from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        color: Expression | None = None
        show: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None
        showAllDataPoints: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        color: Expression | None = None
        fontSize: Expression | None = None
        funnelLabelStyle: Expression | None = None
        labelDisplayUnits: Expression | None = None
        percentageLabelPrecision: Expression | None = None
        show: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)


class PercentBarLabelProperties(LayoutNode):
    class _PercentBarLabelPropertiesHelper(LayoutNode):
        color: Expression | None = None
        show: Expression | None = None

    properties: _PercentBarLabelPropertiesHelper = Field(default_factory=_PercentBarLabelPropertiesHelper)


class FunnelProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    percentBarLabel: list[PercentBarLabelProperties] = Field(
        default_factory=lambda: [PercentBarLabelProperties()],
    )


class Funnel(BaseVisual):
    visualType: str = "funnel"
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: FunnelProperties = Field(default_factory=FunnelProperties)
