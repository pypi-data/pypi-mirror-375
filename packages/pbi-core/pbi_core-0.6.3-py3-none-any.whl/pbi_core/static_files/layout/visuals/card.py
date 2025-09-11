from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual, ColumnProperty
from .properties.base import Expression


class CategoryLabelsProperties(LayoutNode):
    class _CategoryLabelsPropertiesHelper(LayoutNode):
        color: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        show: Expression | None = None

    properties: _CategoryLabelsPropertiesHelper = Field(default_factory=_CategoryLabelsPropertiesHelper)
    selector: Selector | None = None


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        pass

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LabelsProperties(LayoutNode):
    class _LabelsPropertiesHelper(LayoutNode):
        color: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        labelPrecision: Expression | None = None
        labelDisplayUnits: Expression | None = None
        preserveWhitespace: Expression | None = None

    properties: _LabelsPropertiesHelper = Field(default_factory=_LabelsPropertiesHelper)
    selector: Selector | None = None


class WordWrapProperties(LayoutNode):
    class _WordWrapperPropertiesHelper(LayoutNode):
        show: Expression | None = None

    properties: _WordWrapperPropertiesHelper = Field(default_factory=_WordWrapperPropertiesHelper)


class CardProperties(LayoutNode):
    categoryLabels: list[CategoryLabelsProperties] = Field(default_factory=lambda: [CategoryLabelsProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    labels: list[LabelsProperties] = Field(default_factory=lambda: [LabelsProperties()])
    wordWrap: list[WordWrapProperties] = Field(default_factory=lambda: [WordWrapProperties()])


class Card(BaseVisual):
    visualType: str = "card"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: CardProperties = Field(default_factory=CardProperties)
