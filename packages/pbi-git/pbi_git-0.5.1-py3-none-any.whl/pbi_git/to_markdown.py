from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import jinja2

from .change_classes import ChangeType

if TYPE_CHECKING:
    from _typeshed import StrPath

    from pbi_git.change_classes import DiffReport


SINGLE_TEMPLATES = {
    p.stem: jinja2.Template(p.read_text()) for p in (Path(__file__).parent / "templates" / "single").iterdir()
}
DIR_TEMPLATES = {
    p.stem: jinja2.Template(p.read_text()) for p in (Path(__file__).parent / "templates" / "split").iterdir()
}


def name_formatter(name: str) -> str:
    """Format names for display in markdown."""
    return name.replace("_", " ").title()


def to_markdown(diff_report: "DiffReport") -> str:
    summary = SINGLE_TEMPLATES["summary"].render(diff_report=diff_report)
    tables_without_changes = ", ".join(table for table, changes in diff_report.ssas_changes.items() if not changes)
    tables_with_changes = {table: changes for table, changes in diff_report.ssas_changes.items() if changes}
    ssas = SINGLE_TEMPLATES["ssas"].render(
        ssas_changes=diff_report.ssas_changes,
        tables_with_changes=tables_with_changes,
        tables_without_changes=tables_without_changes,
        name_formatter=name_formatter,
    )
    layout = SINGLE_TEMPLATES["layout"].render(
        layout_changes=diff_report.layout_changes,
        ChangeType=ChangeType,
    )
    return SINGLE_TEMPLATES["main"].render(summary=summary, ssas=ssas, layout=layout)


class _SectionDirectory(TypedDict):
    main: str
    images: dict[str, str]
    visuals: dict["StrPath", str]


class DirectoryDict(TypedDict):
    main: str
    ssas: str
    layout_changes: str
    layout: dict["StrPath", _SectionDirectory]


def to_markdown_dir(diff_report: "DiffReport") -> DirectoryDict:
    summary = DIR_TEMPLATES["summary"].render(diff_report=diff_report)
    tables_without_changes = ", ".join(table for table, changes in diff_report.ssas_changes.items() if not changes)
    tables_with_changes = {table: changes for table, changes in diff_report.ssas_changes.items() if changes}
    ssas = DIR_TEMPLATES["ssas"].render(
        ssas_changes=diff_report.ssas_changes,
        tables_with_changes=tables_with_changes,
        tables_without_changes=tables_without_changes,
        name_formatter=name_formatter,
    )
    layout_changes = DIR_TEMPLATES["layout"].render(
        layout_changes=diff_report.layout_changes,
        ChangeType=ChangeType,
    )

    layout = {}
    for section in diff_report.layout_changes.sections:
        layout[section.path_name()] = {
            "main": DIR_TEMPLATES["section"].render(section=section, ChangeType=ChangeType),
            "visuals": {
                visual.path_name(): DIR_TEMPLATES["visual"].render(visual=visual, ChangeType=ChangeType)
                for visual in section.visuals
                if visual.change_type != ChangeType.NO_CHANGE
            },
            "images": section.image_paths,
        }
    return {"main": summary, "ssas": ssas, "layout_changes": layout_changes, "layout": layout}
