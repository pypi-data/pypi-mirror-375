from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .properties.base import Expression


class FillProperties(LayoutNode):
    class _FillPropertiesHelper(LayoutNode):
        fillColor: Expression | None = None
        image: Expression | None = None
        show: Expression | None = None
        transparency: Expression | None = None

    properties: _FillPropertiesHelper = Field(default_factory=_FillPropertiesHelper)
    selector: Selector | None = None


class IconProperties(LayoutNode):
    class _IconPropertiesHelper(LayoutNode):
        bottomMargin: Expression | None = None
        horizontalAlignment: Expression | None = None
        leftMargin: Expression | None = None
        lineColor: Expression | None = None
        lineTransparency: Expression | None = None
        lineWeight: Expression | None = None
        padding: Expression | None = None
        rightMargin: Expression | None = None
        shapeType: Expression | None = None
        show: Expression | None = None
        topMargin: Expression | None = None
        verticalAlignment: Expression | None = None

    properties: _IconPropertiesHelper = Field(default_factory=_IconPropertiesHelper)
    selector: Selector | None = None


class OutlineProperties(LayoutNode):
    class _OutlinePropertiesHelper(LayoutNode):
        lineColor: Expression | None = None
        roundEdge: Expression | None = None
        show: Expression | None = None
        transparency: Expression | None = None
        weight: Expression | None = None

    properties: _OutlinePropertiesHelper = Field(default_factory=_OutlinePropertiesHelper)
    selector: Selector | None = None


class ShapeProperties(LayoutNode):
    class _ShapePropertiesHelper(LayoutNode):
        roundEdge: Expression | None = None

    properties: _ShapePropertiesHelper = Field(default_factory=_ShapePropertiesHelper)
    selector: Selector | None = None


class TextProperties(LayoutNode):
    class _TextPropertiesHelper(LayoutNode):
        fontColor: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        horizontalAlignment: Expression | None = None
        leftMargin: Expression | None = None
        padding: Expression | None = None
        rightMargin: Expression | None = None
        show: Expression | None = None
        text: Expression | None = None
        topMargin: Expression | None = None
        verticalAlignment: Expression | None = None

    properties: _TextPropertiesHelper = Field(default_factory=_TextPropertiesHelper)
    selector: Selector | None = None


class ActionButtonProperties(LayoutNode):
    fill: list[FillProperties] = Field(default_factory=lambda: [FillProperties()])
    icon: list[IconProperties] = Field(default_factory=lambda: [IconProperties()])
    outline: list[OutlineProperties] = Field(default_factory=lambda: [OutlineProperties()])
    shape: list[ShapeProperties] = Field(default_factory=lambda: [ShapeProperties()])
    text: list[TextProperties] = Field(default_factory=lambda: [TextProperties()])


class ActionButton(BaseVisual):
    visualType: str = "actionButton"
    model_config = ConfigDict(extra="forbid")

    drillFilterOtherVisuals: bool = True
    objects: ActionButtonProperties = Field(default_factory=ActionButtonProperties)
