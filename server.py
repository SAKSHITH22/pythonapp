from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Dummy credentials
USERNAME = "admin"
PASSWORD = "1234"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("index.html", "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            fields = urllib.parse.parse_qs(post_data.decode())

            username = fields.get('username', [''])[0]
            password = fields.get('password', [''])[0]

            print(f"Login attempt: username={username}, password={password}")   # Log the attempt

            if username == USERNAME and password == PASSWORD:
                message = f"""
                <html>
                <body style="text-align:center; font-family:Arial;">
                    <h1>Welcome, {username}!</h1>
                    <p>Login successful.</p>
                    <a href="/">Logout</a>
                </body>
                </html>
                """
            else:
                message = """
                <html>
                <body style="text-align:center; font-family:Arial;">
                    <h1>Login Failed</h1>
                    <p>Invalid username or password.</p>
                    <a href="/">Try Again</a>
                </body>
                </html>
                """

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(message.encode())
        else:
            self.send_error(404, "Page Not Found")

if __name__ == '__main__':
    PORT = 8001
    server = HTTPServer(('localhost', PORT), SimpleHTTPRequestHandler)
    print(f"Server running on http://localhost:{PORT}")

    server.serve_forever()
