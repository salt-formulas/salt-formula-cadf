#!/usr/bin/env python
# coding: utf-8

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from pygments import highlight, lexers, formatters
import SocketServer
import json

class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")
        content_len = int(self.headers.getheader('content-length', 0))
        parsed = json.loads(self.rfile.read(content_len))
        formatted_json = json.dumps(parsed, indent=2, sort_keys=True)
        colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())
        print(colorful_json)
        print "_____________________________________________________"

def run(server_class=HTTPServer, handler_class=S, port=33333):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
