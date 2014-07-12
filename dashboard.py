#!/usr/bin/python

import serial

print 'About to open BMS'
bms = serial.Serial('/dev/tty.usbserial', 19200)
print 'Opened BMS'
bms

################

import sys
import datetime
from dateutil import tz

class BmsReport:
    def __init__(this, timestamp, raw):
        this.timestamp = timestamp
        this.raw = raw

    @staticmethod
    def fromSerial(bms):
        START = '\x1b'
        # Wait until start character
        while bms.read(1) != START:
            pass
        while True:
            raw = ''
            timestamp = datetime.datetime.now(tz.tzlocal())
            while True:
                c = bms.read(1)
                if c == START:
                    print 'Read START unexpectedly early from BMS'
                    break
                raw += c
                if len(raw) == 1653:
                    if (raw[0] == '[' and
                        raw[1] == 'H' and
                        raw[66] == ' ' and
                        raw[113] == ' ' and
                        raw[626] == ' ' and
                        raw[1139] == ' ' and
                        raw[1652] == ' '):
                        return BmsReport(timestamp, raw)
                    print 'Read incorrect delimiter from BMS'
                    break
    
    def parsed(this):
        # contentGroupByteBuffer: offset * 2 + 2
        # auxiliaryGroupByteBuffer: offset * 2 + 67
        return {
            'bmsFault': int(this.raw[2:4], 16),
            'numOnOffCycles': int(this.raw[4:8], 16),
            'timeSincePowerUpInSecs': int(this.raw[8:14], 16),
            'sourceCurrentAmps': int(this.raw[14:18], 16) / 10.0,
            'loadCurrentAmps': int(this.raw[18:22], 16) / 10.0,
            'variousIOState': int(this.raw[22:24], 16),
            'relativeChargeCurrentLimitPercentage': int(this.raw[24:26], 16) / 255.0 * 100.0,
            'relativeDischargeCurrentLimitPercentage': int(this.raw[26:28], 16) / 255.0 * 100.0,
            'areRelaysOn': int(this.raw[28:30], 16),
            'stateOfChargePercentage': int(this.raw[30:32], 16) / 100.0,

            # Voltages in V
            'packTotalVoltage': int(this.raw[32:36], 16) / 10.0,
            'minCellVoltage': int(this.raw[42:44], 16) / 100.0 + 2.0,
            'avgCellVoltage': int(this.raw[46:48], 16) / 100.0 + 2.0,
            'maxCellVoltage': int(this.raw[48:50], 16) / 100.0 + 2.0,

            # Temperatures in C
            'minCellBoardTempC': int(this.raw[52:54], 16) - 0x80,
            'avgCellBoardTempC': int(this.raw[56:58], 16) - 0x80,
            'maxCellBoardTempC': int(this.raw[58:60], 16) - 0x80,
            
            # Stats
            'depthOfDischargeKAH': int(this.raw[83:87], 16) / 1000.0,
            'capacityKAH': int(this.raw[87:91], 16) / 1000.0,
            'stateOfHealthPercentage': int(this.raw[91:93], 16) / 100.0,

            # Resistance in Ohms
            'packTotalResistance': int(this.raw[93:97], 16) * 1e-4,
            'minCellResistance': int(this.raw[97:99], 16) * 1e-4,
            'avgCellResistance': int(this.raw[101:103], 16) * 1e-4,
            'maxCellResistance': int(this.raw[103:105], 16) * 1e-4,

            # Power in W
            'power': int(this.raw[109:113], 16) * 100,
        }

#######

def c2f(c):
    return c * 9.0 / 5.0 + 32
    
def format_dashboard(bms_report):
    b = bms_report.parsed()
    print datetime.datetime.now(tz.tzlocal()).strftime('%Y-%m-%d %H:%M:%S%z')
    print
    print 'Power   %5dW' % b['power']
    print ('Voltage  %.2fV : %.2fV : %.2fV  (2.5V-2.7V to 3.6V)' % 
        (b['minCellVoltage'], b['avgCellVoltage'], b['maxCellVoltage']))
    print ('Temp      %3dF :  %3dF :  %3dF  (-20F to 113F-130F)' % 
        (c2f(b['minCellBoardTempC']), c2f(b['avgCellBoardTempC']), c2f(b['maxCellBoardTempC'])))
    print
    print ('Total consumed %.1f KAH (of approx %.1f KAH)' % 
        (b['depthOfDischargeKAH'], b['capacityKAH']))

########

BmsReport.fromSerial(bms)
BmsReport.fromSerial(bms)

while True:
    report = BmsReport.fromSerial(bms)
    format_dashboard(report)
    logfile = report.timestamp.strftime('/var/log/chargecar/bms-%Y-%m-%d.log')
    epoch_time = (report.timestamp - datetime.datetime(1970, 1, 1, tzinfo=tz.tzutc())).total_seconds()
    formatted_date = report.timestamp.strftime('%Y-%m-%d %H:%M:%S%z')
    open(logfile, 'a+b').write('%.3f %s %s\n' % (epoch_time, formatted_date, report.raw))
    
