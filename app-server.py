#!/usr/bin/env python3
"""Serves the BaseUI app and forwards /janus to the Janus HTTP API, so the browser sees one origin (no CORS)."""
import argparse
import http.client
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HOP_BY_HOP = {"connection", "keep-alive", "transfer-encoding", "te", "trailer", "upgrade", "proxy-authorization", "proxy-authenticate"}


class Handler(SimpleHTTPRequestHandler):
    """Static files for everything, except /janus which goes to the upstream Janus server."""

    upstream = "127.0.0.1:8080"

    def is_janus(self):
        """Tells whether this request is for the Janus API."""
        return self.path == "/janus" or self.path.startswith(("/janus/", "/janus?"))

    def proxy(self):
        """Replays the request on the upstream server and sends its answer back unchanged."""
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP_BY_HOP | {"host"}}
        connection = http.client.HTTPConnection(self.upstream, timeout=130)
        try:
            connection.request(self.command, self.path, body, headers)
            response = connection.getresponse()
            data = response.read()
        except OSError as error:
            self.send_error(502, f"Janus upstream {self.upstream} unreachable: {error}")
            return
        finally:
            connection.close()
        self.send_response(response.status)
        for key, value in response.getheaders():
            if key.lower() not in HOP_BY_HOP | {"content-length"}:
                self.send_header(key, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        """GET: Janus API or static file."""
        self.proxy() if self.is_janus() else super().do_GET()

    def do_POST(self):
        """POST: only the Janus API accepts it."""
        self.proxy() if self.is_janus() else self.send_error(405)

    def do_OPTIONS(self):
        """OPTIONS: preflight for the Janus API."""
        self.proxy() if self.is_janus() else self.send_error(405)


def main():
    """Parses the command line and runs the threaded server (threads keep Janus long-polls from blocking each other)."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8075)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--directory", default=".")
    parser.add_argument("--upstream", default="127.0.0.1:8080", help="host:port that serves /janus")
    args = parser.parse_args()
    Handler.upstream = args.upstream
    server = ThreadingHTTPServer((args.bind, args.port), partial(Handler, directory=args.directory))
    print(f"app on http://{args.bind}:{args.port}/  (/janus -> http://{args.upstream}/janus)")
    server.serve_forever()


if __name__ == "__main__":
    main()
