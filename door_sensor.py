import logging
import asyncio
from sechome_conf import HOST


if HOST == 'pi':
    import RPi.GPIO as gpio
else:
    import mock_gpio as gpio
    gpio.setwarnings(False)


def setup_gpio(pin):
    gpio.setmode(gpio.BOARD)
    gpio.setup(pin, gpio.IN)

def cleanup_gpio():
    gpio.cleanup()

# 0 == open, 1 == closed
def is_door_open(pin):
    return gpio.input(pin) == 0

async def read_door_sensor(pin=18, interval=1):
    setup_gpio(pin)
    door_state = is_door_open(pin)
    print("initial door state: {}".format(door_state))
    yield door_state
    try:
        while True:
            await asyncio.sleep(interval)
            new_door_state = is_door_open(pin)

            if door_state == new_door_state:
                continue
            else:
                door_state = new_door_state
                yield door_state
    finally:
        cleanup_gpio()
