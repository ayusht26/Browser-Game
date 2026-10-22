import os
import sys
import mimetypes
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gta-vc-web")

mimetypes.init()
mimetypes.add_type("application/wasm", ".wasm")
mimetypes.add_type("text/javascript", ".js")
mimetypes.add_type("audio/mpeg", ".mp3")
mimetypes.add_type("audio/wav", ".wav")
mimetypes.add_type("application/octet-stream", ".dff")
mimetypes.add_type("application/octet-stream", ".txd")
mimetypes.add_type("application/octet-stream", ".col")
mimetypes.add_type("application/octet-stream", ".dir")
mimetypes.add_type("application/octet-stream", ".dat")
mimetypes.add_type("application/octet-stream", ".ipl")
mimetypes.add_type("application/octet-stream", ".ide")
mimetypes.add_type("application/octet-stream", ".ifp")
mimetypes.add_type("application/octet-stream", ".sdt")
mimetypes.add_type("application/octet-stream", ".raw")
mimetypes.add_type("application/octet-stream", ".adf")
mimetypes.add_type("application/octet-stream", ".scm")
mimetypes.add_type("application/octet-stream", ".cfg")
mimetypes.add_type("application/octet-stream", ".zon")
mimetypes.add_type("application/octet-stream", ".gxt")
mimetypes.add_type("application/octet-stream", ".sc")
mimetypes.add_type("application/octet-stream", ".img")
mimetypes.add_type("font/ttf", ".ttf")

class ViceCityHTTPHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Necessary headers for WebAssembly performance and cross-origin isolation
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        # Route root requests to host.html
        if self.path == "/" or self.path == "":
            self.path = "/host.html"
            return super().do_GET()

        # Disallow directory listings for asset directories
        full_path = self.translate_path(self.path)
        if os.path.isdir(full_path):
            self.send_error(404, "Directory listing forbidden")
            return None

        return super().do_GET()

def run_server():
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, ViceCityHTTPHandler)
    print(f"============================================================")
    print(f"   GRAND THEFT AUTO: VICE CITY - WEBASSEMBLY PORT")
    print(f"   Server running at: http://localhost:{PORT}")
    print(f"   Serving directory: {DIRECTORY}")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
