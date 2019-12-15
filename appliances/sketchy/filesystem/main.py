
import json
import machine
import math
from collections import deque
from machine import (
    Pin,
    Timer,
)
from utime import (
    sleep_ms,
    sleep_us,
)

from fonts import char_def_to_points
from fonts.default import CHARS

from lib.femtoweb import default_http_endpoints
from lib.femtoweb.server import (
    _200,
    _400,
    GET,
    POST,
    as_choice,
    as_json,
    as_maybe,
    as_type,
    as_websocket,
    as_with_default,
    route,
    send,
    serve,
)


###############################################################################
# Exceptions
###############################################################################

class OutOfBounds(Exception): pass


###############################################################################
# Stepper Motor Control
###############################################################################

X_AXIS = 'x'
Y_AXIS = 'y'
X_AXIS_MAX = 880
Y_AXIS_MAX = 680
DIR_UP = 'up'
DIR_DOWN = 'down'
DIR_LEFT = 'left'
DIR_RIGHT = 'right'

DIR_BACKLASH_STEPS_MAP = {
    DIR_UP: 14,
    DIR_DOWN: 14,
    DIR_LEFT: 14,
    DIR_RIGHT: 14,
}

STEPPER_NOT_ENABLE_PIN = Pin(0, Pin.OUT)
STEPPER_NOT_ENABLE_PIN.value(1)

STEPPER_X_STEP_PIN = Pin(4, Pin.OUT)
STEPPER_X_STEP_PIN.value(0)

STEPPER_X_DIR_PIN = Pin(2, Pin.OUT)
STEPPER_X_DIR_PIN.value(1)

STEPPER_Y_STEP_PIN = Pin(15, Pin.OUT)
STEPPER_Y_STEP_PIN.value(0)

STEPPER_Y_DIR_PIN = Pin(13, Pin.OUT)
STEPPER_Y_DIR_PIN.value(1)


x_pos = 0
y_pos = 0


enable_steppers = lambda: STEPPER_NOT_ENABLE_PIN.value(0)
disable_steppers = lambda: STEPPER_NOT_ENABLE_PIN.value(1)


# Keep track of the last step direction for each axis so that we can compensate
# for the backlash when the direction changes.
axis_last_step_dir_map = {
    X_AXIS: DIR_LEFT,
    Y_AXIS: DIR_DOWN,
}


def pulse_step_pin(step_pin):
    step_pin.value(1)
    sleep_us(1)
    step_pin.value(0)
    sleep_us(1)


def step(axis, direction):
    global x_pos
    global y_pos
    if axis == X_AXIS:
        if direction == DIR_LEFT:
            if x_pos == 0:
                return False
            x_pos -= 1
        elif direction == DIR_RIGHT:
            if x_pos == X_AXIS_MAX:
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
            if y_pos == Y_AXIS_MAX:
                return False
            y_pos += 1
        step_pin = STEPPER_Y_STEP_PIN
        dir_pin = STEPPER_Y_DIR_PIN

    dir_pin(0 if direction in (DIR_DOWN, DIR_LEFT) else 1)

    # If the current direction is the opposite of the last axis step, step
    # through the backlash.
    if direction != axis_last_step_dir_map[axis]:
        num_backlash_steps = DIR_BACKLASH_STEPS_MAP[direction]
        while num_backlash_steps:
            pulse_step_pin(step_pin)
            sleep_ms(3)
            num_backlash_steps -= 1
        axis_last_step_dir_map[axis] = direction

    pulse_step_pin(step_pin)
    return True


def multi_step(axis, direction, num_steps):
    enable_steppers()
    while num_steps:
        step(axis, direction)
        sleep_ms(3)
        num_steps -= 1
    disable_steppers()


is_moving_to_point = False

def move_to_point(x, y):
    global x_pos
    global y_pos
    global is_moving_to_point

    if x > X_AXIS_MAX or y > Y_AXIS_MAX:
        raise OutOfBounds('x,y max is {},{}, got {},{}'.format(
            X_AXIS_MAX, Y_AXIS_MAX, x, y))

    # Discard any specified fractional component and calculate deltas.
    x = math.floor(x)
    y = math.floor(y)
    x_delta = x - x_pos
    y_delta = y - y_pos

    # Plan a linear path.
    max_delta = max(abs(x_delta), abs(y_delta))
    if max_delta == 0:
        return
    x_acc_step_size = x_delta / max_delta
    y_acc_step_size = y_delta / max_delta
    x_acc = 0
    y_acc = 0

    enable_steppers()
    while x_pos != x or y_pos != y:
        is_moving_to_point = True

        if x_acc_step_size != 0 and x_pos != x:
            last_x_acc = x_acc
            x_acc += x_acc_step_size
            if math.floor(x_acc) != math.floor(last_x_acc):
                if x_acc_step_size < 0:
                    step(X_AXIS, DIR_LEFT)
                elif x_acc_step_size > 0:
                    step(X_AXIS, DIR_RIGHT)

        if y_acc_step_size != 0 and y_pos != y:
            last_y_acc = y_acc
            y_acc += y_acc_step_size
            if math.floor(y_acc) != math.floor(last_y_acc):
                if y_acc_step_size < 0:
                    step(Y_AXIS, DIR_DOWN)
                elif y_acc_step_size > 0:
                    step(Y_AXIS, DIR_UP)

        sleep_ms(3)
    is_moving_to_point = False
    disable_steppers()


