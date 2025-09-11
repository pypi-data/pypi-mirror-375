from pydantic import Field

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import Expression


class BackgroundProperties(LayoutNode):
    class _BackgroundPropertiesHelper(LayoutNode):
        color: Expression | None = None
        show: Expression | None = None
        transparency: Expression | None = None

    properties: _BackgroundPropertiesHelper = Field(default_factory=_BackgroundPropertiesHelper)


class BorderProperties(LayoutNode):
    class _BorderPropertiesHelper(LayoutNode):
        background: Expression | None = None
        color: Expression | None = None
        radius: Expression | None = None
        show: Expression | None = None
        width: Expression | None = None

    properties: _BorderPropertiesHelper = Field(default_factory=_BorderPropertiesHelper)


class DividerProperties(LayoutNode):
    class _DividerPropertiesHelper(LayoutNode):
        color: Expression | None = None
        show: Expression | None = None
        style: Expression | None = None
        width: Expression | None = None

    properties: _DividerPropertiesHelper = Field(default_factory=_DividerPropertiesHelper)


class DropShadowProperties(LayoutNode):
    class _DropShadowPropertiesHelper(LayoutNode):
        angle: Expression | None = None
        color: Expression | None = None
        position: Expression | None = None
        preset: Expression | None = None
        shadowBlur: Expression | None = None
        shadowDistance: Expression | None = None
        shadowSpread: Expression | None = None
        show: Expression | None = None
        transparency: Expression | None = None

    properties: _DropShadowPropertiesHelper = Field(default_factory=_DropShadowPropertiesHelper)


class GeneralProperties(LayoutNode):
    class _GeneralPropertiesHelper(LayoutNode):
        altText: Expression | None = None
        keepLayerOrder: Expression | None = None

    properties: _GeneralPropertiesHelper = Field(default_factory=_GeneralPropertiesHelper)


class LockAspectProperties(LayoutNode):
    class _LockAspectPropertiesHelper(LayoutNode):
        show: Expression | None = None

    properties: _LockAspectPropertiesHelper = Field(default_factory=_LockAspectPropertiesHelper)


class SpacingProperties(LayoutNode):
    class _SpacingPropertiesHelper(LayoutNode):
        customizeSpacing: Expression | None = None
        spaceBelowSubTitle: Expression | None = None
        spaceBelowTitle: Expression | None = None
        spaceBelowTitleArea: Expression | None = None

    properties: _SpacingPropertiesHelper = Field(default_factory=_SpacingPropertiesHelper)


class StylePresetProperties(LayoutNode):
    class _StylePresetPropertiesHelper(LayoutNode):
        name: Expression | None = None

    properties: _StylePresetPropertiesHelper = Field(default_factory=_StylePresetPropertiesHelper)


class SubTitleProperties(LayoutNode):
    class _SubTitlePropertiesHelper(LayoutNode):
        alignment: Expression | None = None
        bold: Expression | None = None
        fontColor: Expression | None = None
        fontFamily: Expression | None = None
        heading: Expression | None = None
        show: Expression | None = None
        text: Expression | None = None
        titleWrap: Expression | None = None

    properties: _SubTitlePropertiesHelper = Field(default_factory=_SubTitlePropertiesHelper)


class TitleProperties(LayoutNode):
    class _TitlePropertiesHelper(LayoutNode):
        alignment: Expression | None = None
        background: Expression | None = None
        fontColor: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        heading: Expression | None = None
        show: Expression | None = None
        text: Expression | None = None
        titleWrap: Expression | None = None
        underline: Expression | None = None

    properties: _TitlePropertiesHelper = Field(default_factory=_TitlePropertiesHelper)


