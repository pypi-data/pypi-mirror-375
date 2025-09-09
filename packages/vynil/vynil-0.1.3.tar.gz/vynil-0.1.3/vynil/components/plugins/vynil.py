from typing import Any

from auryn import GX, Lines
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from vynil import Component, Render
import yaml


def g_content(gx: GX) -> None:
    if Component.CONTENT not in gx.state:
        raise ValueError("no content (this macro can only be used inside a component)")
    content: Lines = gx.state[Component.CONTENT]
    gx.transform(content.snap(gx.line.indent))


def x_get(gx: GX, index: int) -> Any:
    globals_: list[Any] = gx.state[Component.GLOBALS]
    result = globals_[index]
    return result


def x_restore_globals(gx: GX, globals_before: dict[str, Any], globals_after: dict[str, Any]) -> None:
    globals_after.clear()
    globals_after.update(globals_before)


def g_yaml(gx: GX) -> None:
    globals_: list[Any] = gx.state.setdefault(Component.GLOBALS, [])
    globals_.append(yaml.safe_load(gx.line.children.snap(0).to_string()))
    gx.add_code(f"globals().update(get({len(globals_) - 1}))")


def g_title(gx: GX, title: str) -> None:
    gx.add_code(f"title({gx.line.indent}, {title!r})")


def x_title(gx: GX, indent: int, title: str) -> None:
    render = Render.fetch(gx)
    if not render.current_chapter:
        raise ValueError("no chapter set (call render.set_chapter() first)")
    render.current_chapter.title = title
    gx.emit(indent, f"<h1 id={render.current_chapter.id!r}>{title}</h1>")


def g_section(gx: GX, title: str) -> None:
    gx.add_code(f"section({gx.line.indent}, {title!r})")


def x_section(gx: GX, indent: int, title: str) -> None:
    render = Render.fetch(gx)
    section = render.add_section(title)
    gx.emit(indent, f"<h2 id={section.id!r}>{title}</h2>")


def g_code(gx: GX, language: str | None = None) -> None:
    render = Render.fetch(gx)
    if language is None:
        language = render.book.default_code_language
    code = gx.line.children.snap(0).to_string().rstrip()
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter()
    html = highlight(code, lexer, formatter)
    first_line, *lines = html.splitlines()
    gx.add_text(gx.line.indent, first_line, interpolate=False)
    for line in lines:
        gx.add_text(0, line, interpolate=False)