def move_to_points(points):
    """Move along a sequence of points.
    """
    for x, y in points:
        move_to_point(x, y)


###############################################################################
# Text Drawing Functions
###############################################################################

def draw_text(text, char_height, char_spacing=None, word_spacing=None,
              x_offset=None, y_offset=None):
    """
    """
    # TODO: check whether plotting text will exceed width before starting
    # TODO: add line wrapping

    # If not specified, set char_spacing and word_spacing relative to
    # char_height.
    if char_spacing is None:
        char_spacing = math.floor(char_height / 8)
    if word_spacing is None:
        word_spacing = char_spacing * 4

    # Use the current x/y position if unspecified.
    if x_offset is None:
        x_offset = x_pos
    if y_offset is None:
        y_offset = y_pos

    # Iterate through the characters in text, drawing each and incrementing the
    # x_offset.
    for char in text:
        # Handle SPACE and unsupported chars by advancing the x position by
        # word_spacing number of steps.
        if char == ' ' or char not in CHARS:
            multi_step(X_AXIS, DIR_RIGHT, word_spacing)
            x_offset += word_spacing
            continue

        points = list(char_def_to_points(CHARS[char]))

        # Calculate the scale.
        max_y = max(y for _, y in points)
        scale = math.ceil(char_height / (max_y + 1))

        # Add a sprue directly below the character entry point.
        sprue_coord = points[0]
        # Move all the points up one to make room for the sprue.
        points = [(x, y + 1) for x, y in points]
        points = [sprue_coord] + points + [sprue_coord]

        # Apply the scaling.
        points = [(x * scale, y * scale) for x, y in points]

        # Calc the next x_offset.
        next_x_offset = max(x for x, _ in points) + char_spacing

        # Apply offset.
        points = [(x + x_offset, y + y_offset) for x, y in points]

        move_to_points(points)

        x_offset += next_x_offset



###############################################################################
# SVG Parser
###############################################################################

def render_svg(fh):
    # TODO - move import to top of module.
    # Install xmltok if necessary.
    try:
        import xmltok
    except ImportError:
        import upip
        upip.install('xmltok')
    import re

    width = None
    width_unit = None
    height = None
    height_unit = None
    scale = None

    NUMBER_UNIT_REGEX = re.compile('^(\d+)(.*)$')
    parse_number_unit = lambda s: NUMBER_UNIT_REGEX.match(s)

    FLOAT_RE_PATTERN = '\-?\d+(?:\.\d+)?'
    PATH_COORD_REGEX = re.compile('({0}),({0})'.format(FLOAT_RE_PATTERN))

    TRANSLATE_REGEX = re.compile(
        'translate\(({0}),({0})\)'.format(FLOAT_RE_PATTERN)
    )

    g_translates = []
    translate = (0, 0)
    open_tags = []
    first_path_point = None
    relative_reference = (0, 0)

    for token in xmltok.tokenize(fh):
        if token[0] == 'START_TAG':
            tag = token[1][1]
            open_tags.append(tag)
            if tag == 'g':
                g_translates.append((0, 0))
            elif tag == 'path':
                first_path_point = None

        elif token[0] == 'END_TAG':
            tag = token[1][1]
            open_tags.pop()
            if tag == 'g':
                x, y = g_translates.pop()
                translate = translate[0] - x, translate[1] - y

        if token[0] != 'ATTR':
            continue
        (_, k), v = token[1:]

        if k == 'height':
            match = parse_number_unit(v)
            height = float(match.group(1))
            height_unit = match.group(2)

        elif k == 'width':
            match = parse_number_unit(v)
            width = float(match.group(1))
            width_unit = match.group(2)

        elif k == 'transform' and open_tags[-1] == 'g':
            match = TRANSLATE_REGEX.match(v)
            if match:
                x = float(match.group(1))
                y = float(match.group(2))
                g_translates[-1] = x, y
                translate = translate[0] + x, translate[1] + y

        elif k == 'd':
            if not width or not height:
                raise AssertionError(
                    'about to parse path but height and/or width not '
                    'set: {}/{}'.format(width, height))
            elif width_unit != height_unit:
                raise AssertionError('Different width/height units: {}/{}'
                                     .format(width_unit, height_unit))
            elif scale is None:
                scale = math.floor(max(X_AXIS_MAX, Y_AXIS_MAX) / max(width, height))

            is_relative = False
            for s in v.split():
                match = PATH_COORD_REGEX.match(s)
                if not match:
                    if s != 'z':
                        is_relative = s.islower()
                        continue
                    else:
                        # Close the path.
                        is_relative = False
                        relative_reference = (0, 0)
                        x, y = first_path_point
                else:
                    x = math.floor(float(match.group(1)))
                    y = math.floor(float(match.group(2)))

                if first_path_point is None:
                    first_path_point = (x, y)

                if is_relative:
                    rel_x, rel_y = relative_reference
                    x += rel_x
                    y += rel_y

                # Set the current point as the relative reference if not
                # closing the path.
                if s != 'z':
                    relative_reference = x, y

                # Apply the current cumulative translations.
                x += math.floor(translate[0])
                y += math.floor(translate[1])
                # Invert the y axis.
                move_to_point(x, Y_AXIS_MAX - y)


