
import gc
import json
import os
from binascii import hexlify
from uwebsocket import websocket
import machine
from machine import (
    ADC,
    Pin,
    Timer,
)
from utime import (
    sleep_ms,
    sleep_us,
)

import config
from lib.femtoweb import default_http_endpoints
from lib.femtoweb.server import (
    _200,
    GET,
    POST,
    as_json,
    route,
    send,
    serve,
)


###############################################################################
# Stepper Motor Control
###############################################################################

X = 0
Y = 1
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 1
DIR_RIGHT = 0
X_MAX = 680
Y_MAX = 680
X_MIN_USABLE = 40
Y_MIN_USABLE = 40
X_MAX_USABLE = 640
Y_MAX_USABLE = 640

CHARS = [
    [(0, 0), (0, 1), (1, 1), (1, 2), (0, 2), (0, 5), (2, 5), (2, 4), (1, 4),
     (1, 3), (2, 3), (2, 0), (0, 0)],
    [(3, 0), (3, 5), (4, 5), (4, 3), (5, 4), (5, 5), (6, 5), (6, 4), (4, 2),
     (6, 1), (6, 0), (5, 0), (4, 1), (4, 0), (3, 0)],
    [(7, 0), (7, 5), (9, 5), (9, 4), (8, 4), (8, 3), (9, 3), (9, 2), (8, 2),
     (8, 1), (9, 1), (9, 0), (7, 0)],
    [(11, 0), (11, 4), (10, 4), (10, 5), (13, 5), (13, 4), (12, 4), (12, 0),
     (11, 0)],
    [(14, 0), (14, 5), (16, 5), (16, 4), (15, 4), (15, 1), (16, 1), (16, 0),
     (14, 0)],
    [(17, 0), (17, 5), (18, 5), (18, 3), (19, 3), (19, 5), (20, 5), (20, 0),
     (19, 0), (19, 2), (18, 2), (18, 0), (17, 0), (18, 0), (18, 2), (19, 2),
     (19, 0)],
    [(23, 0), (23, 3), (21, 4), (21, 5), (22, 5), (23, 4), (23, 5), (24, 5),
     (24, 0), (23, 0)],
]

Y_not_enable_pin = Pin(25, Pin.OUT)
Y_not_enable_pin.value(0)

Y_not_reset_pin = Pin(26, Pin.OUT)
Y_not_reset_pin.value(1)

Y_dir_pin = Pin(33, Pin.OUT)
Y_dir_pin.value(1)

Y_step_pin = Pin(32, Pin.OUT)
Y_step_pin.value(0)

X_not_enable_pin = Pin(22, Pin.OUT)
X_not_enable_pin.value(0)

X_not_reset_pin = Pin(19, Pin.OUT)
X_not_reset_pin.value(1)

X_dir_pin = Pin(18, Pin.OUT)
X_dir_pin.value(1)

X_step_pin = Pin(23, Pin.OUT)
X_step_pin.value(0)

x_pos = 0
y_pos = 0


def draw_character(char, y_offset=0):
    for x, y in char:
        x = x * 25 + 40
        y = y * 25 + 40 + y_offset
        move_to_point(x, y)


def step(axis, direction):
    global x_pos
    global y_pos
    if axis == X:
        if direction == DIR_LEFT:
            if x_pos == 0:
                return False
            x_pos -= 1
        elif direction == DIR_RIGHT:
            if x_pos == X_MAX:
                return False
            x_pos += 1
        dir_pin = X_dir_pin
        step_pin = X_step_pin
    else:
        if direction == DIR_DOWN:
            if y_pos == 0:
                return False
            y_pos -= 1
        elif direction == DIR_UP:
            if y_pos == Y_MAX:
                return False
            y_pos += 1
        dir_pin = Y_dir_pin
        step_pin = Y_step_pin

    dir_pin.value(direction)
    step_pin.value(1)
    sleep_us(1)
    step_pin.value(0)
    sleep_us(1)
    return True


def step_toward_point(x, y):
    """Maybe step toward the specified point and return a boolean indicating
    whether a step was actually taken.
    """
    if x == x_pos and y == y_pos:
        return False
    if x < x_pos:
        step(X, DIR_LEFT)
    elif x > x_pos:
        step(X, DIR_RIGHT)
    if y < y_pos:
        step(Y, DIR_DOWN)
    elif y > y_pos:
        step(Y, DIR_UP)
    return True


def move_to_point(x, y):
    while step_toward_point(x, y):
        sleep_ms(3)


###############################################################################
# Route Handlers
###############################################################################

@route('/')
def index(request, methods=(GET,)):
    return default_http_endpoints._fs_GET('/public/index.html')


def websocket_server_handshake(request):
    """ Adapated from the websocket_helper.py:
    https://github.com/micropython/webrepl/blob/master/websocket_helper.py
    """
    import hashlib
    import binascii
    webkey = request.headers.get('Sec-WebSocket-Key')
    if not webkey:
        raise OSError("Not a websocket request")
    respkey = bytes(webkey, 'ascii') + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    respkey = hashlib.sha1(respkey).digest()
    respkey = binascii.b2a_base64(respkey)[:-1]
    resp = b"""\
HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: %s\r
\r
""" % respkey
    request.connection.send(resp)


_active_input_conn = None
@route('/input', methods=(GET,))
def input(request):
    global _active_input_conn
    global _input_callback_timer

    if _active_input_conn is not None:
        _active_input_conn.close()

    conn = request.connection
    _active_input_conn = conn

    websocket_server_handshake(request)
    ws = websocket(conn, True)

    def callback(timer):
        updated, inputs = read_inputs()
        # TODO
        # Make only-send-on-updated dependent on whether the game server is
        # acting as an access point. In station mode, always sending regardless
        # of updated state seems to result in more consistent latency - I
        # suspect because the router sees it as a squeaky data wheel, and
        # thusly greases it.
        try:
            ws.write(json.dumps(inputs))
        except:
            conn.close()
            timer.deinit()
            return None

        timer.init(period=20, mode=Timer.ONE_SHOT, callback=callback)
        gc.collect()

    callback(Timer(-1))


@route('/_status', methods=(GET,))
@as_json
def _status(request):
    uname = os.uname()
    data = {
        'MicroPython': {
            'Release': uname.release,
            'version': uname.version,
            'mem_free': gc.mem_free(),
        },
        'Machine': {
            'Unique ID': hexlify(machine.unique_id()),
            'Frequency (Hz)': machine.freq(),
        }
    }

    return _200(body=data)


@route('/_reset', methods=(GET, POST))
def _reset(request):
    """Reset the device.
    """
    # Manually send the response prior to calling machine.reset
    send(request.connection, _200())
    machine.reset()


@route('/_config', methods=(GET,))
@as_json
def _config_GET(request):
    return _200(body=config._config)


@route('.*', methods=(GET,))
def apps(request):
    return default_http_endpoints._fs_GET('/public{}'.format(request.path))


if __name__ == '__main__':
    serve()
