import http.server
import socketserver
import os

# Specify the port you want to use for the server
port = 8000
web_root = "document/en/ps5"

# Change the current working directory to the 'wwwroot' folder
os.chdir(web_root)

# Create a custom request handler that serves files with caching disabled
class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        http.server.SimpleHTTPRequestHandler.end_headers(self)

# Create a socket server with the specified port and custom handler
with socketserver.TCPServer(("0.0.0.0", port), NoCacheHandler) as httpd:
    print(f"Serving at http://localhost:{port}")
    httpd.serve_forever()
