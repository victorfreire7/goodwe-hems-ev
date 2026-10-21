"""Servidor do dashboard: entrega index.html e repassa /api/* ao backend (README, seção 8.1).

Como o navegador só fala com este servidor, não há CORS. Variáveis: DASHBOARD_HOST (127.0.0.1),
DASHBOARD_PORT (8080) e BACKEND_URL (http://127.0.0.1:3000). Uso: python dashboard/server.py"""
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PAGE = Path(__file__).resolve().parent / "index.html"
FORWARDED_HEADERS = ("Content-Type", "X-Simulation-Id")


def make_handler(backend_url):
    class Handler(BaseHTTPRequestHandler):
        def _reply(self, status, body, content_type):
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _proxy(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", 0))) or None
            request = urllib.request.Request(backend_url.rstrip("/") + self.path[len("/api"):], data=body,
                                             method=self.command)
            for name in FORWARDED_HEADERS:
                if self.headers.get(name):
                    request.add_header(name, self.headers[name])
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    self._reply(response.status, response.read(), response.headers.get("Content-Type", "application/json"))
            except urllib.error.HTTPError as error:
                self._reply(error.code, error.read(), error.headers.get("Content-Type", "application/json"))
            except (urllib.error.URLError, TimeoutError):
                self._reply(502, b'{"error":"Backend indispon\\u00edvel."}', "application/json")

        def do_GET(self):
            if self.path.startswith("/api/"):
                self._proxy()
            elif self.path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
            elif self.path in ("/", "/index.html"):
                self._reply(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            else:
                self._reply(404, b'{"error":"Rota n\\u00e3o encontrada."}', "application/json")

        def do_PUT(self):
            if self.path.startswith("/api/"):
                self._proxy()
            else:
                self._reply(404, b'{"error":"Rota n\\u00e3o encontrada."}', "application/json")

        def log_message(self, format, *args):
            pass

    return Handler


def main():
    host, port = os.environ.get("DASHBOARD_HOST", "127.0.0.1"), int(os.environ.get("DASHBOARD_PORT", 8080))
    backend = os.environ.get("BACKEND_URL", "http://127.0.0.1:3000")
    print(f"Dashboard em http://{host}:{port} (backend: {backend})")
    ThreadingHTTPServer((host, port), make_handler(backend)).serve_forever()


if __name__ == "__main__":
    main()
