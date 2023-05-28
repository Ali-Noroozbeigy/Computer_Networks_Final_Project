from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import redis


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/users':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            users = []
            for key in cache.scan_iter('*'):
                users.append(key.decode('utf-8'))
            
            message = json.dumps(users)

            self.wfile.write(message.encode('utf-8'))
            return

        elif self.path.startswith("/user/"):
            username = self.path[6:]

            if not cache.exists(username):
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = json.dumps({'response': "404 User Name Not Found\n"})
                self.wfile.write(message.encode('utf-8'))
                return

            info = cache.hgetall(username)
            
            info = {key.decode('utf-8'): value.decode('utf-8') for key, value in info.items()}
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = json.dumps(info)
            self.wfile.write(message.encode('utf-8'))
            return
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = json.dumps({"response": "404 Not Found\n"})
            self.wfile.write(message.encode('utf-8'))
        return
    
    def do_POST(self):
        if self.path == '/add-user':
            content_length = int(self.headers.get('Content-length', 0))

            post_data = self.rfile.read(content_length)
            dec = post_data.decode('utf-8')
            parsed = json.loads(dec)
            if not cache.exists(parsed['username']):
                cache.hmset(parsed['username'], {'IP': self.client_address[0], 'PORT': parsed['PORT']})

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = json.dumps({'response': "200 OK\n"})
                self.wfile.write(message.encode('utf-8'))
                return
            else:
                self.send_response(409)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = json.dumps({"response": "409 Conflict: username exits\n"})
                self.wfile.write(message.encode('utf-8'))
                return
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = json.dumps({"response": "404 Not Found\n"})

            self.wfile.write(message.encode('utf-8'))



server_address = ('', 8000)
httpd = HTTPServer(server_address, RequestHandler)
cache = redis.Redis(host='localhost', port=6379, db=0)
print("Starting server...")
httpd.serve_forever()
