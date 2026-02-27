from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir('/app')
httpd = HTTPServer(('0.0.0.0', 3000), CORSRequestHandler)
print("Dashboard running on http://localhost:3000")
httpd.serve_forever()
