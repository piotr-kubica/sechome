import asyncio
import logging
from collections import namedtuple
from log import logger

WifiDevices = namedtuple('WifiDevices', 'active, left, joined')

# module globals
wifi_devices = {
    '18:31:BB:53:A2:B4': {'name':'router5'    , 'inmate': False},
    '18:31:BA:5C:A1:B0': {'name':'router24'   , 'inmate': False},
    '90:26:24:E9:A2:AF': {'name':'galaxy-a5'  , 'inmate': False}
}

active_devices = None
scan_consecutive_timeouts = 0

async def nmap_scan_wifi():
    nmap_command = 'sudo nmap -sP -n 192.168.1.1/24'
    proc = await asyncio.create_subprocess_exec(*(nmap_command.split()), 
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await proc.communicate()
    out, err = stdout.decode('utf-8'), stderr.decode('utf-8')
    if proc.returncode != 0:
        logger.error('Failed to run nmap. STDOUT: {} \n STDERR: {}'.format(out, err))
    return out

def filter_macs(nmap_output):
    return [line.split()[2] for line in nmap_output.split('\n') if line.startswith('MAC Address:')]
            
def device_names(mac_list, wifi_devices):
    names = set()
    for mac in mac_list:
        device = wifi_devices.get(mac.upper())
        if not device:
            logger.critical("Unknown device MAC: {} has accessed network".format(mac))
        else: 
            names.add(device['name'])
    return names

async def find_active_devices(wifi_devices, scan_timeout_sec=30):
    global scan_consecutive_timeouts
    try:
        nmap_out = await asyncio.wait_for(nmap_scan_wifi(), scan_timeout_sec)
        scan_consecutive_timeouts = 0
        # print(nmap_out)
    except asyncio.TimeoutError:
        scan_consecutive_timeouts += 1
        logger.warning('Nmap scan timeout! Consecutive timeouts: {}'.format(scan_consecutive_timeouts))
        return set()
    macs = filter_macs(nmap_out)
    print(macs)
    names = device_names(macs, wifi_devices)
    print(names)
    return names

def devices_change(existing, found):
    joined = found - existing
    left = existing - found
    print('left: {}, joined: {}'.format(left, joined))
    return WifiDevices(found, left, joined)

async def track_device_changes(wifi_devices):
    global active_devices
    found_devices = await find_active_devices(wifi_devices)
    if active_devices is None:
        active_devices = found_devices
    
    change = devices_change(active_devices, found_devices)
    active_devices = found_devices
    return change
