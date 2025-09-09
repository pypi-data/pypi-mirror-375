from __future__ import annotations

import pathlib
import re
from typing import Any, ClassVar, Iterable, Pattern

import yaml

from .assets import Asset
from .components import Component

INVALID_CHARS = re.compile(r"[^a-z0-9 ]+")

type BookArgument = str | pathlib.Path | dict[str, Any] | Book


class Book:
    """
    A book to be rendered.

    Attributes:
        title: The book title.
        authors: The book authors.
        identifier: The book identifier.
        language_code: The book language code.
        default_code_language: The default code language.
        path: The book path.
        chapters: The book chapters.
        assets: The book assets.
        components: The book components.
    """

    # Conventions:
    metadata_filename: ClassVar[str] = "book.yaml"
    chapters_directory_name: ClassVar[str] = "chapters"
    assets_directory_name: ClassVar[str] = "assets"
    components_directory_name: ClassVar[str] = "components"

    def __init__(
        self,
        title: str,
        authors: list[str],
        identifier: str | None = None,
        language_code: str = "en",
        default_code_language: str = "python",
        path: pathlib.Path | None = None,
    ) -> None:
        self.title = title
        self.authors = authors
        self.identifier = identifier
        self.language_code = language_code
        self.default_code_language = default_code_language
        self.path = path
        self.chapters: dict[int, Chapter] = {}
        self.assets: dict[tuple[str, str], Asset] = {}
        self.components: list[Component] = []

    def __str__(self) -> str:
        return f"book {self.title!r}"

    def __repr__(self) -> str:
        return f"<{self}>"
    
    @classmethod
    def resolve(cls, book: BookArgument) -> Book:
        """
        Resolve a book.

        Arguments:
            book: The book to resolve.
                If it's a book object, it's returned as-is; if it's a string or path object, it's loaded from that
                directory; if it's a dictionary, it's converted to a book object.

        Returns:
            The resolved book.
        """
        if isinstance(book, Book):
            return book
        if isinstance(book, dict):
            book = cls(**book)
            for chapter in book.get("chapters", []):
                book.add_chapter(chapter)
            for asset in book.get("assets", []):
                book.add_asset(asset)
            for component in book.get("components", []):
                book.add_component(component)
            return book
        directory = pathlib.Path(book)
        metadata_path = directory / cls.metadata_filename
        metadata = yaml.safe_load(metadata_path.read_text())
        book = Book(**metadata, path=directory)
        for path in cls._collect(directory / cls.chapters_directory_name, "*.vyn"):
            book.add_chapter(path)
        for path in cls._collect(directory / cls.assets_directory_name, "*"):
            book.add_asset(path)
        for path in cls._collect(directory / cls.components_directory_name, "*"):
            book.add_component(path)
        return book

    @classmethod
    def _collect(cls, directory: pathlib.Path, pattern: str) -> Iterable[pathlib.Path]:
        directory = pathlib.Path(directory)
        for path in sorted(directory.rglob(pattern)):
            if path.is_dir():
                continue
            yield path
    
    @property
    def cover(self) -> str:
        for (_, name), asset in self.assets.items():
            if name.split(".")[0] == "cover":
                return asset.url
        return ""
    
    def add_chapter(self, chapter: str | pathlib.Path | dict[str, Any] | Chapter) -> Chapter:
        """
        Add a chapter to the book.

        Arguments:
            chapter: The chapter to add.
                If it's a chapter object, it's used as-is; if It's a string or path object, it's loaded from that file;
                if it's a dictionary, it's converted to a chapter object.
        
        Returns:
            The added chapter.
        """
        chapter = Chapter.resolve(chapter)
        if chapter.number in self.chapters:
            raise ValueError(f"cannot add {chapter}: {self.chapters[chapter.number]} is already part of the book")
        self.chapters[chapter.number] = chapter
        return chapter

    def add_asset(self, asset: str | pathlib.Path | dict[str, Any] | Asset) -> Asset:
        """
        Add an asset to the book.
        
        Arguments:
            asset: The asset to add.
                If it's an asset object, it's used as-is; if it's a string or path object, it's loaded from that file;
                if it's a dictionary, it's converted to an asset object.
        
        Returns:
            The added asset.
        """
        asset = Asset.resolve(asset)
        token = asset.type, asset.name
        if token in self.assets:
            raise ValueError(f"asset {asset} is already part of the book")
        self.assets[token] = asset
        return asset
    
    def add_component(self, component: str | pathlib.Path | dict[str, Any] | Component) -> Component:
        """
        Add a component to the book.

        Arguments:
            component: The component to add.
                If it's a component object, it's used as-is; if it's a string or path object, it's loaded from that file;
                if it's a dictionary, it's converted to a component object.
        
        Returns:
            The added component.
        """
        component = Component.resolve(component)
        self.components.append(component)
        return component


class Chapter:
    """
    A chapter of a book.

    Attributes:
        id: The chapter id.
        number: The chapter number.
        text: The chapter text.
        title: The chapter title.
    """

    # Conventions:
    chapter_name_regex: ClassVar[Pattern] = re.compile(r"^(\d+)-(.*)\.vyn$")

    def __init__(
        self,
        id: str,
        number: int,
        text: str,
        title: str | None = None,
        path: pathlib.Path | None = None,
    ) -> None:
        self.id = id
        self.number = number
        self.text = text
        self.title = title
        self.path = path
        self.sections: dict[str, Section] = {}

    def __str__(self) -> str:
        return f"chapter #{self.number} ({self.title})"

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def resolve(cls, chapter: str | pathlib.Path | dict[str, Any] | Chapter) -> Chapter:
        """
        Resolve a chapter.

        Arguments:
            chapter: The chapter to resolve.
                If it's a chapter object, it's returned as-is; if it's a string or path object, it's loaded from that
                file; if it's a dictionary, it's converted to a chapter object.

        Returns:
            The resolved chapter.
        """
        if isinstance(chapter, Chapter):
            return chapter
        if isinstance(chapter, dict):
            return cls(**chapter)
        path = pathlib.Path(chapter)
        match = cls.chapter_name_regex.match(path.name)
        if not match:
            raise ValueError(f"{path} is not a valid chapter path (expected '<number>-<id>.vyn')")
        number, id = match.groups()
        number = int(number)
        text = path.read_text()
        return cls(id, number, text, path=path)

    def add_section(self, title: str) -> Section:
        """
        Add a section to the chapter.

        Arguments:
            title: The title of the section.

        Returns:
            The added section.
        """
        slug = INVALID_CHARS.sub("", title.lower()).replace(" ", "-")
        section_id = f"{self.id}-{slug}"
        if section_id in self.sections:
            raise ValueError(f"section {section_id} already exists")
        section = Section(id=section_id, title=title)
        self.sections[section_id] = section
        return section


class Section:
    """
    A section of a chapter.

    Attributes:
        id: The section id.
        title: The section title.
    """

    def __init__(self, id: str, title: str):
        self.id = id
        self.title = title
    
    def __str__(self) -> str:
        return f"section {self.title!r}"

    def __repr__(self) -> str:
        return f"<{self}>"