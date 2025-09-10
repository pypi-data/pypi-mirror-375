from typing import Any

from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector
from pbi_core.static_files.layout.sources.paragraphs import Paragraph

from .base import BaseVisual
from .properties.base import Expression


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        paragraphs: list[Paragraph] | None = None
        responsive: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class ValueProperties(LayoutNode):
    class _ValuePropertiesHelper(LayoutNode):
        class _ValuePropertiesExpr(LayoutNode):
            context: Any | None = None  # TODO: should be Source, but causes circular import issues with Subquery
            expr: Any | None = None  # TODO: should be Source, but causes circular import issues with Subquery
            value: Any | None = None  # TODO: should be Source, but causes circular import issues with Subquery
            propertyDefinitionKind: str | None = None

        expr: _ValuePropertiesExpr = Field(default_factory=_ValuePropertiesExpr)
        formatString: Expression | None = None

    properties: _ValuePropertiesHelper = Field(default_factory=_ValuePropertiesHelper)
    selector: Selector | None = None


class TextBoxProperties(LayoutNode):
    general: list[GeneralProperties] = Field(default_factory=lambda: [GeneralProperties()])
    values: list[ValueProperties] = Field(default_factory=lambda: [ValueProperties()])


class TextBox(BaseVisual):
    visualType: str = "textbox"
    model_config = ConfigDict(extra="forbid")

    drillFilterOtherVisuals: bool = True
    objects: TextBoxProperties = Field(default_factory=TextBoxProperties)
