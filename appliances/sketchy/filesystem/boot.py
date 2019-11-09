
import webrepl
from machine import reset
from micropython import alloc_emergency_exception_buf

import config
from lib.wifi import connect_to_access_point
from lib.sdcard import mount_sdcard
from lib.wifi import create_access_point


alloc_emergency_exception_buf(100)


if config.get('WIFI_STATION_CONNECT_ON_BOOT'):
    connect_to_access_point(
        config.get('WIFI_STATION_SSID'),
        config.get('WIFI_STATION_PASSWORD')
    )

if config.get('WIFI_CREATE_ACCESS_POINT_ON_BOOT'):
    create_access_point()

if config.get('WEBREPL_START_ON_BOOT'):
    webrepl.start()

if config.get('SD_CARD_MOUNT_ON_BOOT'):
    mount_sdcard(
        slot_num=config.get('SD_CARD_SLOT'),
        mount_point=config.get('SD_CARD_MOUNT_POINT')
    )
