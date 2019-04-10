import sys
import os
import asyncio
from sechome_conf import HOST
from datetime import datetime as dt
from wifi_scanner import track_device_changes, wifi_devices
from door_sensor import read_door_sensor
from dropbox_uploader import upload_log, get_uploader_path
from log import logger, get_log_filename, get_base_log_filename
from notifier import is_system_armed, schedule_notification, notify_user, setup_notif_queue


def check_system_version_36():
    ver = sys.version_info
    if ver.major < 3 or (ver.major == 3 and ver.minor < 6):
        sys.exit("\nPython 3.6 required\n")

async def track_wlan_devices():
    while True:
        changes = await track_device_changes(wifi_devices)
        if (len(changes.joined) != 0 or len(changes.left) != 0):
            logger.info(changes)
        await asyncio.sleep(60 * 2) # 2 mins

async def track_door_sensor():
    ''' continously track door sensor
        used async generator, see https://www.python.org/dev/peps/pep-0525/
    '''
    async for i in read_door_sensor():
        door_change_msg = "Door state changed to: " + ("open" if i else "closed")
        logger.warning(door_change_msg)
        change_dt = dt.now()
        if is_system_armed(change_dt):
            logger.critical("System is armed and door state changed!")
            schedule_notification(door_change_msg + " at " + change_dt.strftime("%Y-%m-%d %H:%M:%S"))

async def upload_logs_to_dropbox(uploader_path, upload_interval=60):
    uploaded_logs = set()
    upload_consecutive_timeouts = 0

    async def try_upload(log_filename, uploader_path):
        nonlocal upload_consecutive_timeouts
        uploaded = await upload_log(log_filename, uploader_path)
        if not uploaded:
            upload_consecutive_timeouts += 1
            logger.warning('Upload timeout! Consecutive timeouts {}'.format(upload_consecutive_timeouts))
            return False
        else:
            upload_consecutive_timeouts = 0
            return True

    while True:
        # always upload base log
        await try_upload(get_base_log_filename(), uploader_path)
        
        # upload rotated logs only once
        log_filename = get_log_filename()
        if log_filename not in uploaded_logs:
            success = await try_upload(log_filename, uploader_path)
            if success:
                uploaded_logs.add(log_filename)
        
        await asyncio.sleep(upload_interval)


if __name__ == "__main__":
    check_system_version_36()
    
    logger.info('Started sechome on {} host'.format(HOST))
    uploader_path = get_uploader_path(HOST)

    # setup the event loop
    asyncio.set_event_loop(asyncio.new_event_loop())
    event_loop = asyncio.get_event_loop()

    setup_notif_queue(asyncio.Queue(loop=event_loop))

    asyncio.ensure_future(track_wlan_devices(), loop=event_loop)
    asyncio.ensure_future(track_door_sensor(), loop=event_loop)
    asyncio.ensure_future(notify_user(), loop=event_loop)
    asyncio.ensure_future(upload_logs_to_dropbox(uploader_path), loop=event_loop)
    
    try:
        event_loop.run_forever()
    finally:
        event_loop.run_until_complete(event_loop.shutdown_asyncgens())
        event_loop.close()
