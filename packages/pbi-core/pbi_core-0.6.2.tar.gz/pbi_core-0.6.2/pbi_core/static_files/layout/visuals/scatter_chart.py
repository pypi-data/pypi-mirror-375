from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class BubblesProperties(LayoutNode):
    class _BubblesPropertiesHelper(LayoutNode):
        bubbleSize: Expression | None = None
        markerShape: Expression | None = None
        showSeries: Expression | None = None

    properties: _BubblesPropertiesHelper = Field(default_factory=_BubblesPropertiesHelper)
    selector: Selector | None = None


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        axisScale: Expression | None = None
        end: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineColor: Expression | None = None
        gridlineShow: Expression | None = None
        gridlineStyle: Expression | None = None
        innerPadding: Expression | None = None
        labelColor: Expression | None = None
        logAxisScale: Expression | None = None
        maxMarginFactor: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        titleColor: Expression | None = None
        titleFontFamily: Expression | None = None
        titleFontSize: Expression | None = None
        titleText: Expression | None = None
        treatNullsAsZero: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)


class CategoryLabelsProperties(LayoutNode):
    class _CategoryLabelsPropertiesHelper(LayoutNode):
        color: Expression | None = None
        enableBackground: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        show: Expression | None = None

    properties: _CategoryLabelsPropertiesHelper = Field(default_factory=_CategoryLabelsPropertiesHelper)


class ColorBorderProperties(LayoutNode):
    class _ColorBorderPropertiesHelper(LayoutNode):
        show: Expression | None = None

    properties: _ColorBorderPropertiesHelper = Field(default_factory=_ColorBorderPropertiesHelper)


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None
        fillRule: Expression | None = None
        legend: Expression | None = None
        showAllDataPoints: Expression | None = None
        valueAxis: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class FillPointProperties(LayoutNode):
    class _FillPointPropertiesHelper(LayoutNode):
        show: Expression | None = None
        style: Expression | None = None

    properties: _FillPointPropertiesHelper = Field(default_factory=_FillPointPropertiesHelper)


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        responsive: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LegendProperties(LayoutNode):
    class _LegendPropertiesHelper(LayoutNode):
        fontSize: Expression | None = None
        labelColor: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        showGradientLegend: Expression | None = None
        showTitle: Expression | None = None
        titleText: Expression | None = None

    properties: _LegendPropertiesHelper = Field(default_factory=_LegendPropertiesHelper)


class PlotAreaProperties(LayoutNode):
    class _PlotAreaPropertiesHelper(LayoutNode):
        transparency: Expression | None = None

    properties: _PlotAreaPropertiesHelper = Field(default_factory=_PlotAreaPropertiesHelper)


class ValueAxisProperties(LayoutNode):
    class _ValueAxisPropertiesHelper(LayoutNode):
        alignZeros: Expression | None = None
        axisScale: Expression | None = None
        end: Expression | None = None
        fontSize: Expression | None = None
        gridlineColor: Expression | None = None
        gridlineShow: Expression | None = None
        labelColor: Expression | None = None
        logAxisScale: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        switchAxisPosition: Expression | None = None
        titleColor: Expression | None = None
        titleFontFamily: Expression | None = None
        titleFontSize: Expression | None = None
        titleText: Expression | None = None
        treatNullsAsZero: Expression | None = None

    properties: _ValueAxisPropertiesHelper = Field(default_factory=_ValueAxisPropertiesHelper)


class Y1AxisReferenceLineProperties(LayoutNode):
    class _Y1AxisReferenceLinePropertiesHelper(LayoutNode):
        displayName: Expression | None = None
        lineColor: Expression | None = None
        show: Expression | None = None
        value: Expression | None = None

    properties: _Y1AxisReferenceLinePropertiesHelper = Field(default_factory=_Y1AxisReferenceLinePropertiesHelper)
    selector: Selector | None = None


class ScatterChartProperties(LayoutNode):
    bubbles: list[BubblesProperties] = Field(default_factory=lambda: [BubblesProperties()])
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    categoryLabels: list[CategoryLabelsProperties] = Field(default_factory=lambda: [CategoryLabelsProperties()])
    colorBorder: list[ColorBorderProperties] = Field(default_factory=lambda: [ColorBorderProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    fillPoint: list[FillPointProperties] = Field(default_factory=lambda: [FillPointProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    legend: list[LegendProperties] = Field(default_factory=lambda: [LegendProperties()])
    plotArea: list[PlotAreaProperties] = Field(default_factory=lambda: [PlotAreaProperties()])
    valueAxis: list[ValueAxisProperties] = Field(default_factory=lambda: [ValueAxisProperties()])
    y1AxisReferenceLine: list[Y1AxisReferenceLineProperties] = Field(
        default_factory=lambda: [Y1AxisReferenceLineProperties()],
    )


class ScatterChart(BaseVisual):
    visualType: str = "scatterChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: ScatterChartProperties = Field(default_factory=ScatterChartProperties)
