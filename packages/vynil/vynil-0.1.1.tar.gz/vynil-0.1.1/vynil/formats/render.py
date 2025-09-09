from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Any, ClassVar

from auryn import GX, TemplateArgument, execute

from ..assets import Asset, Font, Image, Script, Style
from ..book import Book, Chapter, Section
from ..components import Component
from .server import Server

if TYPE_CHECKING:
    from .format import Format

ROOT = pathlib.Path(__file__).parent
FONTFACE = """
@font-face {{
    font-family: '{font.family}';
    src: url('../{font.url}') format('{font.font_type}');
    font-weight: {font.weight};
    font-style: {font.style};
}}
"""


class Render:
    """
    An ongoing rendering of a book.

    Attributes:
        book: The book being rendered.
        current_chapter: The current chapter being rendered.
        current_section: The current section being rendered.
        styles: The styles to be included in the book (by URL).
        scripts: The scripts to be included in the book (by URL).
        images: The images to be included in the book (by URL).
        fonts: The fonts to be included in the book (by URL).
        files: All other files to be included in the book (by URL).
    """

    # Conventions:
    fonts_styles_filename: ClassVar[str] = "fonts.css"
    module_on_load_name: ClassVar[str] = "on_load"
    module_render_name: ClassVar[str] = "render"

    def __init__(self, format: Format, book: Book) -> None:
        self.format = format
        self.book = book
        self.current_chapter: Chapter | None = None
        self.current_section: Section | None = None
        self.styles: dict[str, Style] = {}
        self.scripts: dict[str, Script] = {}
        self.images: dict[str, Image] = {}
        self.fonts: dict[str, Font] = {}
        self.files: dict[str, Asset] = {}
        self._available_images: dict[str, Image] = {}
        # A placeholder for the CSS that defines the included fonts.
        self._fonts_style = Style(
            name=self.fonts_styles_filename,
            mimetype="text/css",
            data=b"",
        )
        self.styles[self._fonts_style.url] = self._fonts_style
        self.components: dict[str, Any] = {}
    
    def __str__(self) -> str:
        return f"{self.format} render of {self.book}"
    
    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def fetch(cls, gx: GX) -> Render:
        """
        Fetch the render in use by the generation/execution.

        Arguments:
            gx: The generation/execution using the render.

        Returns:
            The renderer.
        """
        return gx.g_locals["render"]

    @property
    def assets(self) -> dict[str, Asset]:
        """
        All the assets (images, styles, scripts, fonts and files) that are included in the book (by URL).
        """
        return {
            **self.images,
            **self.styles,
            **self.scripts,
            **self.fonts,
            **self.files,
        }
    
    def execute(
        self,
        template: TemplateArgument,
        context: dict[str, Any] | None = None,
        /,
        **context_kwargs: Any,
    ) -> bytes:
        """
        Render the book according to a template.

        Arguments:
            template: The template to use to render the book.
            context: Additional context for the generation/execution.
            **context_kwargs: Additional context for the generation/execution.

        Returns:
            The rendered data.
        """
        for asset in self.book.assets.values():
            # Include any asset that doesn't have format constraints, or whose format constraints are met.
            name = self.format.match(asset.name)
            if not name:
                continue
            match asset:
                case Font():
                    self.fonts[asset.url] = asset
                case Image():
                    self.images[asset.url] = asset
                    self._available_images[asset.name] = asset
                case Style():
                    self.styles[asset.url] = asset
                case Script():
                    self.scripts[asset.url] = asset
                case _:
                    self.files[asset.url] = asset
        for component in Component.builtins():
            self.components.update(component.load(self))
        for component in self.book.components:
            self.components.update(component.load(self))
        data = execute(
            template,
            context,
            load=[
                "vynil",
                self.components,
            ],
            render=self,
            book=self.book,
            g_render=self,
            g_book=self.book,
            **context_kwargs,
        )
        fonts_css = []
        for font in self.fonts.values():
            fonts_css.append(FONTFACE.format(font=font))
        self._fonts_style.data = "\n".join(fonts_css).strip().encode()
        return data.encode()
    
    def to_binary(self) -> bytes:
        """
        Render into binary data.

        Returns:
            The rendered binary data.
        """
        return self.format.render_binary(self)
    
    def to_html(self) -> str:
        """
        Render into HTML (i.e. to serve it as a web page).

        Returns:
            The rendered HTML.
        """
        return self.format.render_html(self)
    
    def save(self, path: str | pathlib.Path) -> None:
        """
        Save the rendered book to a given path.

        Arguments:
            path: The path to save the rendered book to.
        """
        self.format.save(self, path)

    def serve(self, port: int) -> None:
        """
        Serve the rendered book on a given port.

        Arguments:
            port: The port to serve the rendered book on.
            render: The rendered book.
        """
        server = Server(port, self)
        server.serve()
    
    def clear(self) -> None:
        """
        Clear configurations accumulated during execution (so another execution can start from scratch).
        """
        self.current_chapter = None
        self.current_section = None
        self.images.clear()
        for chapter in self.book.chapters.values():
            chapter.sections.clear()

    def reload(self) -> Render:
        """
        Reload the render.

        Returns:
            The reloaded render.
        """
        if not self.book.path:
            raise ValueError(f"cannot reload {self}: book was not read from disk")
        book = Book.resolve(self.book.path)
        return self.format.render(book)

    def set_chapter(self, number: int) -> Chapter:
        """
        Set the current chapter.

        Arguments:
            number: The chapter number.
        
        Returns:
            The chapter.
        """
        if number not in self.book.chapters:
            available = ", ".join(str(chapter) for chapter in self.book.chapters.values())
            raise ValueError(f"chapter {number} not found (available chapters are {available})")
        self.current_chapter = self.book.chapters[number]
        return self.current_chapter

    def add_section(self, title: str) -> Section:
        """
        Add a section to the current chapter.

        Arguments:
            title: The title of the section.

        Returns:
            The added section.
        """
        if not self.current_chapter:
            raise ValueError(f"cannot add section {title!r} when no chapter is set")
        self.current_section = self.current_chapter.add_section(title)
        return self.current_section

    def add_image(self, name: str) -> str:
        """
        Include an image in the book.

        Arguments:
            name: The image name.

        Returns:
            The image URL.
        """
        if name not in self.images:
            available = ", ".join(self.images)
            raise ValueError(f"image {name!r} does not exist (available images are {available})")
        return self._available_images[name].url

    def add_style(self, path_or_name: str | pathlib.Path, css: str | None = None) -> str:
        """
        Add a stylesheet to the book.

        If the path exists, the stylesheet is read as a file; otherwise, it is considered dynamic and its content should
        be provided explicitly.

        Arguments:
            path_or_name: The stylesheet path or name (if it's dynamic).
            css: The stylesheet content (if it's dynamic).

        Returns:
            The style URL.
        """
        path = pathlib.Path(path_or_name)
        if path.exists():
            name = path.name
            css = path.read_text()
        elif css:
            name = str(path_or_name)
            path = None
        else:
            raise ValueError(f"stylesheet {path!r} does not exist and no content was provided")
        style = Style(
            name=name,
            mimetype="text/css",
            data=css.encode(),
            path=path,
        )
        if style.url in self.styles:
            raise ValueError(f"style {style.url!r} already exists")
        self.styles[style.url] = style
        return style.url

    def add_script(self, path_or_name: str | pathlib.Path, js: str | None = None) -> str:
        """
        Add a script to the book.

        If the path exists, the script is read as a file; otherwise, it is considered dynamic and its content should
        be provided explicitly.

        Arguments:
            path_or_name: The script path or name (if it's dynamic).
            js: The script content (if it's dynamic).

        Returns:
            The script URL.
        """
        path = pathlib.Path(path_or_name)
        if path.exists():
            name = path.name
            js = path.read_text()
        elif js:
            name = str(path_or_name)
            path = None
        else:
            raise ValueError(f"script {path!r} does not exist and no content was provided")
        script = Script(
            name=name,
            mimetype="text/javascript",
            data=js.encode(),
            path=path,
        )
        if script.url in self.scripts:
            raise ValueError(f"script {script.url!r} already exists")
        self.scripts[script.url] = script
        return script.url

