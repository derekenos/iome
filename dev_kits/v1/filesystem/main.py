
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
# I/O Configuration and Polling
###############################################################################

def get_adc_pin(pin_num):
    adc = ADC(Pin(pin_num))
    adc.atten(ADC.ATTN_11DB)
    return adc


def get_button_pin(pin_num):
    return Pin(pin_num, Pin.IN, Pin.PULL_UP)


CONTROLLER_1_KNOB_PIN = get_adc_pin(32)
CONTROLLER_1_SYSTEM_BUTTON_PIN = get_button_pin(27)
CONTROLLER_1_KNOB_BUTTON_PIN = get_button_pin(14)


_last_inputs = [
    0,
    0,
    0,
    0,
]


def read_inputs():
    global _last_inputs
    inputs = [
        CONTROLLER_1_KNOB_PIN.read() >> 3,

        (CONTROLLER_1_SYSTEM_BUTTON_PIN.value() ^ 1) |
        CONTROLLER_1_KNOB_BUTTON_PIN.value() << 1,

        0,
        0
    ]
    updated = inputs != _last_inputs
    _last_inputs = inputs
    return updated, inputs



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
