from __future__ import annotations
import http.server
import time
from typing import cast, TYPE_CHECKING

import auryn
import watchdog.events
import watchdog.observers

if TYPE_CHECKING:
    from .render import Render


class Server(http.server.HTTPServer):
    """
    A simple HTTP server to serve a book and its assets.
    """

    def __init__(self, port: int, render: Render) -> None:
        super().__init__(("", port), Handler)
        self.allow_reuse_address = True # Prevent OSError: [Errno 98] Address already in use
        self.render = render
        self.html = self.render.to_html()

    def reload(self) -> None:
        """
        If the book was created from a directory, re-render it.
        """
        if self.render.book.path:
            try:
                self.render = self.render.reload()
                self.html = self.render.to_html()
            except auryn.Error as error:
                print(error.report())
    
    def serve(self) -> None:
        """
        Serve the book, reloading it when modified.
        """
        if self.render.book.path:
            observer = watchdog.observers.Observer()
            observer.schedule(Reloader(self), self.render.book.path, recursive=True)
            observer.start()
        print(f"http://localhost:{self.server_port}")
        try:
            self.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            if self.render.book.path:
                observer.stop()
                observer.join()


class Handler(http.server.SimpleHTTPRequestHandler):
    """
    A simple request handler to serve a book and its assets.
    """

    def do_GET(self) -> None:
        """
        Return the book for GET /, and a particular asset (or 404) for GET /<asset>.
        """
        server: Server = cast(Server, self.server)
        path = self.path.strip("/")
        if not path:
            self._send("text/html", server.html.encode())
        elif path in server.render.assets:
            asset = server.render.assets[path]
            self._send(asset.mimetype, asset.data)
        else:
            self.send_response(404)
            self.end_headers()

    def _send(self, mimetype: str, data: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-type", mimetype)
        self.send_header("Content-length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


class Reloader(watchdog.events.FileSystemEventHandler):
    """
    A file system event handler to reload the server whenever the book is modified.
    """

    def __init__(self, server: Server) -> None:
        self.server = server

    def on_modified(self, event: watchdog.events.FileSystemEvent) -> None:
        """
        Reload the server whenever the book is modified.
        """
        print("reloading book... ", end="")
        started = time.time()
        self.server.reload()
        print(f"done in {time.time() - started:0.2f} seconds")