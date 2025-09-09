from __future__ import annotations
import contextlib
import io
import mimetypes
import pathlib
from typing import ClassVar

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from .asset import Asset

ITALIC_SUFFIX = "-italic"


class Font(Asset):

    mimetypes: ClassVar[list[str]] = [
        "font/ttf",
        "font/otf",
        "font/woff",
        "font/woff2",
    ]
    directory: ClassVar[str] = "fonts/"
    types: ClassVar[dict[str, str]] = {
        "font/ttf": "truetype",
        "font/otf": "opentype",
        "font/woff": "woff",
        "font/woff2": "woff2",
    }

    def __init__(
        self,
        name: str,
        mimetype: str,
        data: bytes,
        path: pathlib.Path | None = None,
    ) -> None:
        super().__init__(name, mimetype, data, path)
        self.font_type, self.family, self.style, self.weight = self._parse()

    def __str__(self) -> str:
        output: list[str] = []
        if self.weight != 400:
            output.append(self.weight_name)
        if self.style != "normal":
            output.append(self.style)
        output.append(self.family)
        return " ".join(output)

    def __repr__(self) -> str:
        return f"<{self}>"

    @classmethod
    def extract_fonts(cls, path: str | pathlib.Path) -> list[Font]:
        """
        Extract static fonts from a variable font.

        Arguments:
            variable_font_path: The path to the variable font.
        
        Returns:
            A list of extracted fonts.
        """
        path = pathlib.Path(path)
        if path.is_dir():
            fonts: list[Font] = []
            for file in path.iterdir():
                fonts.extend(cls.extract_fonts(file))
            return fonts
        mimetype = mimetypes.guess_type(path)[0]
        if mimetype not in cls.types:
            supported = ", ".join(cls.types)
            raise ValueError(f"unsupported font type: {mimetype!r} (supported font types are {supported})")
        font = TTFont(path)
        if "fvar" not in font:
            return []
        fvar = font["fvar"]
        name_table = font["name"]
        fonts: list[Font] = []
        for instance in fvar.instances:
            name_id = instance.subfamilyNameID
            instance_name = name_table.getName(name_id, 3, 1, 0x409) or name_table.getName(name_id, 1, 0, 0)
            if instance_name is None:
                continue
            coordinates = {axis.axisTag: instance.coordinates.get(axis.axisTag, axis.defaultValue) for axis in fvar.axes}
            instantiated: TTFont = instantiateVariableFont(font, axisLimits=coordinates, inplace=False)
            basename = path.stem.lower()
            if basename.endswith(ITALIC_SUFFIX):
                basename = basename.removesuffix(ITALIC_SUFFIX)
            name = f"{basename}-{str(instance_name).replace(' ', '')}.{path.suffix}"
            file = io.BytesIO()
            instantiated.save(file)
            fonts.append(cls(name, mimetype, file.getvalue()))
        return fonts
    
    @property
    def weight_name(self) -> str:
        if self.weight <= 100:
            return "thin"
        elif self.weight <= 200:
            return "extralight"
        elif self.weight <= 300:
            return "light"
        elif self.weight <= 400:
            return "normal"
        elif self.weight <= 500:
            return "medium"
        elif self.weight <= 600:
            return "semibold"
        elif self.weight <= 700:
            return "bold"
        elif self.weight <= 800:
            return "extrabold"
        else:
            return "black"
    
    def _parse(self) -> tuple[str, str, str, int]:
        font_type = self.types[self.mimetype]
        ttf = TTFont(io.BytesIO(self.data))
        family = self._get_font_name(ttf, 16) or self._get_font_name(ttf, 1)
        if not family:
            raise ValueError(f"unable to extract font {self.name!r} family")
        style = self._get_font_style(ttf)
        weight = self._get_font_weight(ttf)
        return font_type, family, style, weight

    def _get_font_name(self, ttf: TTFont, name_id: int) -> str | None:
        for record in ttf["name"].names:
            if record.nameID == name_id:
                with contextlib.suppress(Exception):
                    return record.toUnicode()
        return None

    def _get_font_style(self, ttf: TTFont) -> str:
        subfamily = self._get_font_name(ttf, 17) or self._get_font_name(ttf, 2)
        if subfamily and "italic" in subfamily.lower():
            return "italic"
        return "normal"

    def _get_font_weight(self, ttf: TTFont) -> int:
        subfamily = self._get_font_name(ttf, 16) or self._get_font_name(ttf, 1)
        if subfamily:
            match subfamily.lower():
                case "thin":
                    return 100
                case "extralight" | "ultralight":
                    return 200
                case "light":
                    return 300
                case "regular" | "normal":
                    return 400
                case "medium":
                    return 500
                case "semibold" | "demibold":
                    return 600
                case "bold":
                    return 700
                case "extrabold" | "ultrabold":
                    return 800
                case "black" | "heavy":
                    return 900
        with contextlib.suppress(Exception):
            return int(ttf["OS/2"].usWeightClass)
        return 400