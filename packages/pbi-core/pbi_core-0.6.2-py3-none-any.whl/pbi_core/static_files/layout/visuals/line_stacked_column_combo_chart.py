from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        axisType: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None
        fillRule: Expression | None = None
        showAllDataPoints: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        backgroundColor: Expression | None = None
        backgroundTransparency: Expression | None = None
        color: Expression | None = None
        enableBackground: Expression | None = None
        fontSize: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelOrientation: Expression | None = None
        labelPosition: Expression | None = None
        show: Expression | None = None
        showAll: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)
    selector: Selector | None = None


class LegendProperties(LayoutNode):
    class _LegendPropertiesHelper(LayoutNode):
        legendMarkerRendering: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None

    properties: _LegendPropertiesHelper = Field(default_factory=_LegendPropertiesHelper)
    selector: Selector | None = None


class LineStylesProperties(LayoutNode):
    class _LineStylesPropertiesHelper(LayoutNode):
        lineStyle: Expression | None = None
        markerShape: Expression | None = None
        shadeArea: Expression | None = None
        showMarker: Expression | None = None
        showSeries: Expression | None = None
        stepped: Expression | None = None
        strokeWidth: Expression | None = None

    properties: _LineStylesPropertiesHelper = Field(default_factory=_LineStylesPropertiesHelper)
    selector: Selector | None = None


class SmallMultiplesLayoutProperties(LayoutNode):
    class _SmallMultiplesLayoutPropertiesHelper(LayoutNode):
        gridLineColor: Expression | None = None
        gridLineStyle: Expression | None = None
        gridLineType: Expression | None = None
        gridPadding: Expression | None = None
        rowCount: Expression | None = None

    properties: _SmallMultiplesLayoutPropertiesHelper = Field(default_factory=_SmallMultiplesLayoutPropertiesHelper)


class SubheaderProperties(LayoutNode):
    class _SubheaderPropertiesHelper(LayoutNode):
        fontSize: Expression | None = None

    properties: _SubheaderPropertiesHelper = Field(default_factory=_SubheaderPropertiesHelper)


class ValueAxisProperties(LayoutNode):
    class _ValueAxisPropertiesHelper(LayoutNode):
        alignZeros: Expression | None = None
        end: Expression | None = None
        gridlineShow: Expression | None = None
        secEnd: Expression | None = None
        secShow: Expression | None = None
        secStart: Expression | None = None
        start: Expression | None = None
        show: Expression | None = None

    properties: _ValueAxisPropertiesHelper = Field(default_factory=_ValueAxisPropertiesHelper)
    selector: Selector | None = None


class LineStackedColumnComboChartProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    legend: list[LegendProperties] = Field(default_factory=lambda: [LegendProperties()])
    lineStyles: list[LineStylesProperties] = Field(default_factory=lambda: [LineStylesProperties()])
    smallMultiplesLayout: list[SmallMultiplesLayoutProperties] = Field(
        default_factory=lambda: [SmallMultiplesLayoutProperties()],
    )
    subheader: list[SubheaderProperties] = Field(default_factory=lambda: [SubheaderProperties()])
    valueAxis: list[ValueAxisProperties] = Field(default_factory=lambda: [ValueAxisProperties()])


class LineStackedColumnComboChart(BaseVisual):
    visualType: str = "lineStackedColumnComboChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: LineStackedColumnComboChartProperties = Field(default_factory=LineStackedColumnComboChartProperties)
