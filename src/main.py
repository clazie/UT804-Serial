import serial

OKCYAN = '\033[96m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'

print("UT804 serial")

ser = serial.Serial()  # open serial port
ser.port = 'COM1'
ser.baudrate = 2400  # set baud rate to 2400 bps
ser.bytesize = serial.SEVENBITS  # number of bits per bytes
ser.parity = serial.PARITY_NONE  # set parity check: no parity
ser.stopbits = serial.STOPBITS_ONE  # number of stop bits
ser.timeout = 0.25  # set timeout to 0.25 second
ser.open()

DEBUG = True


def Log(msg: str):
  if (DEBUG):
    print(f'{OKCYAN}{msg}{ENDC}')


def Warn(msg: str):
  print(f'{WARNING}{msg}{ENDC}')


def Error(msg: str):
  print(f'{FAIL}{msg}{ENDC}')


def calcValue(s: str, corr: int = 0) -> float:
  try:
    if (len(s) < 8):
      raise ValueError('Not a valid value')

    factor = int(s[5:6].decode('ascii'))
    valstr: str = line[0:5].decode('ascii')

    if (valstr == '::0<:'):
      raise ValueError('Overload')

    valint = int(valstr)
    value = float(valint / 100000 * (10 ** (factor + corr)))
    value = round(value, 5)

    if ((s[8:9].decode('ascii') == '4') or (s[8:9].decode('ascii') == '5')):  # Negative sign
      value = -value

  except ValueError as e:
    Warn(f'Value error: {e}')
    value = 99999999.9  # Error value
  except Exception as e:
    Error(f'General error: {e}')
    value = 99999999.9  # Error value
  return value


print(ser.name)
while True:
  line: bytes = ser.readline()

  if (len(line) > 8):  # Minimum length of a valid line
    Log('-----------------------')
    Log(f'Line: {line}')
    measurement: str = line[6:7].decode('ascii')

    match (line[7:8].decode('ascii')):
      case '0':
        acdc = 'DC'
      case '1':
        acdc = 'AC'
      case '3':
        acdc = 'AC+DC'
      case _:  # Unknown
        acdc = ''

    valuestr = ''
    match measurement:
      case '1':  # VDC
        print('DC Voltage measurement')
        value: float = calcValue(line)
        valuestr = f'{value} V {acdc}'

      case '2':  # VAC
        print('AC Voltage measurement')
        value: float = calcValue(line)
        valuestr = f'{value} V {acdc}'

      case '3':  # mVDC
        print('DC Millivolt measurement')
        value: float = calcValue(line, 3)
        valuestr = f'{value} mV {acdc}'

      case '<':  # Frequency (Hz, %)
        if(line[8:9].decode('ascii') == '1'):
          print('Frequency measurement')
          value: float = calcValue(line, 2)
          valuestr = f'{value} Hz'
        elif(line[8:9].decode('ascii') == '5'):
          print('Duty cycle measurement')
          value: float = -1 * calcValue(line, 3)
          valuestr = f'{value} %'

      case '4':  # Ohm
        print('Resistance measurement')
        value: float = calcValue(line, 2)  # Corr factor 10 for Ohm
        valuestr = f'{value} Ohm'

      case ';':  # Diode (V)
        print('Diode measurement')
        value: float = calcValue(line, 1)  # Corr factor 10 for Ohm
        valuestr = f'{value} V'

      case ':':  # Continuity
        print('Continuity measurement')
        value: float = calcValue(line, 2)  # Corr factor 10 for Ohm
        valuestr = f'{value} Ohm'

      case '5':  # Capacitance
        print('Capacitance measurement')
        value: float = calcValue(line, -2)
        valuestr = f'{value} uF'

      case '6':  # Temperature (°C)
        print('Temperature measurement')
        value: float = calcValue(line, 4)
        valuestr = f'{value} °C'

      case '=':  # Temperature (°F)
        print('Temperature measurement')
        value: float = calcValue(line, 4)
        valuestr = f'{value} °F'

      case '7':  # uA
        print('Microampere measurement')
        value: float = calcValue(line, 3)
        valuestr = f'{value} uA {acdc}'

      case '8':  # mA
        print('Milliampere measurement')
        value: float = calcValue(line, 2)
        valuestr = f'{value} mA {acdc}'

      case '?':  # %
        print('Dutycycle measurement')
        value: float = calcValue(line, 3)
        valuestr = f'{value} %'

      case '9':  # A
        print('Ampere measurement')
        value: float = calcValue(line, 1)
        valuestr = f'{value} A {acdc}'

      case '_':
        print(f'Unknown measurement type: {measurement}')
        value: float = calcValue(line)
        valuestr = f'{value} Unknown unit {acdc}'

    print(f'{OKGREEN}Value: {valuestr}{ENDC}')

  if (len(line) > 5):
    tmp: str = line[5:6].decode('ascii')
    Log(f'Char 5: {tmp} (Factor)')
  if (len(line) > 6):
    tmp: str = line[6:7].decode('ascii')
    Log(f'Char 6: {tmp} (Function)')
  if (len(line) > 7):
    tmp: str = line[7:8].decode('ascii')
    Log(f'Char 7: {tmp} ({acdc})')
  if (len(line) > 8):
    tmp: str = line[8:9].decode('ascii')
    Log(f'Char 8: {tmp} (Sign)')
  if (len(line) > 9):
    tmp: str = ord(line[9:10])
    Log(f'Char 9: 0x{tmp}')
  if (len(line) > 10):
    tmp: str = ord(line[10:11])
    Log(f'Char 10: 0x{tmp}')

exit(0)
