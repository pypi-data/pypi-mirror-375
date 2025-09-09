from __future__ import annotations
import mimetypes
import pathlib
from typing import Any, ClassVar

type AssetArgument = str | pathlib.Path | dict[str, Any] | Asset


class Asset:
    """
    An asset to be included in a book.

    Attributes:
        name: The asset name.
        mimetype: The asset mimetype.
        data: The asset data.
        path: The asset path.
    """

    mimetypes: ClassVar[list[str]] = []
    directory: ClassVar[str] = "files/"

    def __init__(
        self,
        name: str,
        mimetype: str,
        data: bytes,
        path: pathlib.Path | None = None,
    ) -> None:
        self.type = self.__class__.__name__.lower()
        self.name = name
        self.mimetype = mimetype
        self.data = data
        self.path = path

    def __str__(self) -> str:
        return f"{self.type} {self.name!r}"

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def resolve(cls, asset: AssetArgument) -> Asset:
        """
        Resolve an asset.

        Arguments:
            asset: The asset.
                If it's an asset object, it's returned as-is; if it's a string or path object, it's loaded from that
                path; if it's a dictionary, it's converted to an asset object.

        Returns:
            The resolved asset.
        """
        if isinstance(asset, Asset):
            return asset
        if isinstance(asset, dict):
            return cls(**asset)
        path = pathlib.Path(asset)
        mimetype, _ = mimetypes.guess_type(path.name)
        if mimetype is None:
            raise ValueError(f"{path} does not match any mimetype")
        data = path.read_bytes()
        for subclass in cls.__subclasses__():
            if mimetype in subclass.mimetypes:
                cls = subclass
                break
        return cls(
            name=path.name,
            mimetype=mimetype,
            data=data,
            path=path,
        )

    @property
    def url(self) -> str:
        """
        The URL of the asset (when the book is served, or within websites/ebooks).
        """
        return f"{self.directory}{self.name}"