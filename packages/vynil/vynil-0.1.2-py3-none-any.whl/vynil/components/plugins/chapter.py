import re
from typing import Callable, Match

from auryn import GX
from vynil import inline_styles

CHAPTER = "chapter"
OPEN_PARAGRAPH = "open_paragraph"
YANK = re.compile(r"YANKED_(\d+)")


def on_load(gx: GX) -> None:
    transform_code = gx.line_transforms.pop(gx.code_prefix)
    transform_text = gx.line_transforms.pop("")
    gx.line_transform(transform_markdown)
    gx.on_complete(on_end(transform_code, transform_text))


def on_end(
    transform_code: Callable[[GX, str], None],
    transform_text: Callable[[GX, str], None],
) -> Callable[[GX], None]:
    def on_end(gx: GX) -> None:
        close_paragraph(gx)
        gx.line_transforms[gx.code_prefix] = transform_code
        gx.line_transforms[""] = transform_text

    return on_end


def transform_markdown(gx: GX, content: str) -> None:
    if not content:
        close_paragraph(gx)
        return
    elif content.startswith("<"):
        close_paragraph(gx)
        gx.add_text(gx.line.indent, content, interpolate=False)
        gx.transform()
        return
    else:
        open_paragraph(gx)
        yanked: list[str] = []
        for _, pattern, final, style in sorted(inline_styles, key=lambda style: -style[0]):
            if final:
                content = pattern.sub(yank(style, yanked), content)
            content = pattern.sub(style, content)
        if yanked:
            content = YANK.sub(put_back(yanked), content)
        indent = gx.line.indent + 4
        gx.add_text(indent, content, interpolate=False)
        gx.transform(gx.line.children.snap(indent))


def open_paragraph(gx: GX) -> None:
    indent = gx.state.get(OPEN_PARAGRAPH, None)
    if not indent:
        gx.add_text(gx.line.indent, "<p>")
        gx.state[OPEN_PARAGRAPH] = gx.line.indent


def close_paragraph(gx: GX) -> None:
    indent = gx.state.get(OPEN_PARAGRAPH, None)
    if indent:
        gx.add_text(indent, "</p>")
        gx.state[OPEN_PARAGRAPH] = None


def yank(style: Callable[[Match], str], yanked: list[str]) -> Callable[[Match], str]:
    def yank(match: Match) -> str:
        yanked.append(style(match))
        return f"YANKED_{len(yanked) - 1}"

    return yank


def put_back(yanked: list[str]) -> Callable[[Match], str]:
    def put_back(match: Match) -> str:
        return yanked[int(match.group(1))]

    return put_back
