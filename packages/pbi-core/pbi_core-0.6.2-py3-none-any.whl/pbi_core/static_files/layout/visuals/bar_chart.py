from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class CategoryAxisProperties(LayoutNode):
    class _CategoryAxisPropertiesHelper(LayoutNode):
        axisStyle: Expression | None = None
        axisType: Expression | None = None
        concatenateLabels: Expression | None = None
        end: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineShow: Expression | None = None
        innerPadding: Expression | None = None
        invertAxis: Expression | None = None
        italic: Expression | None = None
        labelColor: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelPrecision: Expression | None = None
        logAxisScale: Expression | None = None
        maxMarginFactor: Expression | None = None
        position: Expression | None = None
        preferredCategoryWidth: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        switchAxisPosition: Expression | None = None
        titleColor: Expression | None = None
        titleFontFamily: Expression | None = None
        titleFontSize: Expression | None = None
        titleItalic: Expression | None = None
        titleText: Expression | None = None

    properties: _CategoryAxisPropertiesHelper = Field(default_factory=_CategoryAxisPropertiesHelper)


class DataPointProperties(LayoutNode):
    class _DataPointPropertiesHelper(LayoutNode):
        borderColorMatchFill: Expression | None = None
        borderShow: Expression | None = None
        borderSize: Expression | None = None
        borderTransparency: Expression | None = None
        fill: Expression | None = None
        fillRule: Expression | None = None
        fillTransparency: Expression | None = None
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
        detailFontFamily: Expression | None = None
        detailItalic: Expression | None = None
        enableBackground: Expression | None = None
        enableDetailDataLabel: Expression | None = None
        enableTitleDataLabel: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        italic: Expression | None = None
        labelContainerMaxWidth: Expression | None = None
        labelContentLayout: Expression | None = None
        labelDensity: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelOverflow: Expression | None = None
        labelPosition: Expression | None = None
        labelPrecision: Expression | None = None
        optimizeLabelDisplay: Expression | None = None
        show: Expression | None = None
        showAll: Expression | None = None
        showBlankAs: Expression | None = None
        titleColor: Expression | None = None
        titleFontFamily: Expression | None = None
        titleFontSize: Expression | None = None
        titleItalic: Expression | None = None
        titleShowBlankAs: Expression | None = None
        titleTransparency: Expression | None = None
        titleUnderline: Expression | None = None
        transparency: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)
    selector: Selector | None = None


class LayoutProperties(LayoutNode):
    class _LayoutPropertiesHelper(LayoutNode):
        ribbonGapSize: Expression | None = None

    properties: _LayoutPropertiesHelper = Field(default_factory=_LayoutPropertiesHelper)


class LegendProperties(LayoutNode):
    class _LegendPropertiesHelper(LayoutNode):
        fontSize: Expression | None = None
        labelColor: Expression | None = None
        position: Expression | None = None
        show: Expression | None = None
        showTitle: Expression | None = None
        titleText: Expression | None = None

    properties: _LegendPropertiesHelper = Field(default_factory=_LegendPropertiesHelper)


class RibbonBandsProperties(LayoutNode):
    class _RibbonBandsPropertiesHelper(LayoutNode):
        borderColorMatchFill: Expression | None = None
        borderShow: Expression | None = None
        borderTransparency: Expression | None = None
        color: Expression | None = None
        fillTransparency: Expression | None = None
        show: Expression | None = None
        transparency: Expression | None = None

    properties: _RibbonBandsPropertiesHelper = Field(default_factory=_RibbonBandsPropertiesHelper)


class ValueAxisProperties(LayoutNode):
    class _ValueAxisPropertiesHelper(LayoutNode):
        axisScale: Expression | None = None
        bold: Expression | None = None
        end: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        gridlineColor: Expression | None = None
        gridlineShow: Expression | None = None
        invertAxis: Expression | None = None
        labelColor: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelPrecision: Expression | None = None
        logAxisScale: Expression | None = None
        show: Expression | None = None
        showAxisTitle: Expression | None = None
        start: Expression | None = None
        titleFontFamily: Expression | None = None
        titleColor: Expression | None = None
        titleFontColor: Expression | None = None
        titleFontSize: Expression | None = None
        titleText: Expression | None = None

    properties: _ValueAxisPropertiesHelper = Field(default_factory=_ValueAxisPropertiesHelper)


class XAxisReferenceLineProperties(LayoutNode):
    class _XAxisReferenceLinePropertiesHelper(LayoutNode):
        displayName: Expression | None = None
        show: Expression | None = None
        value: Expression | None = None

    properties: _XAxisReferenceLinePropertiesHelper = Field(default_factory=_XAxisReferenceLinePropertiesHelper)
    selector: Selector | None = None


class ZoomProperties(LayoutNode):
    class _ZoomPropertiesHelper(LayoutNode):
        show: Expression | None = None
        showLabels: Expression | None = None
        showTooltip: Expression | None = None

    properties: _ZoomPropertiesHelper = Field(default_factory=_ZoomPropertiesHelper)


class BarChartProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] = Field(default_factory=lambda: [CategoryAxisProperties()])
    dataPoint: list[DataPointProperties] = Field(default_factory=lambda: [DataPointProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    layout: list[LayoutProperties] = Field(default_factory=lambda: [LayoutProperties()])
    legend: list[LegendProperties] = Field(default_factory=lambda: [LegendProperties()])
    ribbonBands: list[RibbonBandsProperties] = Field(default_factory=lambda: [RibbonBandsProperties()])
    valueAxis: list[ValueAxisProperties] = Field(default_factory=lambda: [ValueAxisProperties()])
    xAxisReferenceLine: list[XAxisReferenceLineProperties] = Field(
        default_factory=lambda: [XAxisReferenceLineProperties()],
    )
    zoom: list[ZoomProperties] = Field(default_factory=lambda: [ZoomProperties()])


class BarChart(BaseVisual):
    visualType: str = "barChart"
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
    objects: BarChartProperties = Field(default_factory=BarChartProperties)
