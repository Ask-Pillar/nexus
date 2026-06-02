"""Web Ingest — HTTP 端点，接收浏览器插件推送的文本"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "sisyphus" / "src"))
from http.server import HTTPServer, BaseHTTPRequestHandler
from nexus.core import NexusCore

core = NexusCore()


class IngestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        data = json.loads(body)
        text = data.get("text", "")
        source = data.get("source", "web")
        core.write(
            title=f"Ingested from {source}", content=text,
            mem_type="note", tags=["ingest", source],
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    server = HTTPServer(("localhost", 8765), IngestHandler)
    print("Nexus Web Ingest on http://localhost:8765")
    server.serve_forever()


if __name__ == "__main__":
    main()
