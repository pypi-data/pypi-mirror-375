from typing import ClassVar

from .asset import Asset


class Image(Asset):
    mimetypes: ClassVar[list[str]] = [
        "image/png",
        "image/jpeg",
        "image/gif",
        "image/svg+xml",
    ]
    directory: ClassVar[str] = "images/"