from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class AnomalyDetectionProperties(LayoutNode):
    class _AnomalyDetectionPropertiesHelper(LayoutNode):
        confidenceBandColor: Expression | None = None
        displayName: Expression | None = None
        explainBy: Expression | None = None
        markerColor: Expression | None = None
        markerShape: Expression | None = None
        show: Expression | None = None
        transform: Expression | None = None
        transparency: Expression | None = None

    properties: _AnomalyDetectionPropertiesHelper = Field(default_factory=_AnomalyDetectionPropertiesHelper)
    selector: Selector | None = None


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        axisType: Expression | None = None
        concatenateLabels: Expression | None = None
        end: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineShow: Expression | None = None
        labelColor: Expression | None = None
        maxMarginFactor: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        titleColor: Expression | None = None
        titleFontFamily: Expression | None = None
        titleFontSize: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)
    selector: Selector | None = None


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        fill: Expression | None = None
        showAllDataPoints: Expression | None = None

    properties: _DataPointPropertiesHelper = Field(default_factory=_DataPointPropertiesHelper)
    selector: Selector | None = None


class ForecastProperties(LayoutNode):
    class _ForecastPropertiesHelper(LayoutNode):
        show: Expression | None = None
        displayName: Expression | None = None
        lineColor: Expression | None = None
        transform: Expression | None = None

    properties: _ForecastPropertiesHelper = Field(default_factory=_ForecastPropertiesHelper)
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        responsive: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        color: Expression | None = None
        labelPosition: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        labelDensity: Expression | None = None
        show: Expression | None = None
        showAll: Expression | None = None
        showSeries: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)
    selector: Selector | None = None


class LegendProperties(LayoutNode):
    class _LegendPropertiesHelper(LayoutNode):
        defaultToCircle: Expression | None = None
        fontSize: Expression | None = None
        labelColor: Expression | None = None
        legendMarkerRendering: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        showTitle: Expression | None = None
        titleText: Expression | None = None

    properties: _LegendPropertiesHelper = Field(default_factory=_LegendPropertiesHelper)


class LineStylesProperties(LayoutNode):
    class _LineStylesPropertiesHelper(LayoutNode):
        lineStyle: Expression | None = None
        markerColor: Expression | None = None
        markerShape: Expression | None = None
        markerSize: Expression | None = None
        showMarker: Expression | None = None
        showSeries: Expression | None = None
        stepped: Expression | None = None
        strokeLineJoin: Expression | None = None
        strokeWidth: Expression | None = None

    properties: _LineStylesPropertiesHelper = Field(default_factory=_LineStylesPropertiesHelper)
    selector: Selector | None = None


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
        end: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineColor: Expression | None = None
        gridlineShow: Expression | None = None
        gridlineStyle: Expression | None = None
        gridlineThickness: Expression | None = None
        labelColor: Expression | None = None
        labelDensity: Expression | None = None
        labelDisplayUnits: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        titleFontFamily: Expression | None = None
        titleText: Expression | None = None

    properties: _ValueAxisPropertiesHelper = Field(default_factory=_ValueAxisPropertiesHelper)


class Y1AxisReferenceLineProperties(LayoutNode):
    class _Y1AxisReferenceLinePropertiesHelper(LayoutNode):
        displayName: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        style: Expression | None = None

    properties: _Y1AxisReferenceLinePropertiesHelper = Field(default_factory=_Y1AxisReferenceLinePropertiesHelper)
    selector: Selector | None = None


class Y2AxisProperties(LayoutNode):
    class _Y2AxisPropertiesHelper(LayoutNode):
        show: Expression | None = None

    properties: _Y2AxisPropertiesHelper = Field(default_factory=_Y2AxisPropertiesHelper)


class ZoomProperties(LayoutNode):
    class _ZoomPropertiesHelper(LayoutNode):
        show: Expression | None = None
        categoryMax: Expression | None = None
        categoryMin: Expression | None = None
        valueMax: Expression | None = None
        valueMin: Expression | None = None

    properties: _ZoomPropertiesHelper = Field(default_factory=_ZoomPropertiesHelper)


class LineChartProperties(LayoutNode):
    anomalyDetection: list[AnomalyDetectionProperties] = Field(
        default_factory=lambda: [AnomalyDetectionProperties()],
    )
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    forecast: list[ForecastProperties] = Field(default_factory=lambda: [ForecastProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    legend: list[LegendProperties] = Field(default_factory=lambda: [LegendProperties()])
    lineStyles: list[LineStylesProperties] = Field(default_factory=lambda: [LineStylesProperties()])
    plotArea: list[PlotAreaProperties] = Field(default_factory=lambda: [PlotAreaProperties()])
    trend: list[TrendProperties] = Field(default_factory=lambda: [TrendProperties()])
    valueAxis: list[ValueAxisProperties] = Field(default_factory=lambda: [ValueAxisProperties()])
    zoom: list[ZoomProperties] = Field(default_factory=lambda: [ZoomProperties()])
    y1AxisReferenceLine: list[Y1AxisReferenceLineProperties] = Field(
        default_factory=lambda: [Y1AxisReferenceLineProperties()],
    )
    y2Axis: list[Y2AxisProperties] = Field(default_factory=lambda: [Y2AxisProperties()])


class LineChart(BaseVisual):
    visualType: str = "lineChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: LineChartProperties = Field(default_factory=LineChartProperties)
