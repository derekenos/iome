# -*- coding: utf-8 -*-

"""Weezel - a CNC add-on toy for the Ikea Mala easel
"""

# Kinematics is the name for how to calculate what we should do to the motors
# to get where we want to go.
#
# In order to do this, we need to know the geometry of how all the physical
# elements are arranged. The version of the Weezel that mounts on the Ikea
# Mala easel using the v2 sled uses an acute trapezoidal geometry.
# See here for more information than you ever wanted to know about trapezoids:
# https://en.wikipedia.org/wiki/Trapezoid
#
# A note about number units: My imperial tape measure gives me the world in
# inches but all in-code calculations are performed in rounded millimeters.
# pfft, "precision" :thumbsdown:
#
# The acute trapazoid that we're dealing with is oriented like this:
#
#                     || upper base
#            _________\/_
#            \          /
# left leg -> \        / <- right leg
#              \      /
#               \____/
#                  /\
#                  || lower base
#
#
# Here's what this looks like on the Ikea Mala easel:
#
# ()                  ()
#  |O________________O|
#   \| |          | |/
#    \ |          | /
#    |\|          |/|
#    | \          / |
#    | |\        /| |
#    | | \      / | |
#    | |  \____/  | |
#    | |  (    )  | |
#    | |          | |
#    | |----------| |
#    | |----------| |
#    | |          | |
#
# Key:
#
#  () - Stepper Motor
#
#   O - Idler Pulley
#
#   _ - Trapezoidal Geometry Base
#
#         -- The upper base is an imaginary horizontal line between the points
#            on the left and right idler pulleys where the belt exits toward
#            the sled
#
#         -- The lower base is the length of belt that is trapped in the sled
#            belt catch
#
#   \ - Trapezoidal Geometry Left Leg (also left stepper motor belt)
#
#   / - Trapezoidal Geometry Right Leg (also right stepper motor belt)
#
#
# The upper and lower base lengths never change, so what we need to calculate
# is how long each the left and right legs needs to be to put the sled where we
# we want it.
#
# Using the v2 sled, the bases have the following values:
#
#  Upper Base: 649 mm (~25 9/16", see below measurement note)
#  Lower Base: 23 mm (dictated by the width of sled belt catch component)
#
# To find the upper base length, I installed the motor mounts on the easel and
# measured the horizontal distance between the points (indicated by
# the "x") on the idler pulleys that is the average location of where the belt
# will exit for the sled across the range of reachable positions:
#
#   ___                               ___
#  /   \                             /   \
# | ( ) |                           | ( ) |
# x\__ /                             \___/x
#
# ^                                       ^
# |_______________ 25 9.16" ______________|
#
#
# As a young lad, I couldn't understand what practical application the geometry
# I was being taught could have in MY life. I cared about industrial music, not
# shapes. As an old man trying to make technology move things in the physical
# world, I've come to appreciate all those shapes. Maybe schools should teach
# geometry as part of the process of designing of physical actuating
# mechanisms. Making things move is so exciting and engaging!
#
# Before we calculate anything, let's consider again what we got:
#            ____________
#            \          /
#             \        /
#              \      /
#               \____/
#
# That looks nice. To assist in our calculations, let's create two right
# triangles by drawing verticals lines from the limits of the lower base to the
# upper:
#            ____________
#            \   |  |   /
#             \  |  |  /
#              \ |  | /
#               \|__|/
#
# Most of the dimensions here are known:
#
#
# desired -> ______   || upper base length
# x axis     _________\/_
# position   \   |  |   /
#             \  |  |<----- desired Y axis position
#              \ |  | /
#               \|__|/
#                 /\
#                 || lower base length
#
# Here are the things we need to calculate:
#
#            ____________
#            \   |  |   /
# left leg -> \  |  |  / <- right leg
# length       \ |  | /     length
#               \|__|/
#
# Thanks to Pythagoras, we know that the sides of a right triangle have the
# following property: a² + b² = c²
#
# where:
#              b
#            ____
#            \   |
#             \  | a
#           c  \ |
#               \|
#
# This is a good time to mention how the sled geometry related this these
# triangles. Here's where the sled and its writing implement are located:
#            ____________
#            \   |  |   /
#             \  |  |  /
#              \ |  | /
#               \|__|/
#             __/    \__ <- sled belt catch
#            \          /
#             \  (  )<----- writing implement
#              `.    .`
#                `..`
#
# What we really want to do is calculate the position of the writing implement,
# which has a fixed x/y offset from either end of the lower trapezoidal base.
# These values are known from the sled geometry and are as follows:
#
#  X Offset: 11.5 mm
#  Y Offset: ~20 mm (depends on the thickness of the chalk / pen / etc.)
#
# We'll do the actual calculation in the function called calc_legs()
#
#
# Converting linear distance to stepper motor steps:
#
# The stepper motor that we're using has a step angle of 1.8 degrees, which
# comes out to 200 steps / revolution.
# https://www.amazon.com/gp/product/B00PNEQI7W
#
# The GT2 belt pulley that we're using has an inner diameter of 12mm, which
# gives us a circumference of 2 * PI * 12 / 2 = 37.7mm
# They're ones that come with this:
# https://www.amazon.com/gp/product/B0776KXY8G
#
# So each 1.8 degree stepper motor step extends or retracts the belt by
# 37.7mm / 200 = 0.1885mm


