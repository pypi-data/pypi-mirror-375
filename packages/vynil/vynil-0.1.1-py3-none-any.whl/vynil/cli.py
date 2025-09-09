import argparse
import pathlib

import auryn

from .api import render_book, serve_book, extract_fonts
from .formats import Format

ROOT = pathlib.Path(__file__).parent
DEFAULT_PORT = 8000
FORMATS = list(Format.classes)


def cli(argv: list[str] | None = None) -> None:
    """
    The command-line interface for the Vynil book generation tool.

    Arguments:
        argv: The command-line arguments (default is sys.argv).
    """
    parser = argparse.ArgumentParser(description="Vynil book generation tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    render_parser = subparsers.add_parser("render", help="render a book")
    render_parser.add_argument("format", help="rendering format", choices=FORMATS)
    render_parser.add_argument("path", help="book directory")
    render_parser.add_argument("-c", "--chapters", help="chapters to render")
    render_parser.add_argument("-o", "--output", help="output path")

    serve_parser = subparsers.add_parser("serve", help="serve a book")
    serve_parser.add_argument("format", help="rendering format", choices=FORMATS)
    serve_parser.add_argument("path", help="book directory")
    serve_parser.add_argument("-c", "--chapters", help="chapters to serve")
    serve_parser.add_argument("-p", "--port", default=DEFAULT_PORT, help="port to serve on")

    extract_parser = subparsers.add_parser("extract", help="extract static fonts from a variable font")
    extract_parser.add_argument("path", help="variable font path")

    args = parser.parse_args(argv)

    try:
        match args.command:
            case "render":
                render_book(args.format, args.path, args.output, parse_chapters(args.chapters))

            case "serve":
                serve_book(args.format, args.path, args.port, parse_chapters(args.chapters))

            case "extract":
                extract_fonts(args.path)
    except auryn.Error as error:
        print(error.report())


def parse_chapters(chapters: str | None) -> list[int] | None:
    if not chapters:
        return None
    selected: list[int] = []
    for chapter in chapters.split(","):
        chapter = chapter.strip()
        if "-" in chapter:
            start, end = chapter.split("-")
            selected.extend(range(int(start), int(end) + 1))
        else:
            selected.append(int(chapter))
    return selected