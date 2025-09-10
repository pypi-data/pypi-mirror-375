from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        axisType: Expression | None = None
        concatenateLabels: Expression | None = None
        fontSize: Expression | None = None
        gridlineColor: Expression | None = None
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
        titleText: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)
    selector: Selector | None = None


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None
        fillRule: Expression | None = None
        showAllDataPoints: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        responsive: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        backgroundColor: Expression | None = None
        backgroundTransparency: Expression | None = None
        color: Expression | None = None
        enableBackground: Expression | None = None
        fontSize: Expression | None = None
        labelDensity: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelOrientation: Expression | None = None
        labelPosition: Expression | None = None
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
    selector: Selector | None = None


class TotalProperties(LayoutNode):
    class _TotalPropertiesHelper(LayoutNode):
        show: Expression | None = None

    properties: _TotalPropertiesHelper = Field(default_factory=_TotalPropertiesHelper)


class ValueAxisProperties(LayoutNode):
    class _ValueAxisPropertiesHelper(LayoutNode):
        axisScale: Expression | None = None
        fontSize: Expression | None = None
        gridlineShow: Expression | None = None
        logAxisScale: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        titleFontFamily: Expression | None = None

    properties: _ValueAxisPropertiesHelper = Field(default_factory=_ValueAxisPropertiesHelper)
    selector: Selector | None = None


class Y1AxisReferenceLineProperties(LayoutNode):
    class _Y1AxisReferenceLinePropertiesHelper(LayoutNode):
        displayName: Expression | None = None
        lineColor: Expression | None = None
        show: Expression | None = None
        style: Expression | None = None
        transparency: Expression | None = None
        value: Expression | None = None

    properties: _Y1AxisReferenceLinePropertiesHelper = Field(default_factory=_Y1AxisReferenceLinePropertiesHelper)
    selector: Selector | None = None


class ZoomProperties(LayoutNode):
    class _ZoomPropertiesHelper(LayoutNode):
        show: Expression | None = None

    properties: _ZoomPropertiesHelper = Field(default_factory=_ZoomPropertiesHelper)


class ColumnChartColumnProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    legend: list[LegendProperties] = Field(default_factory=lambda: [LegendProperties()])
    valueAxis: list[ValueAxisProperties] = Field(default_factory=lambda: [ValueAxisProperties()])
    totals: list[TotalProperties] = Field(default_factory=lambda: [TotalProperties()])
    y1AxisReferenceLine: list[Y1AxisReferenceLineProperties] = Field(
        default_factory=lambda: [Y1AxisReferenceLineProperties()],
    )
    zoom: list[ZoomProperties] = Field(default_factory=lambda: [ZoomProperties()])


class ColumnChart(BaseVisual):
    visualType: str = "columnChart"
    model_config = ConfigDict(extra="forbid")

    objects: ColumnChartColumnProperties = Field(default_factory=ColumnChartColumnProperties)
    selector: Selector | None = None
    columnCount: Expression | None = None
    columnProperties: dict[str, ColumnProperty] | None = None
