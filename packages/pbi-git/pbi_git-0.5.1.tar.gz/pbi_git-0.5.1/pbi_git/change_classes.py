import contextlib
import datetime
import textwrap
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

import jinja2
from pbi_core.static_files.layout.performance import NoQueryError

from .utils import get_git_name

if TYPE_CHECKING:
    from _typeshed import StrPath
    from pbi_core.ssas.server import BaseTabularModel
    from pbi_core.static_files.layout.layout import Section
    from pbi_core.static_files.layout.performance import Performance
    from pbi_core.static_files.layout.visual_container import VisualContainer


def name_formatter(name: str) -> str:
    """Format names for display in markdown."""
    return name.replace("_", " ").title()


FIELD_CHANGES_TABLE = jinja2.Template("""
| Field | From | To |
| ----- | ---- | -- |
{% for field, (from_val, to_val) in changes.items() -%}
| {{name_formatter(field)}} | <code>{{ from_val or "*No Value*" }}</code> | <code>{{ to_val or "*No Value*" }}</code> |
{% endfor %}
""")


def get_field_changes_table(changes: dict[str, tuple[Any, Any]]) -> str:
    parsed_data = {k: (get_git_name(a), get_git_name(b)) for k, (a, b) in changes.items()}
    return FIELD_CHANGES_TABLE.render(
        changes=parsed_data,
        name_formatter=name_formatter,
    )


class ChangeType(Enum):
    ADDED = "ADDED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    NO_CHANGE = "NO_CHANGE"  # used when only changes in children are present


@dataclass
class Change:
    id: str
    change_type: ChangeType
    parent_entity: Any  # The entity itself, e.g., a table or measure object in the elder report
    child_entity: Any  # The entity itself, e.g., a table or measure object in the younger report
    field_changes: dict[str, tuple[Any, Any]] = field(default_factory=dict)  # field name to [old_value, new_value]


@dataclass
class FilterChange(Change):
    def to_markdown(self) -> str:
        if self.change_type == ChangeType.NO_CHANGE:
            return ""
        if self.change_type in {ChangeType.ADDED, ChangeType.DELETED}:
            return f"""
Filter: {self.primary_entity().get_display_name()}

**Filter {self.change_type.value.title()}**
"""

        filter_change_table = get_field_changes_table(self.field_changes)
        return f"""

Filter: {self.primary_entity().get_display_name()}

{filter_change_table}
"""

    def primary_entity(self) -> Any:
        return self.parent_entity or self.child_entity


@dataclass
class VisualChange(Change):
    parent_entity: "VisualContainer | None"
    child_entity: "VisualContainer | None"
    filters: list[FilterChange] = field(default_factory=list)
    data_changes: dict[str, Any] = field(default_factory=dict)
    performance_comparison: dict[str, "Performance"] = field(default_factory=dict)

    def _generate_performance_section(self) -> str:
        if not self.performance_comparison:
            return ""

        ret = ""
        if self.performance_comparison.get("parent") is None:
            child_duration = round(self.performance_comparison["child"].total_duration / 1000, 2)
            ret += f"Render Time: N/A -> {child_duration}s"
        elif self.performance_comparison.get("child") is None:
            parent_duration = round(self.performance_comparison["parent"].total_duration / 1000, 2)
            ret += f"Render Time: {parent_duration}s -> N/A"
        else:
            child_duration = round(self.performance_comparison["child"].total_duration / 1000, 2)
            parent_duration = round(self.performance_comparison["parent"].total_duration / 1000, 2)

            change = round((child_duration - parent_duration) / max(parent_duration, 0.01) * 100, 2)

            color = "grey"
            if change < 0:
                color = "green"
            elif change > 0:
                color = "red"

            change_text = f"<span style='color: {color}'>{change}%</span>"

            ret += f"Render Time: {parent_duration}s -> {child_duration}s ({change_text})\n"
        return ret

    def to_markdown(self) -> str:
        """Convert the visual change to a markdown string."""
        if self.change_type == ChangeType.NO_CHANGE:
            return ""
        if self.change_type in {ChangeType.ADDED, ChangeType.DELETED}:
            return f"**Visual {self.change_type.value.title()}**\n{self._generate_performance_section()}"

        ret = f"{self._generate_performance_section()}\n"
        if self.field_changes:
            ret += get_field_changes_table(self.field_changes)

        if self.filters:
            filter_section = "#### *Updated Filters*\n"

            for f in self.filters:
                filter_section += f.to_markdown()
            ret += textwrap.indent(filter_section, "> ", predicate=lambda _line: True)
            ret += "\n"
        if self.data_changes:
            data_section = "#### *Updated Data Queries*\n"
            data_section += "| Section | Source | Action |\n"
            data_section += "| ------- | ------ | ------ |\n"
            for field, changes in self.data_changes.items():
                for change_type in ["added", "removed"]:
                    for item in changes.get(change_type, []):
                        data_section += f"| {field} | {item} | {change_type.title()} |\n"
            ret += textwrap.indent(data_section, "> ", predicate=lambda _line: True)
        return ret

    def primary_entity(self) -> "VisualContainer":
        ret = self.parent_entity or self.child_entity
        assert ret is not None
        return ret

    def change_count(self) -> int:
        return len(self.field_changes) + len(self.filters) + len(self.data_changes)

    def display_name(self) -> str:
        return self.primary_entity().pbi_core_name()

    def path_name(self) -> str:
        base = f"{self.display_name()}_{self.primary_entity().pbi_core_id()}"
        return base.lower().replace(" ", "_").replace(".", "_")

    def add_performance_comparison(self, parent_ssas: "BaseTabularModel", child_ssas: "BaseTabularModel") -> None:
        if self.parent_entity:
            with contextlib.suppress(NoQueryError):
                self.performance_comparison["parent"] = self.parent_entity.get_performance(parent_ssas)
        if self.child_entity:
            with contextlib.suppress(NoQueryError):
                self.performance_comparison["child"] = self.child_entity.get_performance(child_ssas)


