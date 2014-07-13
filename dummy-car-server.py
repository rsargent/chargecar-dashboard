#!/usr/bin/python

import json
import math
import random
import sys
import time
import BaseHTTPServer
import SimpleHTTPServer


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Respond to a GET request."""
        if self.path == '/get.json':
            time.sleep(0.25)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            offset = math.pow(math.sin(time.time() * 0.2) * 0.5 + 0.5, 2)
            data = {
                'time':time.time(),
                'minCellVoltage':2.4 + offset * 0.5,
                'avgCellVoltage':2.6 + offset * 0.5,
                'maxCellVoltage':2.8 + offset * 0.5,
                'loadCurrentAmps':-40 + offset * 300,
                'minCellBoardTempC': -20 + offset * 70,
                'avgCellBoardTempC': -15 + offset * 70,
                'maxCellBoardTempC': -10 + offset * 70,
            }
            self.wfile.write(json.dumps(data))
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# BaseHTTPServer.HTTPServer
# HandlerClass.protocol_version = "HTTP/1.1"
httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8002), Handler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()