class VisualHeaderProperties(LayoutNode):
    class _VisualHeaderPropertiesHelper(LayoutNode):
        background: Expression | None = None
        border: Expression | None = None
        foreground: Expression | None = None
        show: Expression | None = None
        showDrillDownExpandButton: Expression | None = None
        showDrillDownLevelButton: Expression | None = None
        showDrillRoleSelector: Expression | None = None
        showDrillToggleButton: Expression | None = None
        showDrillUpButton: Expression | None = None
        showFilterRestatementButton: Expression | None = None
        showFocusModeButton: Expression | None = None
        showOptionsMenu: Expression | None = None
        showPinButton: Expression | None = None
        showSeeDataLayoutToggleButton: Expression | None = None
        showSmartNarrativeButton: Expression | None = None
        showTooltipButton: Expression | None = None
        showVisualErrorButton: Expression | None = None
        showVisualInformationButton: Expression | None = None
        showVisualWarningButton: Expression | None = None
        transparency: Expression | None = None

    properties: _VisualHeaderPropertiesHelper = Field(default_factory=_VisualHeaderPropertiesHelper)


class VisualHeaderTooltipProperties(LayoutNode):
    class _VisualHeaderTooltipPropertiesHelper(LayoutNode):
        background: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        section: Expression | None = None
        text: Expression | None = None
        themedBackground: Expression | None = None
        themedTitleFontColor: Expression | None = None
        titleFontColor: Expression | None = None
        transparency: Expression | None = None
        type: Expression | None = None
        underline: Expression | None = None

    properties: _VisualHeaderTooltipPropertiesHelper = Field(default_factory=_VisualHeaderTooltipPropertiesHelper)


class VisualLinkProperties(LayoutNode):
    class _VisualLinkPropertiesHelper(LayoutNode):
        bookmark: Expression | None = None
        disabledTooltip: Expression | None = None
        drillthroughSection: Expression | None = None
        enabledTooltip: Expression | None = None
        navigationSection: Expression | None = None
        show: Expression | None = None
        tooltip: Expression | None = None
        type: Expression | None = None
        webUrl: Expression | None = None

    properties: _VisualLinkPropertiesHelper = Field(default_factory=_VisualLinkPropertiesHelper)


class VisualTooltipProperties(LayoutNode):
    class _VisualTooltipPropertiesHelper(LayoutNode):
        background: Expression | None = None
        fontFamily: Expression | None = None
        fontSize: Expression | None = None
        section: Expression | None = None
        show: Expression | None = None
        titleFontColor: Expression | None = None
        type: Expression | None = None
        valueFontColor: Expression | None = None

    properties: _VisualTooltipPropertiesHelper = Field(default_factory=_VisualTooltipPropertiesHelper)


class VCProperties(LayoutNode):
    background: list[BackgroundProperties] | None = Field(default_factory=lambda: [BackgroundProperties()])
    border: list[BorderProperties] | None = Field(default_factory=lambda: [BorderProperties()])
    divider: list[DividerProperties] | None = Field(default_factory=lambda: [DividerProperties()])
    dropShadow: list[DropShadowProperties] | None = Field(default_factory=lambda: [DropShadowProperties()])
    general: list[GeneralProperties] | None = Field(default_factory=lambda: [GeneralProperties()])
    lockAspect: list[LockAspectProperties] | None = Field(default_factory=lambda: [LockAspectProperties()])
    spacing: list[SpacingProperties] | None = Field(default_factory=lambda: [SpacingProperties()])
    stylePreset: list[StylePresetProperties] | None = Field(default_factory=lambda: [StylePresetProperties()])
    subTitle: list[SubTitleProperties] | None = Field(default_factory=lambda: [SubTitleProperties()])
    title: list[TitleProperties] | None = Field(default_factory=lambda: [TitleProperties()])
    visualHeader: list[VisualHeaderProperties] | None = Field(default_factory=lambda: [VisualHeaderProperties()])
    visualHeaderTooltip: list[VisualHeaderTooltipProperties] | None = Field(
        default_factory=lambda: [VisualHeaderTooltipProperties()],
    )
    visualLink: list[VisualLinkProperties] | None = Field(default_factory=lambda: [VisualLinkProperties()])
    visualTooltip: list[VisualTooltipProperties] | None = Field(default_factory=lambda: [VisualTooltipProperties()])
