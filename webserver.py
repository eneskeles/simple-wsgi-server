# WSGI compatible web server
import socket
from io import StringIO
from app import Application
from typing import Dict, List, Tuple
from enum import Enum

class HttpStatusCode(Enum):
    OK = '200 OK',
    ACCEPTED = '201 Accepted'
    NOT_FOUND = '404 Not Found'


EOL = '\r\n'
class HttpRequestParser:
    def __init__(self, http_request: str):
        request, *headers, _, body = http_request.split(EOL)
        method, path, protocol = request.split()
        
        headers = {
            line.split(':', maxsplit=1)
            for line in headers
        }
        
        self.method: str = method
        self.path: str = path
        self.protocol: str = protocol
        self.headers: Dict[str, str] = headers
        self.body: str = body

        self.set_environ()

    def set_environ(self) -> Dict[str, str]:
        self.environ = {
            'REQUEST_METHOD': self.method,
            'PATH_INFO': self.path,
            'SERVER_PROTOCOL': self.protocol,
            'wsgi.input': StringIO(self.body),
            #**format_headers(headers),
        }

class HttpResponse:
    def __init__(self, protocol, status_code, headers, body):
        self.protocol: str = protocol
        self.headers: Dict[str: str] = headers
        self.status_code: HttpStatusCode = status_code
        self.body: str = body
        
    def __str__(self):
        headers_as_str = f'{EOL}'.join([
            f'{header_name}: {header_value}' for (header_name, header_value) in self.headers.items()
        ])
        return f'{self.protocol} {self.status_code}{EOL}' + headers_as_str + f'{EOL}{EOL}{self.body}{EOL}'
        

class WebServer:
    def __init__(self, host, port, backlog, packet_size=1024, encoding='utf-8'):
        self.socket = socket.socket()
        self.socket.bind((host, port))
        self.socket.listen(backlog)
        
        self.request_size = packet_size
        self.encoding = encoding

    def run(self):
        con, addr = self.socket.accept()

        with con:
            http_request = con.recv(self.request_size).decode(self.encoding)
            parser = HttpRequestParser(http_request)
            environ = parser.environ

            result = Application(environ, start_response)

            for chunk in result:
                if chunk:
                    con.sendall(chunk.encode('utf-8'))

        self.socket.close()

        def start_response(status: str, response_headers: List[Tuple[str, str]], exc_info=None):
            con.sendall(f'HTTP/1.1 {status}{EOL}')
            for (header_name, header_value) in response_headers:
                con.sendall(f'{header_name}: {header_value}{EOL}')
            con.sendall(EOL)
        

