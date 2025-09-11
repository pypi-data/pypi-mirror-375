from pbi_core.logging import get_logger
from pbi_core.report.local.main import LocalReport
from pbi_core.ssas.model_tables.enums.enums import DataType
from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel

from .get_static_elements import get_static_elements
from .text_elements import TextElement, TextElements

logger = get_logger()


def get_ssas_elements(server: BaseTabularModel) -> TextElements:
    text_elements = []
    for m in server.measures:
        text_elements.append(
            TextElement(
                category="Measure",
                source="ssas",
                xpath=["measures", m.id],
                field="name",
                text=m.name,
            ),
        )
        if m.data_type == DataType.STRING and isinstance(m.expression, str):
            text_elements.append(
                TextElement(
                    category="Measure",
                    source="ssas",
                    xpath=["measures", m.id],
                    field="expression",
                    text=m.expression,
                ),
            )
        if isinstance(m.format_string, str):
            text_elements.append(
                TextElement(
                    category="Measure",
                    source="ssas",
                    xpath=["measures", m.id],
                    field="format_string",
                    text=m.format_string,
                ),
            )
        if isinstance(m.description, str):
            text_elements.append(
                TextElement(
                    category="Measure",
                    source="ssas",
                    xpath=["measures", m.id],
                    field="description",
                    text=m.description,
                ),
            )
    for c in server.columns:
        if isinstance(c.explicit_name, str):
            text_elements.append(
                TextElement(
                    category="Column",
                    source="ssas",
                    xpath=["columns", c.id],
                    field="explicit_name",
                    text=c.explicit_name,
                ),
            )
        if isinstance(c.description, str):
            text_elements.append(
                TextElement(
                    category="Column",
                    source="ssas",
                    xpath=["columns", c.id],
                    field="description",
                    text=c.description,
                ),
            )
    return TextElements(text_elements=text_elements)


def get_source_text_elements(report: LocalReport) -> TextElements:
    static_elements = get_static_elements(report.static_files.layout)
    ssas_elements = get_ssas_elements(report.ssas)
    return TextElements(text_elements=static_elements.text_elements + ssas_elements.text_elements)
