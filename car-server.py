#!/usr/bin/python

import serial

print 'About to open BMS'
bms = serial.Serial('/dev/ttyUSB0', 19200)
print 'Opened BMS'
bms

########

from bms import *

########


from Queue import Queue
import threading

queue = Queue()

def poll_bms(bms, queue):
    # Throw away the first two
    BmsReport.fromSerial(bms)
    BmsReport.fromSerial(bms)
    # Queue up reports for serving over http
    while True:
        report = BmsReport.fromSerial(bms)
        queue.put(report.parsed())
        logfile = report.timestamp.strftime('/root/cc/log/bms-%Y-%m-%d.log')
        epoch_time = (report.timestamp - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()
        formatted_date = report.timestamp.strftime('%Y-%m-%d %H:%M:%S%z')
        open(logfile, 'a+b').write('%.3f %s %s\n' % (epoch_time, formatted_date, report.raw))

threading.Thread(target=poll_bms, args=(bms, queue)).start()

########

import BaseHTTPServer
import SimpleHTTPServer
import json

class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        global queue
        if self.path == '/get.json':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            report = queue.get()
            out = json.dumps(report)
            log('Serving report that was read %.3f seconds ago' % (time.time() - report['time']))
            self.wfile.write(out)
        else:
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

# BaseHTTPServer.HTTPServer
# HandlerClass.protocol_version = "HTTP/1.1"
httpd = BaseHTTPServer.HTTPServer(('127.0.0.1', 8002), Handler)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()

