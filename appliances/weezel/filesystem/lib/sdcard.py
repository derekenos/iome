
from machine import SDCard
from os import mount
from utime import sleep


SDCARD_MOUNTED = False


def mount_sdcard(slot_num, mount_point):
    global SDCARD_MOUNTED
    sdcard = SDCard(slot=slot_num)
    tries_remaining = 10
    while tries_remaining:
        try:
            mount(sdcard, mount_point)
        except OSError as e:
            print('Could not mount SD Card: OSError {}'.format(e))
        else:
            print('Mounted SD Card at: {}'.format(mount_point))
            SDCARD_MOUNTED = True
            break
        tries_remaining -= 1
        if tries_remaining == 0:
            break
        print('Trying again to mount SD Card...')
        sleep(1)
