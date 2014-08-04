#!/usr/bin/python

import os
import subprocess

os.chdir(os.path.dirname(__file__))
print "Starting car-server.py in background"
subprocess.Popen(['./car-server.py'])
print "Starting startx"
subprocess.check_output('startx')

