import contextlib
import pathlib
import tempfile
from typing import Any, ClassVar, Iterator

from auryn import TemplateArgument
from playwright.sync_api import Page, sync_playwright

from ...book import Book
from ..render import Render
from ..format import Format

ROOT = pathlib.Path(__file__).parent


class Print(Format):
    """
    Render a book for print as a PDF.
    """

    template: ClassVar[pathlib.Path] = ROOT / "print.html.aur"
    print_style: ClassVar[pathlib.Path] = ROOT / "print.css"
    pagedjs_script: ClassVar[pathlib.Path] = ROOT / "paged.polyfill.min.js"
    pagedjs_style: ClassVar[pathlib.Path] = ROOT / "paged.interface.css"

    def render(self, book: Book) -> Render:
        """
        Render a book for as print as a PDF.

        Arguments:
            book: The book to render.
        
        Returns:
            The rendered book.
        """
        render = super().render(book)
        render.add_style(self.print_style)
        render.add_style(self.pagedjs_style)
        render.add_script(self.pagedjs_script)
        return render

    def render_binary(self, render: Render) -> bytes:
        """
        Generate the binary data of a rendered book.

        Arguments:
            render: The rendered book.

        Returns:
            The rendered book binary data.
        """
        # Since we don't know how chapters will break across pages, we need to generate the book twice: once to get the
        # breakdown of the chapters, after which we can extract their locations, and another time to populate the table
        # of contents accordingly.
        html = render.execute(self.template, toc={})
        toc = self._extract_toc(render, html)
        render.clear()
        return render.execute(self.template, toc=toc)

    def save(self, render: Render, output: pathlib.Path) -> None:
        """
        Save the rendered book to a PDF file.

        Arguments:
            render: The rendered book.
            output: The output path.
        """
        if not output.suffix == ".pdf":
            output = output.with_suffix(".pdf")
        html = render.to_binary()
        with self._page(render, html) as page:
            # After Paged.js has run, we can print the web page as PDF.
            page.pdf(
                path=output,
                format="A4",
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                display_header_footer=False,
                print_background=True,
            )

    def _extract_toc(self, render: Render, html: bytes) -> dict[str, int]:
        with self._page(render, html) as page:
            # After Paged.js has run, we can extract each chapter's location by detecting chapter headers (h1), and
            # using Paged.js metadata to infer their page numbers.
            toc = page.evaluate(
                """
                () => {
                    const toc = {};
                    const titles = document.querySelectorAll('h1[id]');
                    titles.forEach(title => {
                        let element = title.closest('.pagedjs_page');
                        if (element) {
                            const number = (
                                element.dataset.pageNumber
                                || element.querySelector('.page-number')?.textContent
                            );
                            if (number && title.id) {
                                toc[title.id] = parseInt(number)
                            }
                        }
                    });
                    const sections = document.querySelectorAll('h2[id]');
                    sections.forEach(section => {
                        let element = section.closest('.pagedjs_page');
                        if (element) {
                            const number = (
                                element.dataset.pageNumber
                                || element.querySelector('.page-number')?.textContent
                            );
                            if (number && section.id) {
                                toc[section.id] = parseInt(number)
                            }
                        }
                    });
                    return toc;
                }
                """
            )
            return toc

    @contextlib.contextmanager
    def _page(self, render: Render, html: bytes) -> Iterator[Page]:
        with tempfile.NamedTemporaryFile(suffix=".html") as f, sync_playwright() as p:
            f.write(html)
            prefix = f.name.rsplit("/", 1)[0]
            browser = p.chromium.launch()
            context = browser.new_context()
            page = context.new_page()
            errors: list[str] = []
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: errors.append(f"Page error: {exc}"))
            page.on("requestfailed", lambda req: errors.append(f"Request failed: {req.url}"))

            def route_assets(route, request):
                url = request.url.split("://", 1)[-1]
                path = url[len(prefix) + 1 :]
                if path in render.assets:
                    asset = render.assets[path]
                    route.fulfill(
                        status=200,
                        body=asset.data,
                        headers={"Content-Type": asset.mimetype},
                    )
                else:
                    route.continue_()

            page.route("**/*", route_assets)
            page.goto(f"file://{f.name}")
            try:
                page.wait_for_function("window.status === 'pagedone'", timeout=5000)
                yield page
            except Exception:
                for error in errors:
                    print(error)
                raise
            finally:
                browser.close()
