import asyncio
import logging
import os
from log import logger


def get_uploader_path(host='pi'):
    if host == 'pi':
        return '/home/pi/Dropbox-Uploader/dropbox_uploader.sh'
    else:
        return '/home/pio/projects/Dropbox-Uploader/dropbox_uploader.sh'

async def do_upload(upload_command):
    print('Trying to upload with command: {}'.format(upload_command))
    proc = await asyncio.create_subprocess_exec(*upload_command, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()
    out = stdout.decode('utf-8')
    if proc.returncode not in (None, 0):
        error_msg = 'Failed to upload logs. Return code {}'
        logger.error(error_msg.format(proc.returncode))
    else:
        print('Upload completed! Return code {}'.format(proc.returncode))
    print('Output: {}'.format(out))
    return out

# TODO future: download armed, disarmed
# async def do_download(download_command):
#     pass

async def upload_log(log_filename, uploader_path, logs_path='/logs', upload_timeout_sec=60):
    upload_command = (uploader_path, 'upload', log_filename, logs_path)
    if not os.path.isfile(log_filename):
        logger.warning("File to upload {} could not be found".format(log_filename))
    else:
        try: 
            await asyncio.wait_for(do_upload(upload_command), upload_timeout_sec)
            return True
        except asyncio.TimeoutError:
            logger.warning('Upload timeout!')
            return False