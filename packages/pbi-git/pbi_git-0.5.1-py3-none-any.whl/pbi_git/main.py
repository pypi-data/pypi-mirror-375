from typing import TYPE_CHECKING

from .change_classes import DiffReport
from .layout_diffs import layout_diff
from .ssas import ssas_diff

if TYPE_CHECKING:
    from pbi_core.main import LocalReport


def diff(parent: "LocalReport", child: "LocalReport", *, performance_comparison: bool = True) -> DiffReport:
    layout_changes = layout_diff(parent.static_files.layout, child.static_files.layout)
    ssas_changes = ssas_diff(parent.ssas, child.ssas)
    if performance_comparison:
        for section in layout_changes.sections:
            for visual in section.visuals:
                visual.add_performance_comparison(parent.ssas, child.ssas)
    return DiffReport(
        layout_changes=layout_changes,
        ssas_changes=ssas_changes,
    )
