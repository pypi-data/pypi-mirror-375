from typing import ClassVar

from .asset import Asset


class Style(Asset):
    mimetypes: ClassVar[list[str]] = [
        "text/css",
    ]
    directory: ClassVar[str] = "styles/"