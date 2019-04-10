import pickle
import base64
import pycron
import configparser
import itertools
from datetime import datetime
from asyncio import Queue, QueueFull, sleep
from log import logger
from email_client import send_email


# module globals
notif_queue = None

def read_arm_config(armed_file="armed.ini"):
    ''' returns cartesian product of (armed, disarmed) cron expressions
    '''
    config = configparser.ConfigParser()
    config.read(armed_file)
    armed_crons = [config['armed'][key] for key in config['armed']]
    disarmed_crons = [config['disarmed'][key] for key in config['disarmed']]
    return [cron_pairs for cron_pairs in itertools.product(armed_crons, disarmed_crons)]

def matches_cron(armed, disarmed, dt:datetime):
    return pycron.is_now(armed, dt) and not pycron.is_now(disarmed, dt)

def check_armed(dt:datetime, cron_pairs:list):
    return any([matches_cron(armed, disarmed, dt) for armed,disarmed in cron_pairs])

def is_system_armed(dt:datetime, armed_file="armed.ini"):
    cron_pairs = read_arm_config(armed_file)
    return check_armed(dt, cron_pairs)

def schedule_notification(message):
    global notif_queue
    try:
        logger.info("Put notification into queue, current notif count: " + str(notif_queue.qsize()))
        notif_queue.put_nowait(message)
    except QueueFull:
        logger.warn("Cannot schedule more than " + notif_queue.maxsize + "notifications. Queue is full!")

async def notify_user():
    """ sends email to notify user of event
    """
    global notif_queue
    while True:
        logger.info("Get notification from queue, current notif count: " + str(notif_queue.qsize()))
        notif = await notif_queue.get()
        send_email('some@gmail.com', decode_gmail_pass("gmail_pass.b") , notif)

def decode_gmail_pass(filename:str) -> str:
    decode = lambda encoded: base64.b64decode(encoded).decode('utf-8')
    with open(filename, "rb") as f:
        return decode(pickle.load(f))

def setup_notif_queue(notifications):
    global notif_queue
    notif_queue = notifications
    return notif_queue

# if __name__ == "__main__":
#     pairs = read_arm_config()
#     now = datetime(2019, 4, 7, 2, 1)
#     print(str(now) + " month: " + now.strftime("%B"))
#     armed = check_armed(now, pairs)
#     print(armed)

