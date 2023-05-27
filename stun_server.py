from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "Hello!\n"

            self.wfile.write(bytes(message, 'utf8'))
        return


server_address = ('', 8000)
httpd = HTTPServer(server_address, RequestHandler)
print("Starting server...")
httpd.serve_forever()
