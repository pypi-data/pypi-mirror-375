import pathlib
from typing import Any, ClassVar

from ...book import Book
from ..format import Format
from ..render import Render

ROOT = pathlib.Path(__file__).parent


class Web(Format):
    """
    A format to render books into web pages.
    """

    # Resources:
    template: ClassVar[pathlib.Path] = ROOT / "web.html.aur"
    web_style: ClassVar[pathlib.Path] = ROOT / "web.css"
    web_script: ClassVar[pathlib.Path] = ROOT / "web.js"

    def render(self, book: Book) -> Render:
        """
        Render a book as a webpage.

        Arguments:
            book: The book to render.
        
        Returns:
            The rendered book.
        """
        render = super().render(book)
        render.add_style(self.web_style)
        render.add_script(self.web_script)
        return render
    
    def render_binary(self, render: Render) -> bytes:
        """
        Generate the binary data of a rendered book.

        Arguments:
            render: The rendered book.

        Returns:
            The rendered book binary data.
        """
        return render.execute(self.template)
    
    def save(self, render: Render, output: pathlib.Path) -> None:
        """
        Save the rendered book to a static website directory.

        Arguments:
            render: The rendered book.
            output: The output path.
        """
        output = pathlib.Path(output)
        if not output.exists():
            output.mkdir(parents=True, exist_ok=True)
        html = render.to_html()
        (output / "index.html").write_bytes(html)
        for asset_url, asset in render.assets.items():
            asset_path = output / asset_url
            asset_path.parent.mkdir(parents=True, exist_ok=True)
            asset_path.write_bytes(asset.data)