@dataclass
class SectionChange(Change):
    parent_entity: "Section | None"
    child_entity: "Section | None"
    filters: list[FilterChange] = field(default_factory=list)
    visuals: list[VisualChange] = field(default_factory=list)
    image_paths: dict[str, str] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Convert the section change to a markdown string."""
        if self.change_type == ChangeType.NO_CHANGE:
            return ""
        if self.change_type in {ChangeType.ADDED, ChangeType.DELETED}:
            return f"**Section {self.change_type.value.title()}**"

        ret = ""
        if self.image_paths:
            ret += """| Before | After |
| ------ | ----- |
| <img src="old.svg" width="100%"> | <img src="new.svg" width="100%"> |
"""
        if self.field_changes:
            ret += get_field_changes_table(self.field_changes)

        if self.filters:
            filter_section = "### *Updated Filters*\n"

            for f in self.filters:
                filter_section += f.to_markdown()
            ret += textwrap.indent(filter_section, "> ", predicate=lambda _line: True)

        return ret

    def change_count(self) -> int:
        return len(self.field_changes) + len(self.filters) + sum(v.change_count() for v in self.visuals)

    def primary_entity(self) -> "Section":
        ret = self.parent_entity or self.child_entity
        assert ret is not None
        return ret

    def display_name(self) -> str:
        return self.primary_entity().displayName

    def path_name(self) -> str:
        base = f"{self.display_name()}_{self.primary_entity().name}"
        return base.lower().replace(" ", "_").replace(".", "_")


@dataclass
class LayoutChange(Change):
    filters: list[FilterChange] = field(default_factory=list)
    sections: list[SectionChange] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Convert the layout change to a markdown string."""
        if self.change_type == ChangeType.NO_CHANGE:
            return "No changes in report layout."

        ret = ""

        if self.filters:
            filter_section = "## *Updated Filters*\n"

            for f in self.filters:
                filter_section += f.to_markdown()
            ret += textwrap.indent(filter_section, "> ", predicate=lambda _line: True)

        return ret


@dataclass
class SsasChange(Change):
    entity_type: str = "--undefined--"  # e.g., "table", "measure", "column"


@dataclass
class DiffReport:
    layout_changes: LayoutChange
    ssas_changes: dict[str, list[SsasChange]]

    def to_markdown(self) -> str:
        """Convert the diff report to a markdown string."""
        from .to_markdown import to_markdown  # noqa: PLC0415

        return to_markdown(self)

    def to_dir(self, path: "StrPath") -> None:
        from .to_markdown import to_markdown_dir  # noqa: PLC0415

        data = to_markdown_dir(self)
        now = datetime.datetime.now(tz=datetime.UTC).strftime("%Y_%m_%d %H_%M_%S")
        root = Path(path) / now
        root.mkdir(parents=True, exist_ok=True)
        (root / "main.md").write_text(data["main"])
        (root / "ssas.md").write_text(data["ssas"])
        (root / "layout.md").write_text(data["layout_changes"])
        for s_name, s_data in data["layout"].items():
            s_dir = root / s_name
            s_dir.mkdir(parents=True, exist_ok=True)
            (s_dir / "visuals").mkdir(parents=True, exist_ok=True)
            (s_dir / "main.md").write_text(s_data["main"])
            if s_data["images"]:
                for img_name, img_data in s_data["images"].items():
                    (s_dir / f"{img_name}.svg").write_text(img_data)
            for v_name, v_data in s_data["visuals"].items():
                (s_dir / "visuals" / f"{v_name}.md").write_text(v_data)

    def to_pdf(self, file_path: str) -> None:
        def add_ids(line: str) -> str:
            if not line.lstrip().startswith("#"):
                return line

            # we're relying on the fact that the string in lstrip is actually a set
            title = line.lstrip(" #")
            title_id = title.lower().replace(" ", "-")
            heading_prefix = line[0 : line.index(title)]
            return f"{heading_prefix} <a id='{title_id}'></a>{title}"

        """Summary here

        Note:
            markdown_pdf doesn't handle temporary files well, that's why we save directly to a file path.

        """
        from markdown_pdf import MarkdownPdf, Section  # noqa: PLC0415

        # mode gfm-like requires linkify-it-py
        css = (Path(__file__).parent / "templates" / "github-dark.css").read_text()

        markdown_content = self.to_markdown()
        markdown_content = "\n".join(add_ids(x) for x in markdown_content.splitlines())
        pdf = MarkdownPdf(mode="gfm-like")
        pdf.add_section(Section(markdown_content), user_css=css)
        pdf.save(file_path)

    def layout_updates(self) -> int:
        """Count the number of layout updates."""
        return len(self.layout_changes.field_changes) + len(self.layout_changes.filters)

    def section_updates(self) -> int:
        """Count the number of section updates."""
        return sum(section.change_count() for section in self.layout_changes.sections)

    def visual_updates(self) -> int:
        """Count the number of visual updates."""
        return sum(
            len(visual.field_changes) + len(visual.filters)
            for section in self.layout_changes.sections
            for visual in section.visuals
        )
