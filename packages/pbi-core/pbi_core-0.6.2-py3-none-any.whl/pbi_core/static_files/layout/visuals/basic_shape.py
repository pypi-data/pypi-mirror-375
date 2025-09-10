from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import BaseVisual
from .properties.base import Expression


class FillProperties(LayoutNode):
    class _FillPropertiesHelper(LayoutNode):
        fillColor: Expression | None = None
        show: Expression | None = None
        transparency: Expression | None = None

    properties: _FillPropertiesHelper = Field(default_factory=_FillPropertiesHelper)


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        shapeType: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LineProperties(LayoutNode):
    class _LinePropertiesHelper(LayoutNode):
        lineColor: Expression | None = None
        roundEdge: Expression | None = None
        transparency: Expression | None = None
        weight: Expression | None = None

    properties: _LinePropertiesHelper = Field(default_factory=_LinePropertiesHelper)


class RotationProperties(LayoutNode):
    class _RotationPropertiesHelper(LayoutNode):
        angle: Expression | None = None

    properties: _RotationPropertiesHelper = Field(default_factory=_RotationPropertiesHelper)


class BasicShapeProperties(LayoutNode):
    fill: list[FillProperties] = Field(default_factory=lambda: [FillProperties()])
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    line: list[LineProperties] = Field(default_factory=lambda: [LineProperties()])
    rotation: list[RotationProperties] = Field(default_factory=lambda: [RotationProperties()])


class BasicShape(BaseVisual):
    visualType: str = "basicShape"
    model_config = ConfigDict(extra="forbid")

    drillFilterOtherVisuals: bool = True
    objects: BasicShapeProperties = Field(default_factory=BasicShapeProperties)
