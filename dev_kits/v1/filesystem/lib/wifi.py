
import machine
import network
import binascii
import time

import config


UNIQUE_ID = binascii.hexlify(machine.unique_id()).decode('ascii')


def connect_to_access_point(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.active() or not wlan.isconnected():
        wlan.active(True)
        wlan.config(dhcp_hostname=config.get('DHCP_HOSTNAME').format(
            UNIQUE_ID=UNIQUE_ID))
        print('connecting to:', ssid)
        wlan.connect(ssid, password)
        wait_seconds_remaining = config.get('WLAN_CONNECT_WAIT_SECONDS')
        while not wlan.isconnected() and wait_seconds_remaining:
            time.sleep(1)
            wait_seconds_remaining -= 1

    print('network config:', wlan.ifconfig())


def create_access_point():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=config.get('WIFI_ACCESS_POINT_SSID').format(
        UNIQUE_ID=UNIQUE_ID))
    ap.active(True)
    return ap
