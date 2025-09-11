from typing import TYPE_CHECKING

from pbi_git.change_classes import ChangeType, SectionChange, VisualChange

from .filters import filter_diff
from .gen_svgs import gen_svgs
from .visual import visual_diff

if TYPE_CHECKING:
    from pbi_core.static_files.layout.layout import Section


def get_visual_changes(
    parent_section: "Section",
    child_section: "Section",
) -> list[VisualChange]:
    visual_changes: list[VisualChange] = []

    parent_visuals = {visual.pbi_core_id(): visual for visual in parent_section.visualContainers}
    child_visuals = {visual.pbi_core_id(): visual for visual in child_section.visualContainers}

    visual_changes.extend(
        VisualChange(
            id=visual_id,
            change_type=ChangeType.DELETED,
            parent_entity=parent_visuals[visual_id],
            child_entity=None,
        )
        for visual_id in set(parent_visuals.keys()) - set(child_visuals.keys())
    )
    visual_changes.extend(
        VisualChange(
            id=visual_id,
            change_type=ChangeType.ADDED,
            parent_entity=None,
            child_entity=child_visuals[visual_id],
        )
        for visual_id in set(child_visuals.keys()) - set(parent_visuals.keys())
    )
    for visual_id in set(parent_visuals.keys()) & set(child_visuals.keys()):
        parent_visual = parent_visuals[visual_id]
        child_visual = child_visuals[visual_id]
        visual_object = visual_diff(parent_visual, child_visual)
        if visual_object.change_type != ChangeType.NO_CHANGE:
            visual_changes.append(visual_object)

    return visual_changes


def section_diff(parent: "Section", child: "Section") -> SectionChange:
    field_changes = {}
    for field in ["height", "width", "ordinal", "displayName"]:
        parent_val = getattr(parent, field, None)
        child_val = getattr(child, field, None)
        if parent_val != child_val and not (parent_val is None and child_val is None):
            field_changes[field] = (parent_val, child_val)

    for field in ["visibility"]:
        parent_val = getattr(parent.config, field, None)
        child_val = getattr(child.config, field, None)
        if parent_val != child_val and not (parent_val is None and child_val is None):
            field_changes[f"config.{field}"] = (parent_val, child_val)

    filter_changes = filter_diff(parent.filters, child.filters)  # type: ignore reportArgumentType
    visual_changes = get_visual_changes(parent, child)

    has_changed = visual_changes or filter_changes or field_changes
    change_type = ChangeType.UPDATED if has_changed else ChangeType.NO_CHANGE

    image_paths = {}
    if visual_changes:
        deleted_ids = {x.primary_entity().pbi_core_id() for x in visual_changes if x.change_type == ChangeType.DELETED}
        added_ids = {x.primary_entity().pbi_core_id() for x in visual_changes if x.change_type == ChangeType.ADDED}
        moved_ids = {
            x.primary_entity().pbi_core_id()
            for x in visual_changes
            if x.change_type == ChangeType.UPDATED
            and any(field in x.field_changes for field in ("x", "y", "width", "height"))
        }
        deleted_ids = {x for x in deleted_ids if x is not None}
        added_ids = {x for x in added_ids if x is not None}
        moved_ids = {x for x in moved_ids if x is not None}

        old_image_path = gen_svgs(parent, deleted=deleted_ids)
        new_image_path = gen_svgs(child, added=added_ids, moved=moved_ids)
        image_paths["old"] = old_image_path
        image_paths["new"] = new_image_path

    return SectionChange(
        id=parent.name,
        change_type=change_type,
        parent_entity=parent,
        child_entity=child,
        filters=filter_changes,  # type: ignore reportArgumentType
        visuals=visual_changes,
        field_changes=field_changes,
        image_paths=image_paths,
    )
