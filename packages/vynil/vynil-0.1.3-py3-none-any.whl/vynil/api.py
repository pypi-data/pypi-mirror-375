import pathlib

from .book import Book, BookArgument
from .assets import AssetArgument, Font
from .formats import Format, FormatArgument


def render_book(
    format: FormatArgument,
    book: str | pathlib.Path,
    output: str | pathlib.Path | None = None,
    chapters: list[int] | None = None,
) -> None:
    """
    Render a book.

    Arguments:
        format: The format to render the book in.
        path: The book directory.
        output: The output path.
    """
    format = Format.resolve(format)
    book_ = Book.resolve(book)
    if chapters:
        book_.chapters = {num: chapter for num, chapter in book_.chapters.items() if num in chapters}
    if output:
        output = pathlib.Path(output)
    else:
        output = book_.path / "output"
    render = format.render(book_)
    render.save(output)


def serve_book(
    format: FormatArgument,
    book: BookArgument,
    port: int,
    chapters: list[int] | None = None,
) -> None:
    """
    Serve a book.

    Arguments:
        format: The format to render the book in.
        book: The book to serve.
        port: The port to serve the book on.
    """
    format = Format.resolve(format)
    book_ = Book.resolve(book)
    if chapters:
        book_.chapters = {num: chapter for num, chapter in book_.chapters.items() if num in chapters}
    render = format.render(book_)
    render.serve(port)


def extract_fonts(path: str | pathlib.Path) -> None:
    """
    Extract static fonts from a variable font.

    Arguments:
        path: The path to the variable font.
    """
    path = pathlib.Path(path)
    fonts = Font.extract_fonts(path)
    if not fonts:
        print(f"font {path} is not a variable font")
        return
    for font in fonts:
        (path.parent / font.name).write_bytes(font.data)
        print(f"extracted {font.name}")
    print("done")