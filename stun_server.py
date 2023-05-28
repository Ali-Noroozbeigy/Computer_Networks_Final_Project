from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import redis


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "Hello!\n"

            self.wfile.write(bytes(message, 'utf8'))

        elif self.path.startswith("/user/"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = f"Hello {self.path[6:]}\n"

            self.wfile.write(bytes(message, 'utf8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = "404 Not Found\n"

            self.wfile.write(bytes(message, 'utf8'))
        return
    
    def do_POST(self):
        if self.path == '/add-user':
            content_length = int(self.headers.get('Content-length', 0))

            post_data = self.rfile.read(content_length)
            dec = post_data.decode('utf-8')
            parsed = json.loads(dec)
            print(parsed['username'], parsed['IP'])

            cache = redis.Redis(host='localhost', port=6379, db=0)
            cache.set(parsed['username'], parsed['IP'])



server_address = ('', 8000)
httpd = HTTPServer(server_address, RequestHandler)
print("Starting server...")
httpd.serve_forever()
