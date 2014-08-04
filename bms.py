import sys
import datetime
from dateutil import tz
import time

def log(msg):
    print msg
    formatted_date = datetime.datetime.now(tz.tzlocal()).strftime('%Y-%m-%d %H:%M:%S%z')
    open('/root/cc/log/bms_messages.log', 'a+b').write('%s %s\n' % (formatted_date, msg))

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
                    log('Read START unexpectedly early from BMS after %d bytes' % (len(raw)))
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
                        log('Read report of length %d' % (len(raw)))
                        return BmsReport(timestamp, raw)
                    log('Read incorrect delimiter from BMS')
                    break

    # TODO(rsargent): make this static
    def signed16(self, x):
        if x > 32767:
            return x - 65535
        else:
            return x
    
    def parsed(self):
        # contentGroupByteBuffer: offset * 2 + 2
        # auxiliaryGroupByteBuffer: offset * 2 + 67
        return {
            'time':time.time(),
            'bmsFault': int(self.raw[2:4], 16),
            'numOnOffCycles': int(self.raw[4:8], 16),
            'timeSincePowerUpInSecs': int(self.raw[8:14], 16),
            'sourceCurrentAmps': self.signed16(int(self.raw[14:18], 16)) / 10.0,
            'loadCurrentAmps': self.signed16(int(self.raw[18:22], 16)) / 10.0,
            'variousIOState': int(self.raw[22:24], 16),
            'relativeChargeCurrentLimitPercentage': int(self.raw[24:26], 16) / 255.0 * 100.0,
            'relativeDischargeCurrentLimitPercentage': int(self.raw[26:28], 16) / 255.0 * 100.0,
            'areRelaysOn': int(self.raw[28:30], 16),
            'stateOfChargePercentage': int(self.raw[30:32], 16) / 100.0,

            # Voltages in V
            'packTotalVoltage': int(self.raw[32:36], 16) / 10.0,
            'minCellVoltage': int(self.raw[42:44], 16) / 100.0 + 2.0,
            'avgCellVoltage': int(self.raw[46:48], 16) / 100.0 + 2.0,
            'maxCellVoltage': int(self.raw[48:50], 16) / 100.0 + 2.0,

            # Temperatures in C
            'minCellBoardTempC': int(self.raw[52:54], 16) - 0x80,
            'avgCellBoardTempC': int(self.raw[56:58], 16) - 0x80,
            'maxCellBoardTempC': int(self.raw[58:60], 16) - 0x80,
            
            # Stats
            'depthOfDischargeKAH': int(self.raw[83:87], 16) / 1000.0,
            'capacityKAH': int(self.raw[87:91], 16) / 1000.0,
            'stateOfHealthPercentage': int(self.raw[91:93], 16) / 100.0,

            # Resistance in Ohms
            'packTotalResistance': int(self.raw[93:97], 16) * 1e-4,
            'minCellResistance': int(self.raw[97:99], 16) * 1e-4,
            'avgCellResistance': int(self.raw[101:103], 16) * 1e-4,
            'maxCellResistance': int(self.raw[103:105], 16) * 1e-4,

            # Power in W
            'power': int(self.raw[109:113], 16) * 100,
        }