###############################################################################
# Route Handlers
###############################################################################

@route('/_reset', methods=(GET, POST))
def _reset(request):
    """Reset the device.
    """
    # Manually send the response prior to calling machine.reset
    send(request.connection, _200())
    machine.reset()


@route('/status', methods=(GET,))
@as_json
def _status(request):
    data = {
        'max_position': {
            'x': X_AXIS_MAX,
            'y': Y_AXIS_MAX
        },
        'current_position': {
            'x': x_pos,
            'y': y_pos
        },
    }
    return _200(body=data)


@route('/', methods=(GET,))
def index(request):
    return default_http_endpoints._fs_GET('/public/index.html')


@route('/demo', methods=(GET,))
def _demo(request):
    draw_text('SKETCHY FOR LIFE', char_height=64, x_offset=0, y_offset=300)
    return _200()


@route('/write', methods=(GET,), query_param_parser_map={
    'text': as_type(str),
    'char_height': as_with_default(as_type(float), 10),
    'char_spacing': as_with_default(as_type(int), 10),
    'word_spacing': as_with_default(as_type(int), 40),
    'x_offset': as_maybe(as_type(int)),
    'y_offset': as_maybe(as_type(int)),
})
def _write(request, text, char_height, char_spacing, word_spacing, x_offset,
           y_offset):
    draw_text(text, char_height, char_spacing, word_spacing, x_offset,
              y_offset)
    return _200()


@route('/move_to_point', methods=(GET,), query_param_parser_map={
    'x': as_type(int),
    'y': as_type(int),
})
def _move_to_point(request, x, y):
    move_to_point(x, y)
    return _200()


@route('/multi_step', methods=(GET,), query_param_parser_map={
    'axis': as_choice(X_AXIS, Y_AXIS),
    'direction': as_choice(DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT),
    'num_steps': as_type(int),
})
def _multi_step(request, axis, direction, num_steps):
    multi_step(axis, direction, num_steps)
    return _200()


_draw_dq = deque((), 512)
@route('/draw', methods=(GET,))
@as_websocket
def _draw(request, ws):
    def callback(timer):
        global _draw_dq
        payload_len = ws.read(1)
        if payload_len is not None:
            x, y = map(int, json.loads(ws.read(int(payload_len))))
            _draw_dq.append((x, y))

        if not is_moving_to_point and _draw_dq:
            x, y = _draw_dq.popleft()
            move_to_point(x, y)

        timer.init(period=20, mode=Timer.ONE_SHOT, callback=callback)
    callback(Timer(-1))


@route('/home', methods=(GET,))
def _home(request):
    """Force it to the home position by setting x_pos and y_pos to their max
    values, moving to point 0,0, and then back up 20 steps to reach the usable
    region.
    """
    global x_pos
    global y_pos
    x_pos = X_AXIS_MAX
    y_pos = Y_AXIS_MAX
    move_to_point(0, 0)
    move_to_point(20, 20)
    x_pos = 0
    y_pos = 0
    return _200()


@route('/demo_svg', methods=(GET,), query_param_parser_map={
    'filename': as_type(str)
})
def _demo_svg(request, filename):
    fh = open(filename, 'r')
    render_svg(fh)
    return _200()


if __name__ == '__main__':
    serve()
