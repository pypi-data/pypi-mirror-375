from __future__ import annotations
import abc
import pathlib

from ..book import Book
from .render import Render

ROOT = pathlib.Path(__file__).parent

type FormatArgument = str | Format


class Format:
    """
    A base class for formats used in book rendering.
    """

    classes: dict[str, type[Format]] = {}

    def __init_subclass__(cls) -> None:
        name = cls.__name__.lower()
        if name in cls.classes:
            raise ValueError(f"format {name} already exists")
        cls.classes[name] = cls
    
    def __str__(self) -> str:
        return self.__class__.__name__.lower()
    
    def __repr__(self) -> str:
        return f"<{self} format>"
    
    @classmethod
    def resolve(cls, format: FormatArgument) -> Format:
        """
        Resolve a format.

        Arguments:
            format: The format to resolve.
                If it's a format object, it's returned as-is; if it's a string, a format object of this name is
                returned.

        Returns:
            The resolved format.
        """
        if isinstance(format, Format):
            return format
        if format not in cls.classes:
            raise ValueError(f"unknown format {format} (available formats are {', '.join(cls.classes)})")
        return cls.classes[format]()

    def match(self, name: str) -> str | None:
        """
        If a name matches this format, return it without format prefixes.

        Arguments:
            name: The name (with format prefixes).

        Returns:
            The name (without format prefixes) if it matches the format, or None otherwise.
        """
        prefixed = False
        matches = False
        while True:
            for name, cls in self.classes.items():
                prefix = f"{name}_"
                if name.startswith(prefix):
                    prefixed = True
                    name = name.removeprefix(prefix)
                    if isinstance(self, cls):
                        matches = True
                    break
            else:
                break
        return name if not prefixed or matches else None
    
    def render(self, book: Book) -> Render:
        """
        Render a book in this format.

        Arguments:
            book: The book to render.

        Returns:
            The rendered book.
        """
        render = Render(self, book)
        render.add_style(ROOT / "common.css")
        render.add_style(ROOT / "syntax-highlighting.css")
        return render
    
    @abc.abstractmethod
    def render_binary(self, render: Render) -> bytes:
        """
        Generate the binary data of a rendered book.

        Arguments:
            render: The rendered book.

        Returns:
            The rendered book binary data.
        """
        raise NotImplementedError()
    
    def render_html(self, render: Render) -> str:
        """
        Generate the HTML of a rendered book (i.e. to serve it as a web page).

        Arguments:
            render: The rendered book.

        Returns:
            The rendered book HTML.
        """
        return self.render_binary(render).decode()
    
    @abc.abstractmethod
    def save(self, render: Render, output: pathlib.Path) -> None:
        """
        Save the rendered book to disk.

        Arguments:
            render: The rendered book.
            output: The output path.
        """
        raise NotImplementedError()