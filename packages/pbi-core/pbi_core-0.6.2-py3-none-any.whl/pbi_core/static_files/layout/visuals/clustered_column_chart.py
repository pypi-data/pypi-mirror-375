from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        axisType: Expression | None = None
        concatenateLabels: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineShow: Expression | None = None
        gridlineStyle: Expression | None = None
        innerPadding: Expression | None = None
        labelColor: Expression | None = None
        maxMarginFactor: Expression | None = None
        preferredCategoryWidth: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        titleColor: Expression | None = None
        titleFontSize: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None
        showAllDataPoints: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        responsive: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        backgroundTransparency: Expression | None = None
        color: Expression | None = None
        enableBackground: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelOrientation: Expression | None = None
        labelOverflow: Expression | None = None
        labelPosition: Expression | None = None
        labelPrecision: Expression | None = None
        show: Expression | None = None
        showAll: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)
    selector: Selector | None = None


class LegendProperties(LayoutNode):
    class _LegendPropertiesHelper(LayoutNode):
        fontSize: Expression | None = None
        labelColor: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        showTitle: Expression | None = None

    properties: _LegendPropertiesHelper = Field(default_factory=_LegendPropertiesHelper)


class PlotAreaProperties(LayoutNode):
    class _PlotAreaPropertiesHelper(LayoutNode):
        transparency: Expression | None = None

    properties: _PlotAreaPropertiesHelper = Field(default_factory=_PlotAreaPropertiesHelper)


class TrendProperties(LayoutNode):
    class _TrendPropertiesHelper(LayoutNode):
        displayName: Expression | None = None
        lineColor: Expression | None = None
        show: Expression | None = None

    properties: _TrendPropertiesHelper = Field(default_factory=_TrendPropertiesHelper)


class ValueAxisProperties(LayoutNode):
    class _ValueAxisPropertiesHelper(LayoutNode):
        axisScale: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineShow: Expression | None = None
        labelColor: Expression | None = None
        labelDisplayUnits: Expression | None = None
        logAxisScale: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        titleFontFamily: Expression | None = None

    properties: _ValueAxisPropertiesHelper = Field(default_factory=_ValueAxisPropertiesHelper)
    selector: Selector | None = None


class ClusteredColumnChartProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    legend: list[LegendProperties] = Field(default_factory=lambda: [LegendProperties()])
    plotArea: list[PlotAreaProperties] = Field(default_factory=lambda: [PlotAreaProperties()])
    trend: list[TrendProperties] = Field(default_factory=lambda: [TrendProperties()])
    valueAxis: list[ValueAxisProperties] = Field(default_factory=lambda: [ValueAxisProperties()])


class ClusteredColumnChart(BaseVisual):
    visualType: str = "clusteredColumnChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: ClusteredColumnChartProperties = Field(default_factory=ClusteredColumnChartProperties)
