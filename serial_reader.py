import serial
import time


if __name__ == '__main__':
    with open('notinservice.hex', 'w') as f:
        ser = serial.Serial('/dev/tty.usbmodem14101', 115200)
        while True:
            line = ser.readline()
            if line.startswith(b'sertx'):
                linestr = str(line, 'ascii').strip()
                hex_stuff = linestr.split('sertx')[1]
                f.write(hex_stuff)