#!/usr/bin/python

import json
import random
import sys
import time
import BaseHTTPServer
import SimpleHTTPServer


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Respond to a GET request."""
        if self.path == '/get.json':
            time.sleep(0.05)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            offset = random.uniform(-.25, .25)
            data = {'minCellVoltage':2.6 + offset,
                    'avgCellVoltage':2.8 + offset,
                    'maxCellVoltage':3.0 + offset}
            self.wfile.write(json.dumps(data))
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# BaseHTTPServer.HTTPServer
# HandlerClass.protocol_version = "HTTP/1.1"
httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8002), Handler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()