import json
import machine
import math
import os
import time
from collections import deque
from machine import (
    Pin,
    PWM,
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
    PUT,
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

from lib._os import path
from lib import gcode


###############################################################################
# Exceptions
###############################################################################

class OutOfBounds(Exception): pass


###############################################################################
# Geometric Constants
###############################################################################

UPPER_BASE_LENGTH_MM = 649
LOWER_BASE_LENGTH_MM = 23
SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM = 11.5
SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM = 20

# Values to compensate for the unusable area within the trapazoid.
UPPER_BASE_ENDPOINT_FRAME_VERTICAL_OFFSET_MM = 18.5
UPPER_BASE_ENDPOINT_FRAME_HORIZONTAL_OFFSET_MM = 14.3
EASEL_FRAME_WIDTH_MM = 40
SLED_EDGE_IMPLEMENT_TOP_OFFSET_MM = 28
SLED_EDGE_IMPLEMENT_HORIZONTAL_OFFSET_MM = 54
TOP_KEEPOUT_MM = (UPPER_BASE_ENDPOINT_FRAME_VERTICAL_OFFSET_MM +
                  EASEL_FRAME_WIDTH_MM +
                  SLED_EDGE_IMPLEMENT_TOP_OFFSET_MM)
SIDE_KEEPOUT_MM = (UPPER_BASE_ENDPOINT_FRAME_HORIZONTAL_OFFSET_MM +
                   EASEL_FRAME_WIDTH_MM +
                   SLED_EDGE_IMPLEMENT_HORIZONTAL_OFFSET_MM)


###############################################################################
# Temporary File Helpers
###############################################################################

TMP_DIR = '/tmp'


def ensure_erase_tmp_dir():
    """Ensure that the /tmp directory exist and erase any existing files.
    """
    try:
        os.stat(TMP_DIR)
    except OSError:
        # Create the directory.
        os.mkdir(TMP_DIR)
    else:
        # Delete the existing files.
        for filename in os.listdir(TMP_DIR):
            os.remove(path.join(TMP_DIR, filename))


###############################################################################
# Geometric Functions
###############################################################################

def calc_legs(x, y):
    """Return the length of each trapezoidal leg as the tuple:
    ( <left-leg-length-mm>, <right-leg-length-mm> )

    Assuming the following geometry:

       b ||      || b
        _\/______\/_
        \   |  |   /
    c -> \  |  |  / <- c
     a ---->|  |<---- a
           \|__|/

    Add the top and side keepouts as fixed offsets.

    """
    # The "a" right triangle leg is always the same for both sides.
    # Just square it once now.
    a2 = math.pow(
        TOP_KEEPOUT_MM + y - SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM, 2
    )

    # Calculate the left leg.
    left_b = SIDE_KEEPOUT_MM + x - SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM
    left_c = math.sqrt(a2 + math.pow(left_b, 2))

    # Calculate the right leg.
    right_b = (UPPER_BASE_LENGTH_MM - left_b -
               SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM * 2)
    right_c = math.sqrt(a2 + math.pow(right_b, 2))

    return (left_c, right_c)


###############################################################################
# Z-Axis Servo Control
###############################################################################

SERVO_PULSE_PERIOD_MS = 20
SERVO_MIN_ROTATION_DEGREES = 0
SERVO_MAX_ROTATION_DEGREES = 180
SERVO_MIN_ROTATION_PULSE_WIDTH_MS = 1
SERVO_MAX_ROTATION_PULSE_WIDTH_MS = 2.5
SERVO_PULSE_WIDTH_MS_PER_ROTATION_DEGREE = (
    (SERVO_MAX_ROTATION_PULSE_WIDTH_MS - SERVO_MIN_ROTATION_PULSE_WIDTH_MS)
    / SERVO_MAX_ROTATION_DEGREES
)
Z_AXIS_UP_SERVO_DEGREES = 30
Z_AXIS_DOWN_SERVO_DEGREES = 0

servo_degrees_to_duty = lambda degrees: int(
    (SERVO_MIN_ROTATION_PULSE_WIDTH_MS +
     SERVO_PULSE_WIDTH_MS_PER_ROTATION_DEGREE * degrees
    ) / SERVO_PULSE_PERIOD_MS * 1024
)

SERVO_PWM = PWM(
    Pin(21),
    freq=int(1 / (SERVO_PULSE_PERIOD_MS / 1000)),
    duty=servo_degrees_to_duty(Z_AXIS_DOWN_SERVO_DEGREES)
)

set_servo_degrees = \
    lambda degrees: SERVO_PWM.duty(servo_degrees_to_duty(degrees))


def move_z(value):
    """Move the z-axis to the raised or lowered position based on whether the
    specified value is >= 0.
    """
    degrees = (Z_AXIS_UP_SERVO_DEGREES if value >= 0 else
               Z_AXIS_DOWN_SERVO_DEGREES)
    set_servo_degrees(degrees)
    global z_pos
    z_pos = value


###############################################################################
# Stepper Motor Control
###############################################################################

LEFT_STEPPER = 'l'
RIGHT_STEPPER = 'r'
# Area reachable by the v2 sled is:
#  width: 17.25" (~438 mm)
#  height: 19.125" (~485 mm)
X_MAX = 380
Y_MAX = 460
DIR_RETRACT = 'retract'
DIR_EXTEND = 'extend'
MIN_LEFT_LEG_LENGTH_MM, _ = calc_legs(0, 0)
_, MIN_RIGHT_LEG_LENGTH_MM = calc_legs(X_MAX, 0)
MAX_LEFT_LEG_LENGTH_MM, _ = calc_legs(X_MAX, Y_MAX)
_, MAX_RIGHT_LEG_LENGTH_MM = calc_legs(0, Y_MAX)
LINEAR_DISTANCE_PER_STEP = 0.1885

INTERSTEP_DELAY_MS = 4

STEPPER_NOT_ENABLE_PIN = Pin(0, Pin.OUT)
STEPPER_NOT_ENABLE_PIN.value(1)

LEFT_STEPPER_STEP_PIN = Pin(4, Pin.OUT)
LEFT_STEPPER_STEP_PIN.value(0)

LEFT_STEPPER_DIR_PIN = Pin(2, Pin.OUT)
LEFT_STEPPER_DIR_PIN.value(1)

RIGHT_STEPPER_STEP_PIN = Pin(15, Pin.OUT)
RIGHT_STEPPER_STEP_PIN.value(0)

RIGHT_STEPPER_DIR_PIN = Pin(13, Pin.OUT)
RIGHT_STEPPER_DIR_PIN.value(1)

# Init to home position.
x_pos = 0
y_pos = 0
z_pos = 0
move_z(z_pos)

left_leg_length, right_leg_length = calc_legs(x_pos, y_pos)

enable_steppers = lambda: STEPPER_NOT_ENABLE_PIN.value(0)
disable_steppers = lambda: STEPPER_NOT_ENABLE_PIN.value(1)


def pulse_step_pin(step_pin):
    # Stepper motor has a step angle of 1.8 degrees (200 steps / revolution)
    step_pin.value(1)
    sleep_us(1)
    step_pin.value(0)
    sleep_us(1)


def step(stepper, direction):
    """Single-step a motor in a direction.
    """
    global left_leg_length
    global right_leg_length

    if stepper == LEFT_STEPPER:
        if direction == DIR_RETRACT:
            if left_leg_length <= MIN_LEFT_LEG_LENGTH_MM:
                return False
            left_leg_length -= LINEAR_DISTANCE_PER_STEP
        elif direction == DIR_EXTEND:
            if left_leg_length >= MAX_LEFT_LEG_LENGTH_MM:
                return False
            left_leg_length += LINEAR_DISTANCE_PER_STEP
        step_pin = LEFT_STEPPER_STEP_PIN
        LEFT_STEPPER_DIR_PIN(0 if direction == DIR_RETRACT else 1)
    else:
        if direction == DIR_RETRACT:
            if right_leg_length <= MIN_RIGHT_LEG_LENGTH_MM:
                return False
            right_leg_length -= LINEAR_DISTANCE_PER_STEP
        elif direction == DIR_EXTEND:
            if right_leg_length >= MAX_RIGHT_LEG_LENGTH_MM:
                return False
            right_leg_length += LINEAR_DISTANCE_PER_STEP
        step_pin = RIGHT_STEPPER_STEP_PIN
        RIGHT_STEPPER_DIR_PIN(0 if direction == DIR_EXTEND else 1)

    pulse_step_pin(step_pin)
    return True


is_moving_to_point = False

def move_to_point(x, y):
    global x_pos
    global y_pos
    global left_leg_length
    global right_leg_length
    global is_moving_to_point

    if x > X_MAX or y > Y_MAX:
        raise OutOfBounds('x,y max is {},{}, got {},{}'.format(
            X_MAX, Y_MAX, x, y))

    if x == x_pos and y == y_pos:
        # Nothing to do.
        return

    # Calculate the new leg lengths and delta from the current.
    new_left_leg_length, new_right_leg_length = calc_legs(x, y)
    left_leg_length_delta = new_left_leg_length - left_leg_length
    right_leg_length_delta = new_right_leg_length - right_leg_length

    # Calculate the number of steps for each motor.
    num_left_steps = math.floor(
        abs(left_leg_length_delta / LINEAR_DISTANCE_PER_STEP)
    )
    num_right_steps = math.floor(
        abs(right_leg_length_delta / LINEAR_DISTANCE_PER_STEP)
    )

    if num_left_steps == 0 and num_right_steps == 0:
        # All deltas are smaller than a single step.
        return

    # Plan a linear path.
    max_num_steps_delta = max(num_left_steps, num_right_steps)
    left_leg_acc_step_size = num_left_steps / max_num_steps_delta
    right_leg_acc_step_size = num_right_steps / max_num_steps_delta
    left_leg_acc = 0
    right_leg_acc = 0

    left_steps_remaining = num_left_steps
    right_steps_remaining = num_right_steps
    is_moving_to_point = True
    enable_steppers()
    while left_steps_remaining or right_steps_remaining:
        if left_steps_remaining:
            last_left_leg_acc = left_leg_acc
            left_leg_acc += left_leg_acc_step_size
            if math.floor(left_leg_acc) != math.floor(last_left_leg_acc):
                step(LEFT_STEPPER,
                     DIR_RETRACT if left_leg_length_delta < 0 else DIR_EXTEND)
                left_steps_remaining -= 1

        if right_steps_remaining:
            last_right_leg_acc = right_leg_acc
            right_leg_acc += right_leg_acc_step_size
            if math.floor(right_leg_acc) != math.floor(last_right_leg_acc):
                step(RIGHT_STEPPER,
                     DIR_RETRACT if right_leg_length_delta < 0 else DIR_EXTEND)
                right_steps_remaining -= 1

        sleep_ms(INTERSTEP_DELAY_MS)

    # TODO - update the global positions in real time.
    x_pos = x
    y_pos = y
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
            move_to_point(x_pos + word_spacing, y_pos)
            x_offset += word_spacing
            continue

        points = list(char_def_to_points(CHARS[char]))

        # Calculate the scale.
        max_y = max(y for _, y in points)
        scale = math.ceil(char_height / (max_y + 1))

        # Add a sprue directly below the character entry point.
        sprue_coord = points[0]
        # Move all the points up one to make room for the sprue.
        points = [(x, y - 1) for x, y in points]
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

    NUMBER_UNIT_REGEX = re.compile('^(\d+(?:\.\d+)?)(.*)$')
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
                scale = math.floor(max(X_MAX, Y_MAX) / max(width, height))

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

                # Apply scaling.
                x *= scale
                y *= scale

                move_to_point(x, y)


###############################################################################
# Gcode Handler
###############################################################################

def execute_gcode(fh):
    class UNITS:
        INCHES = 0
        MILLIMETERS = 1

    class MODES:
        ABSOLUTE = 0
        INCREMENTAL = 1

    units = None
    mode = None

    inch_to_mm = lambda x: (x * 25.4) if x is not None else None

    def _assert_ready_to_move():
        if units is None or mode is None:
            raise AssertionError('units ({}) and/or mode ({}) is None'
                                 .format(units, mode))

    def calc_xyz_from_params(params):
        x = params.get('X')
        y = params.get('Y')
        z = params.get('Z')

        if units == UNITS.INCHES:
            x, y, z = map(inch_to_mm, (x, y, z))

        if x is None:
            x = x_pos
        elif mode == MODES.INCREMENTAL:
            x += x_pos

        if y is None:
            y = y_pos
        else:
            # Invert the specified Y to match our orientation.
            y = -y
            if mode == MODES.INCREMENTAL:
                y += y_pos

        if z is None:
            z = z_pos
        elif mode == MODES.INCREMENTAL:
            z += z_pos

        return x, y, z

    for line in fh:
        command, params = gcode.parse_line(line)
        if command == gcode.COMMANDS.PROGRAMMING_IN_INCHES:
            units = UNITS.INCHES

        elif command == gcode.COMMANDS.PROGRAMMING_IN_MILLIMETERS:
            units = UNITS.MILLIMETERS
            pass

        elif command == gcode.COMMANDS.ABSOLUTE_PROGRAMMING:
            mode = MODES.ABSOLUTE

        elif command == gcode.COMMANDS.INCREMENTAL_PROGRAMMING:
            mode = MODES.INCREMENTAL

        elif command == gcode.COMMANDS.RAPID_POSITIONING:
            _assert_ready_to_move()
            x, y, _ = calc_xyz_from_params(params)
            pre_rapid_z_pos = z_pos
            if z_pos < 0:
                # Raise the z-axis before moving.
                move_z(0)
            move_to_point(x, y)
            # Restore the pre-move z-axis position.
            set_z_axis_position(pre_rapid_z_pos)

        elif command == gcode.COMMANDS.LINEAR_INTERPOLATION:
            _assert_ready_to_move()
            x, y, z = calc_xyz_from_params(params)
            move_z(z)
            move_to_point(x, y)

        # Ignore all other commands


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
        'position': {
            'x': x_pos,
            'y': y_pos,
            'MAX_X': X_MAX,
            'MAX_Y': Y_MAX

        },
        'geometry': {
            'UPPER_BASE_LENGTH_MM': UPPER_BASE_LENGTH_MM,
            'LOWER_BASE_LENGTH_MM': LOWER_BASE_LENGTH_MM,
            'SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM':
              SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM,
            'SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM':
              SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM,
            'MIN_LEFT_LEG_LENGTH_MM': MIN_LEFT_LEG_LENGTH_MM,
            'MIN_RIGHT_LEG_LENGTH_MM': MIN_RIGHT_LEG_LENGTH_MM,
            'MAX_LEFT_LEG_LENGTH_MM': MAX_LEFT_LEG_LENGTH_MM,
            'MAX_RIGHT_LEG_LENGTH_MM': MAX_RIGHT_LEG_LENGTH_MM,
            'LINEAR_DISTANCE_PER_STEP': LINEAR_DISTANCE_PER_STEP,
            'left_leg': left_leg_length,
            'right_leg': right_leg_length
        }
    }
    return _200(body=data)


