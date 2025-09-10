from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class ColumnFormattingProperties(LayoutNode):
    class _ColumnFormattingPropertiesHelper(LayoutNode):
        class _DataBarsProperties(LayoutNode):
            axisColor: Expression | None = None
            hideText: Expression | None = None
            negativeColor: Expression | None = None
            positiveColor: Expression | None = None
            reverseDirection: Expression | None = None

        alignment: Expression | None = None
        backColor: Expression | None = None
        dataBars: _DataBarsProperties | None = None
        fontColor: Expression | None = None
        labelDisplayUnits: Expression | None = None
        labelPrecision: Expression | None = None
        styleHeader: Expression | None = None
        styleValues: Expression | None = None

    properties: _ColumnFormattingPropertiesHelper = Field(default_factory=_ColumnFormattingPropertiesHelper)
    selector: Selector | None = None


class ColumnHeadersProperties(LayoutNode):
    class _ColumnHeadersPropertiesHelper(LayoutNode):
        alignment: Expression | None = None
        autoSizeColumnWidth: Expression | None = None
        backColor: Expression | None = None
        bold: Expression | None = None
        fontColor: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        outline: Expression | None = None
        outlineStyle: Expression | None = None
        underline: Expression | None = None
        wordWrap: Expression | None = None

    properties: _ColumnHeadersPropertiesHelper = Field(default_factory=_ColumnHeadersPropertiesHelper)
    selector: Selector | None = None


class ColumnWidthProperties(LayoutNode):
    class _ColumnWidthPropertiesHelper(LayoutNode):
        value: Expression | None = None

    properties: _ColumnWidthPropertiesHelper = Field(default_factory=_ColumnWidthPropertiesHelper)
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        pass

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class GridProperties(LayoutNode):
    class _GridPropertiesHelper(LayoutNode):
        gridHorizontal: Expression | None = None
        gridHorizontalColor: Expression | None = None
        gridHorizontalWeight: Expression | None = None
        gridVertical: Expression | None = None
        gridVerticalColor: Expression | None = None
        gridVerticalWeight: Expression | None = None
        imageHeight: Expression | None = None
        outlineColor: Expression | None = None
        outlineWeight: Expression | None = None
        rowPadding: Expression | None = None
        textSize: Expression | None = None

    properties: _GridPropertiesHelper = Field(default_factory=_GridPropertiesHelper)
    selector: Selector | None = None


class TotalProperties(LayoutNode):
    class _TotalPropertiesHelper(LayoutNode):
        fontColor: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        outline: Expression | None = None
        totals: Expression | None = None

    properties: _TotalPropertiesHelper = Field(default_factory=_TotalPropertiesHelper)
    selector: Selector | None = None


class ValuesProperties(LayoutNode):
    class _ValuesPropertiesHelper(LayoutNode):
        backColor: Expression | None = None
        backColorPrimary: Expression | None = None
        backColorSecondary: Expression | None = None
        fontColor: Expression | None = None
        fontColorPrimary: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        outline: Expression | None = None
        underline: Expression | None = None
        urlIcon: Expression | None = None
        wordWrap: Expression | None = None

    properties: _ValuesPropertiesHelper = Field(default_factory=_ValuesPropertiesHelper)
    selector: Selector | None = None


class TableChartColumnProperties(LayoutNode):
    columnFormatting: list[ColumnFormattingProperties] = Field(
        default_factory=lambda: [ColumnFormattingProperties()],
    )
    columnHeaders: list[ColumnHeadersProperties] = Field(default_factory=lambda: [ColumnHeadersProperties()])
    columnWidth: list[ColumnWidthProperties] = Field(default_factory=lambda: [ColumnWidthProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    grid: list[GridProperties] = Field(default_factory=lambda: [GridProperties()])
    total: list[TotalProperties] = Field(default_factory=lambda: [TotalProperties()])
    values: list[ValuesProperties] = Field(default_factory=lambda: [ValuesProperties()])


class TableChart(BaseVisual):
    visualType: str = "tableEx"
    objects: TableChartColumnProperties = Field(default_factory=TableChartColumnProperties)
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
