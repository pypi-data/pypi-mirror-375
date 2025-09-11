from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET  # noqa: S405

import svgwrite
import svgwrite.shapes

if TYPE_CHECKING:
    from pbi_core.static_files.layout.section import Section
from pathlib import Path

SVGS: dict[str, str] = {f.stem: f.read_text() for f in (Path(__file__).parents[1] / "svgs").glob("*.svg")}
VISUAL_MAPPER = {
    "textbox": "text_box",
    "card": "card",
    "map": "map",
    "clusteredColumnChart": "bar",
    "pieChart": "pie",
    "scatterChart": "scatter",
}


class Raw:
    elementname: str = "rect"  # needed to pass validation

    def __init__(self, text: str, width: float, height: float) -> None:
        self.text = text
        self.width = width
        self.height = height

    def get_xml(self) -> ET.Element:
        ret = ET.fromstring(self.text)  # noqa: S314
        ret.set("width", str(self.width))
        ret.set("height", str(self.height))
        ret.set("preserveAspectRatio", "none")
        return ret


def conv_name(x: str) -> str:
    return x.lower().replace(" ", "_")


def gen_svgs(
    section: "Section",
    added: set[str] | None = None,
    deleted: set[str] | None = None,
    moved: set[str] | None = None,
) -> str:
    assert section._layout is not None
    added = added or set()
    deleted = deleted or set()
    moved = moved or set()

    svg_path = (Path(__file__).parent / "test.svg").absolute()
    drawing = svgwrite.Drawing(
        svg_path.absolute().as_posix().replace("\\", "/"),
        profile="tiny",
        viewBox=f"0 0 {section.width} {section.height}",
    )

    for visual in section.visualContainers:
        viz_map_key = None
        if visual.config.singleVisual is not None:
            viz_map_key = visual.config.singleVisual.visualType

        g = drawing.g()
        g.translate(visual.x, visual.y)
        if viz_map_key in VISUAL_MAPPER:
            g.add(Raw(SVGS[VISUAL_MAPPER[viz_map_key]], visual.width, visual.height))
        else:
            g.add(
                svgwrite.shapes.Rect(
                    size=(visual.width, visual.height),
                    fill="red",
                    stroke="black",
                    stroke_width=1,
                ),
            )

        if visual.pbi_core_id() in added:
            g.add(Raw(SVGS["_added"], visual.width, visual.height))
        if visual.pbi_core_id() in deleted:
            g.add(Raw(SVGS["_deleted"], visual.width, visual.height))
        if visual.pbi_core_id() in moved:
            g.add(Raw(SVGS["_moved"], visual.width, visual.height))
        drawing.add(g)

    drawing.save()

    data = svg_path.read_text(encoding="utf-8")
    svg_path.unlink()
    return data
