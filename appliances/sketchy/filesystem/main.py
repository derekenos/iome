
import machine
import math
from machine import Pin
from utime import (
    sleep_ms,
    sleep_us,
)

from lib.femtoweb import default_http_endpoints
from lib.femtoweb.server import (
    _200,
    _400,
    GET,
    POST,
    as_choice,
    as_json,
    as_type,
    route,
    send,
    serve,
)


###############################################################################
# Stepper Motor Control
###############################################################################

X = 'x'
Y = 'y'
DIR_UP = 'up'
DIR_DOWN = 'down'
DIR_LEFT = 'left'
DIR_RIGHT = 'right'
X_MAX = 880
Y_MAX = 680

CHARS = {
    'S': [
        (0, 0), (0, 1), (1, 1), (1, 2), (0, 2), (0, 5), (2, 5), (2, 4),
        (1, 4), (1, 3), (2, 3), (2, 0), (0, 0), (2, 0)
    ],
    'K': [
        (0, 0), (0, 5), (1, 5), (1, 3), (2, 4), (2, 5), (3, 5), (3, 4), (1, 2),
        (3, 1), (3, 0), (2, 0), (1, 1), (1, 0), (0, 0), (3, 0)
    ],
    'E': [
        (0, 0), (0, 5), (2, 5), (2, 4), (1, 4), (1, 3), (2, 3), (2, 2), (1, 2),
        (1, 1), (2, 1), (2, 0), (0, 0), (2, 0)
    ],
    'T': [
        (1, 0), (1, 4), (0, 4), (0, 5), (3, 5), (3, 4), (2, 4), (2, 0), (1, 0),
        (3, 0)
    ],
    'C': [
        (0, 0), (0, 5), (2, 5), (2, 4), (1, 4), (1, 1), (2, 1), (2, 0), (0, 0),
        (2, 0)
    ],
    'H': [
        (0, 0), (0, 5), (1, 5), (1, 3), (2, 3), (2, 5), (3, 5), (3, 0), (2, 0),
        (2, 2), (1, 2), (1, 0), (0, 0), (1, 0), (1, 2), (2, 2), (2, 0)
    ],
    'Y': [
        (2, 0), (2, 3), (0, 4), (0, 5), (1, 5), (2, 4), (2, 5), (3, 5), (3, 0),
        (2, 0), (3, 0)
    ],
}


STEPPER_NOT_ENABLE_PIN = Pin(13, Pin.OUT)
STEPPER_NOT_ENABLE_PIN.value(1)

STEPPER_X_STEP_PIN = Pin(15, Pin.OUT)
STEPPER_X_STEP_PIN.value(0)

STEPPER_X_DIR_PIN = Pin(2, Pin.OUT)
STEPPER_X_DIR_PIN.value(1)

STEPPER_Y_STEP_PIN = Pin(4, Pin.OUT)
STEPPER_Y_STEP_PIN.value(0)

STEPPER_Y_DIR_PIN = Pin(0, Pin.OUT)
STEPPER_Y_DIR_PIN.value(1)


x_pos = 0
y_pos = 0


enable_steppers = lambda: STEPPER_NOT_ENABLE_PIN.value(0)
disable_steppers = lambda: STEPPER_NOT_ENABLE_PIN.value(1)


def draw_character(char, scale=25):
    for x, y in char:
        x = x * scale
        y = y * scale
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
        step_pin = STEPPER_X_STEP_PIN
        dir_pin = STEPPER_X_DIR_PIN
    else:
        if direction == DIR_DOWN:
            if y_pos == 0:
                return False
            y_pos -= 1
        elif direction == DIR_UP:
            if y_pos == Y_MAX:
                return False
            y_pos += 1
        step_pin = STEPPER_Y_STEP_PIN
        dir_pin = STEPPER_Y_DIR_PIN

    dir_pin(0 if direction in (DIR_DOWN, DIR_LEFT) else 1)
    step_pin.value(1)
    sleep_us(1)
    step_pin.value(0)
    sleep_us(1)
    return True


def multi_step(axis, direction, num_steps):
    enable_steppers()
    while num_steps:
        step(axis, direction)
        sleep_ms(3)
        num_steps -= 1
    disable_steppers()


def move_to_point(x, y):
    global x_pos
    global y_pos

    if x > X_MAX or y > Y_MAX:
        raise AssertionError('x,y max is {},{}, got {},{}'.format(
            X_MAX, Y_MAX, x, y))

    # Discard any specified fractional component and calculate deltas.
    x_delta = math.floor(x) - x_pos
    y_delta = math.floor(y) - y_pos

    # Plan a linear path.
    max_delta = max(abs(x_delta), abs(y_delta))
    x_step_size = x_delta / max_delta
    y_step_size = y_delta / max_delta
    x_pos_acc = x_pos
    y_pos_acc = y_pos

    enable_steppers()
    while x_pos != x and y_pos != y:
        x_pos_acc += x_step_size
        y_pos_acc += y_step_size
        x_pos_acc_floor = math.floor(x_pos_acc)
        y_pos_acc_floor = math.floor(y_pos_acc)

        if x_pos_acc_floor != x_pos:
            if x_pos_acc_floor < x_pos:
                step(X, DIR_LEFT)
            elif x_pos_acc_floor > x_pos:
                step(X, DIR_RIGHT)

        if y_pos_acc_floor != y_pos:
            if y_pos_acc_floor < y_pos:
                step(Y, DIR_DOWN)
            elif y_pos_acc_floor > y_pos:
                step(Y, DIR_UP)

        sleep_ms(3)
    disable_steppers()


###############################################################################
# Route Handlers
###############################################################################

@route('/demo', methods=(GET,))
def _demo(request):
    scale = int(request.query.get('scale', 25))
    x_offset = 0
    for c in 'SKETCHY':
        coords = CHARS[c]
        draw_character([(x + x_offset, y) for x, y in coords], scale)
        x_offset += max(x for x, _ in coords) + 1
    return _200()


@route('/move_to_point', methods=(GET,), query_param_parser_map={
    'x': as_type(int),
    'y': as_type(int),
})
def _move_to_point(request, x, y):
    move_to_point(x, y)
    return _200()


@route('/multi_step', methods=(GET,), query_param_parser_map={
    'axis': as_choice(X, Y),
    'direction': as_choice(DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT),
    'num_steps': as_type(int),
})
def _multi_step(request, axis, direction, num_steps):
    multi_step(axis, direction, num_steps)
    return _200()


@route('/status', methods=(GET,))
@as_json
def _status(request):
    data = {
        'max_position': {
            'x': X_MAX,
            'y': Y_MAX
        },
        'current_position': {
            'x': x_pos,
            'y': y_pos
        },
    }
    return _200(body=data)


@route('/_reset', methods=(GET, POST))
def _reset(request):
    """Reset the device.
    """
    # Manually send the response prior to calling machine.reset
    send(request.connection, _200())
    machine.reset()


@route('/', methods=(GET,))
def index(request):
    return default_http_endpoints._fs_GET('/public/index.html')


if __name__ == '__main__':
    serve()
