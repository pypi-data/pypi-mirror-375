import re
from typing import Callable, Match, Pattern

import latex2mathml.converter

inline_styles: list[tuple[int, Pattern, bool, Callable[[Match], str]]] = []


def inline_style(
    pattern: str,
    priority: int = 0,
    final: bool = False,
) -> Callable[[Callable[[Match], str]], Callable[[Match], str]]:
    def decorator(style: Callable[[Match], str]) -> Callable[[Match], str]:
        inline_styles.append((priority, re.compile(pattern), final, style))
        return style

    return decorator


@inline_style(r"`(.+?)`", priority=2, final=True)
def code(match: Match) -> str:
    code = match.group(1).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<code>{code}</code>"


@inline_style(r"\$(.+?)\$", priority=1, final=True)
def math(match: Match) -> str:
    return latex2mathml.converter.convert(match.group(1))


@inline_style(r"\*\*(.+?)\*\*")
def bold(match: Match) -> str:
    return f"<strong>{match.group(1)}</strong>"


@inline_style(r"\*(.+?)\*")
def italic(match: Match) -> str:
    return f"<em>{match.group(1)}</em>"


@inline_style(r"__(.+?)__")
def underline(match: Match) -> str:
    return f"<u>{match.group(1)}</u>"


@inline_style(r"--(.+?)--")
def strikethrough(match: Match) -> str:
    return f"<s>{match.group(1)}</s>"


@inline_style(r"\[(.+?)\]\((.+?)\)")
def link(match: Match) -> str:
    text, url = match.groups()
    if url.startswith("#") and not url.startswith("#chapter-"):
        url = f"#{{render.current_chapter.id}}-{url[1:]}"
    elif not url.startswith("http"):
        url = f"https://{url}"
    return f'<a href="{url}">{text}</a>'
