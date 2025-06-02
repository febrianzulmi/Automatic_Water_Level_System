import serial, argparse, sys, glob

def scanPort(flag):
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        if int(flag) == 0:
           ports = glob.glob('/dev/ttyS[0-9]*')
        elif int(flag) == 1:
           ports = glob.glob('/dev/ttySC[0-9]*')
        elif int(flag) == 2:
           ports = glob.glob('/dev/ttyUS[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/ttyUS.*')
    else:
        raise EnvironmentError('Unsupported platform')
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def addPort(port, ports):
    for i in port:
        ports.append(i)
    return ports
        
ports = []
port_gpio = scanPort(0)
ports = addPort(port_gpio, ports)
port_sc = scanPort(1)
ports = addPort(port_sc, ports)
port_usb = scanPort(2)
ports = addPort(port_usb, ports)
length = len(ports)
if length > 0:
   for i in ports:
       print(i)