@route('/', methods=(GET,))
def index(request):
    return default_http_endpoints._fs_GET('/public/index.html')


@route('/demo', methods=(GET,))
def _demo(request):
    draw_text('WEEZEL', char_height=64, char_spacing=16, x_offset=0,
              y_offset=Y_MAX / 2 - 64)
    return _200()


@route('/trace_perimeter', methods=(GET,))
def _trace_perimeter(request):
    for x, y in (
            (0, 0),
            (0, Y_MAX),
            (X_MAX, Y_MAX),
            (X_MAX, 0),
            (0, 0),
    ):
        move_to_point(x, y)
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
    move_to_point(0, 0)
    return _200()


@route('/move_to_center', methods=(GET,))
def _move_to_center(request):
    """Move to the center.
    """
    move_to_point(X_MAX / 2, Y_MAX / 2)
    return _200()


@route('/demo_svg', methods=(GET,), query_param_parser_map={
    'filename': as_type(str)
})
def _demo_svg(request, filename):
    fh = open(filename, 'r')
    render_svg(fh)
    return _200()


@route('/execute_gcode', methods=(PUT,))
def _execute_gcode(request):
    # Upload the file to a temporary location.
    file_path = '/tmp/gcode.{}'.format(time.time())
    default_http_endpoints._fs_PUT(file_path, request)
    try:
        with open(file_path, 'r') as fh:
            execute_gcode(fh)
    finally:
        # Delete the temporary file.
        os.remove(file_path)
    return _200()


@route('/set_servo_degrees', methods=(GET,), query_param_parser_map={
    'degrees': as_type(int)
})
def _set_servo_degrees(request, degrees):
    set_servo_degrees(degrees)
    return _200()


if __name__ == '__main__':
    ensure_erase_tmp_dir()
    serve()
