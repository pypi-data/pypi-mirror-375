from typing import ClassVar

from .asset import Asset


class Script(Asset):
    mimetypes: ClassVar[list[str]] = [
        "text/javascript",
    ]
    directory: ClassVar[str] = "scripts/"