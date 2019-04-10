import inspect
from random import randint
from time import sleep
OUT = 1
IN = 1

LOW = 0
HIGH = 1

BOARD = 'BOARD'
BCM = 'BCM'

# Defaults:
__warnings = True
__mode = "BOARD"


# This is not a real mock, it just print a 'reminder' that there could be warnings
# because setwarnings has not been set to false
def showwarning():
    global __warnings

    if __warnings:
        print("This script could print warnings. Use GPIO.setwarnings(False) to disable warnings.")
        print("GPIO."+inspect.stack()[1][3]+"()")


def setup(channel, direction, initial=False):
    showwarning()
    print("Setup pin " + str(channel) + " as " + str(direction))


def cleanup(channel=False):
    showwarning()
    print('Cleanup GPIO pins')


def setmode(mode='BOARD'):
    global __mode
    allowed_values = ['BOARD', 'BCM']
    if mode in allowed_values:
        __mode = mode
    else:
        print("Unknown numbering mode " + mode)
        exit(1)
    print("Mode set to: " + str(mode))


def input(pin):
    showwarning()
    with open('door_input_mock', 'r') as f:
        out = int(str(f.read()).strip())
    # out = randint(0,1)
    # sleep(10)
    # print("Input pin: " + str(a) + " value: " + str(rand_out))
    return out


def output(a, b):
    showwarning()
    print("Set pin " + str(a) + " to " + str(b))


def setwarnings(flag):
    global __warnings
    __warnings = flag


# if __name__ == "__main__":
#     out = input(18)
#     print(out)