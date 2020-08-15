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
    _503,
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
# Utility Functions
###############################################################################

inch_to_mm = lambda x: (x * 25.4) if x is not None else None


###############################################################################
# File Operation Helpers
###############################################################################

TMP_DIR = '/tmp'
DATA_DIR = '/data'

class DATAFILES:
    STATE = 0

DATAFILE_FILENAME_MAP = {
    DATAFILES.STATE: 'state',
}


def ensure_erase_tmp_dir():
    """Ensure that the tmp directory exists and erase any existing files.
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


def ensure_data_dir():
    """Ensure that the data directory exists and erase any existing files.
    """
    try:
        os.stat(DATA_DIR)
    except OSError:
        # Create the directory.
        os.mkdir(DATA_DIR)


def read_datafile(name):
    filename = DATAFILE_FILENAME_MAP[name]
    file_path = path.join(DATA_DIR, filename)
    if not path.exists(file_path):
        return None
    return json.load(open(file_path, 'r', encoding='utf-8'))


def write_datafile(name, data):
    filename = DATAFILE_FILENAME_MAP[name]
    file_path = path.join(DATA_DIR, filename)
    # Attempt to encode here to prevent truncating an existing file in the case
    # of an error.
    data = json.dumps(data)
    with open(file_path, 'w') as fh:
        fh.write(data)


###############################################################################
# Stepper Class
###############################################################################

class Stepper:
    """Stepper motor interface.
    Current model: https://www.amazon.com/gp/product/B00PNEQI7W
    """
    STEPS_PER_REVOLUTION = 200

    # These CW (clockwise) and CCW (counter-clockwise) direction pin values
    # correspond to the way in which the shaft will turn when you view the
    # stepper head-on from the front.
    CCW, CW = 0, 1

    def __init__(self, not_enable_pin_num, dir_pin_num, step_pin_num):
        self.not_enable_pin = Pin(not_enable_pin_num, Pin.OUT)
        self.not_enable_pin.value(1)

        self.step_pin = Pin(step_pin_num, Pin.OUT)
        self.step_pin.value(0)

        self.dir_pin = Pin(dir_pin_num, Pin.OUT)
        self.dir_pin.value(1)

    def enable(self):
        self.not_enable_pin.value(0)

    def disable(self):
        self.not_enable_pin.value(1)

    def pulse_step_pin(self):
        self.step_pin.value(1)
        sleep_us(1)
        self.step_pin.value(0)
        sleep_us(1)

    def step(self, direction):
        self.dir_pin(direction)
        self.pulse_step_pin()


###############################################################################
# Stepper Motor Assembly Class
###############################################################################

class StepperMotorAssembly(Stepper):
    # Define the diameter of the timing pulley inner surface that comes in
    # contact with the belt.
    TIMING_PULLEY_BELT_MATING_SURFACE_DIAMETER_MM = 12

    # Derived constants.
    TIMING_PULLEY_BELT_MATING_SURFACE_CURCUMFERENCE_MM = \
        2 * math.pi * (TIMING_PULLEY_BELT_MATING_SURFACE_DIAMETER_MM / 2)
    MM_PER_STEP = (TIMING_PULLEY_BELT_MATING_SURFACE_CURCUMFERENCE_MM /
                   Stepper.STEPS_PER_REVOLUTION)


###############################################################################
# Servo Class
###############################################################################

class Servo:
    """Servo motor interface.
    Current model: https://www.amazon.com/gp/product/B072V529YD
    """
    PULSE_PERIOD_MS = 20
    MIN_ROTATION_DEGREES = 0
    MAX_ROTATION_DEGREES = 180
    MIN_ROTATION_PULSE_WIDTH_MS = 1
    MAX_ROTATION_PULSE_WIDTH_MS = 2.5
    PULSE_WIDTH_MS_PER_ROTATION_DEGREE = (
        (MAX_ROTATION_PULSE_WIDTH_MS - MIN_ROTATION_PULSE_WIDTH_MS)
        / MAX_ROTATION_DEGREES
    )

    @classmethod
    def servo_degrees_to_duty(cls, degrees):
        return int(
            (cls.MIN_ROTATION_PULSE_WIDTH_MS +
             cls.PULSE_WIDTH_MS_PER_ROTATION_DEGREE * degrees
            ) / cls.PULSE_PERIOD_MS * 1024
        )

    def __init__(self, pin_num):
        self.pwm = PWM(
            Pin(pin_num),
            freq=int(1 / (self.PULSE_PERIOD_MS / 1000)),
            duty=self.servo_degrees_to_duty(0)
        )

    def set(self, degrees):
        self.pwm.duty(self.servo_degrees_to_duty(degrees))


###############################################################################
# Z-Axis Class
###############################################################################

class ZAxis(Servo):
    LIFTED_POSITION_DEGREES = 30
    DROPPED_POSITION_DEGREES = 0

    def lift(self):
        self.set(self.LIFTED_POSITION_DEGREES)

    def drop(self):
        self.set(self.DROPPED_POSITION_DEGREES)


###############################################################################
# Weezel Class
###############################################################################

class Weezel:
    HOME_X = 0
    HOME_Y = 0
    HOME_Z = 0

    UPPER_BASE_LENGTH_MM = 649
    LOWER_BASE_LENGTH_MM = 23
    SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM = 11.5
    SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM = 20

    MAX_X = 380
    MAX_Y = 460
    INTERSTEP_DELAY_MS = 8

    # Values to compensate for the unusable area within the trapazoid.
    UPPER_BASE_ENDPOINT_FRAME_VERTICAL_OFFSET_MM = 18.5
    UPPER_BASE_ENDPOINT_FRAME_HORIZONTAL_OFFSET_MM = 14.3
    EASEL_FRAME_BEAM_WIDTH_MM = 40
    SLED_EDGE_IMPLEMENT_TOP_OFFSET_MM = 28
    SLED_EDGE_IMPLEMENT_HORIZONTAL_OFFSET_MM = 54
    TOP_KEEPOUT_MM = (UPPER_BASE_ENDPOINT_FRAME_VERTICAL_OFFSET_MM +
                      EASEL_FRAME_BEAM_WIDTH_MM +
                      SLED_EDGE_IMPLEMENT_TOP_OFFSET_MM)

    SIDE_KEEPOUT_MM = (UPPER_BASE_ENDPOINT_FRAME_HORIZONTAL_OFFSET_MM +
                       EASEL_FRAME_BEAM_WIDTH_MM +
                       SLED_EDGE_IMPLEMENT_HORIZONTAL_OFFSET_MM)

    @classmethod
    def calc_legs(cls, x, y):
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
            cls.TOP_KEEPOUT_MM + y -
            cls.SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM, 2
        )

        # Calculate the left leg.
        left_b = cls.SIDE_KEEPOUT_MM + x - \
            cls.SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM
        left_c = math.sqrt(a2 + math.pow(left_b, 2))

        # Calculate the right leg.
        right_b = (cls.UPPER_BASE_LENGTH_MM - left_b -
                   cls.SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM * 2)
        right_c = math.sqrt(a2 + math.pow(right_b, 2))
        return (left_c, right_c)

    def __init__(self, left_stepper_motor_assembly,
                 right_stepper_motor_assembly, z_axis):

        self.MIN_LEFT_LEG_LENGTH_MM, _ = self.calc_legs(0, 0)
        self._, MIN_RIGHT_LEG_LENGTH_MM = self.calc_legs(self.MAX_X, 0)
        self.MAX_LEFT_LEG_LENGTH_MM, _ = self.calc_legs(self.MAX_X, self.MAX_Y)
        self._, MAX_RIGHT_LEG_LENGTH_MM = self.calc_legs(0, self.MAX_Y)

        self.left_stepper_motor_assembly = left_stepper_motor_assembly
        self.right_stepper_motor_assembly = right_stepper_motor_assembly
        self.z_axis = z_axis

        self.x = self.HOME_X
        self.y = self.HOME_Y
        self.z = self.HOME_Z
        self.move_z(self.z)

        # The length of the trapazoid geometry legs.
        self.left_leg_length, self.right_leg_length = \
            self.calc_legs(self.x, self.y)

        # Flag to indicate whether a motion operation is active.
        self.in_motion = False

    def disable_steppers(self):
        self.left_stepper_motor_assembly.disable()
        self.right_stepper_motor_assembly.disable()

    def move_z(self, z):
        if z < 0:
            self.z_axis.drop()
        else:
            self.z_axis.lift()
        self.z = z

    def move_xy(self, x, y):
        if x > self.MAX_X or y > self.MAX_Y:
            raise OutOfBounds('x,y max is {},{}, got {},{}'.format(
                self.MAX_X, self.MAX_Y, x, y))

        if x == self.x and y == self.y:
            # Nothing to do.
            return

        # Calculate the new leg lengths and delta from the current.
        new_left_leg_length, new_right_leg_length = self.calc_legs(x, y)
        left_leg_length_delta = new_left_leg_length - self.left_leg_length
        right_leg_length_delta = new_right_leg_length - self.right_leg_length

        # Calculate the number of steps for each motor.
        num_left_steps = math.floor(
            abs(left_leg_length_delta /
                self.left_stepper_motor_assembly.MM_PER_STEP)
        )
        num_right_steps = math.floor(
            abs(right_leg_length_delta /
                self.right_stepper_motor_assembly.MM_PER_STEP)
        )

        if num_left_steps == 0 and num_right_steps == 0:
            # All deltas are smaller than a single step.
            return

        # Scale the length delta of each belt over the duration of the move.
        max_num_steps_delta = max(num_left_steps, num_right_steps)
        left_leg_acc_step_size = num_left_steps / max_num_steps_delta
        right_leg_acc_step_size = num_right_steps / max_num_steps_delta
        left_leg_acc = 0
        right_leg_acc = 0

        left_steps_remaining = num_left_steps
        right_steps_remaining = num_right_steps
        self.left_stepper_motor_assembly.enable()
        self.right_stepper_motor_assembly.enable()
        while left_steps_remaining or right_steps_remaining:
            if left_steps_remaining:
                last_left_leg_acc = left_leg_acc
                left_leg_acc += left_leg_acc_step_size
                if math.floor(left_leg_acc) != math.floor(last_left_leg_acc):
                    self.left_stepper_motor_assembly.step(
                        Stepper.CCW if left_leg_length_delta < 0 else
                        Stepper.CW
                    )
                    left_steps_remaining -= 1

            if right_steps_remaining:
                last_right_leg_acc = right_leg_acc
                right_leg_acc += right_leg_acc_step_size
                if math.floor(right_leg_acc) != math.floor(last_right_leg_acc):
                    self.right_stepper_motor_assembly.step(
                        Stepper.CW if right_leg_length_delta < 0 else
                        Stepper.CCW
                    )
                    right_steps_remaining -= 1

            sleep_ms(self.INTERSTEP_DELAY_MS)

        self.left_stepper_motor_assembly.disable()
        self.right_stepper_motor_assembly.disable()

        self.x = x
        self.y = y
        self.left_leg_length = new_left_leg_length
        self.right_leg_length = new_right_leg_length


###############################################################################
# Decorators
###############################################################################

def motion_operation(func):
    """A decorator for functions that effect (relatively) long-running
    motion operations that handles global state modifications and
    last-known-position persistence.
    """
    def f(weezel, *args, **kwargs):
        if weezel.in_motion:
            # A motion operation is already in progress so return a
            # HTTP 503 - server currently unavailable response.
            return _503()
        weezel.in_motion = True
        try:
            result = func(weezel, *args, **kwargs)
        except:
            raise
        else:
            return result
        finally:
            weezel.in_motion = False
            # TODO
            #weezel.save_state()
    return f


###############################################################################
# Text Drawing Functions
###############################################################################

@motion_operation
def draw_text(weezel, text, char_height, char_spacing=None, word_spacing=None,
              x_offset=None, y_offset=None):
    """
    """
    # TODO: check whether plotting text will exceed width before starting
    # TODO: add line wrapping

    weezel.z_axis.drop()

    # If not specified, set char_spacing and word_spacing relative to
    # char_height.
    if char_spacing is None:
        char_spacing = math.floor(char_height / 8)
    if word_spacing is None:
        word_spacing = char_spacing * 4

    # Use the current x/y position if unspecified.
    if x_offset is None:
        x_offset = weezel.x
    if y_offset is None:
        y_offset = weezel.y

    # Iterate through the characters in text, drawing each and incrementing the
    # x_offset.
    for char in text:
        # Handle SPACE and unsupported chars by advancing the x position by
        # word_spacing number of steps.
        if char == ' ' or char not in CHARS:
            weezel.move_xy(weezel.x + word_spacing, weezel.y)
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

        for point in points:
            x, y = point
            weezel.move_xy(x, y)

        x_offset += next_x_offset

    weezel.z_axis.lift()


###############################################################################
# Gcode Helpers
###############################################################################

@motion_operation
def execute_gcode(weezel, fh):
    class UNITS:
        INCHES = 0
        MILLIMETERS = 1

    class MODES:
        ABSOLUTE = 0
        INCREMENTAL = 1

    units = None
    mode = None

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
            x = weezel.x
        elif mode == MODES.INCREMENTAL:
            x += weezel.x

        if y is None:
            y = weezel.y
        else:
            # Invert the specified Y to match our orientation.
            y = -y
            if mode == MODES.INCREMENTAL:
                y += weezel.y

        if z is None:
            z = weezel.z
        elif mode == MODES.INCREMENTAL:
            z += weezel.z

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
            pre_rapid_weezel.z = weezel.z
            if weezel.z < 0:
                # Raise the z-axis before moving.
                weezel.move_z(0)
            weezel.move_xy(x, y)
            # Restore the pre-move z-axis position.
            set_z_axis_position(pre_rapid_weezel.z)

        elif command == gcode.COMMANDS.LINEAR_INTERPOLATION:
            _assert_ready_to_move()
            x, y, z = calc_xyz_from_params(params)
            weezel.move_z(z)
            weezel.move_xy(x, y)

        # Ignore all other commands


###############################################################################
# Route Handlers
###############################################################################

def attach_routes(weezel):

    @route('/_reset', methods=(GET, POST))
    def _reset(request):
        """Reset the device.
        """
        # Manually send the response prior to calling machine.reset
        send(request.connection, _200())
        machine.reset()


    @route('/state', methods=(GET,))
    @as_json
    def _state(request):
        data = {
            'weezel': {
                k: getattr(weezel, k) for k in (
                    'x',
                    'y',
                    'z',
                    'left_leg_length',
                    'right_leg_length',
                )
            }
        }
        return _200(body=data)


    @route('/constants', methods=(GET,))
    @as_json
    def _constants(request):
        data = {
            'weezel': {
                k: getattr(weezel, k) for k in (
                    'HOME_X',
                    'HOME_Y',
                    'HOME_Z',
                    'UPPER_BASE_LENGTH_MM',
                    'LOWER_BASE_LENGTH_MM',
                    'SLED_BELT_CATCH_IMPLEMENT_X_OFFSET_MM',
                    'SLED_BELT_CATCH_IMPLEMENT_Y_OFFSET_MM',
                    'MAX_X',
                    'MAX_Y',
                    'INTERSTEP_DELAY_MS',
                    'UPPER_BASE_ENDPOINT_FRAME_VERTICAL_OFFSET_MM',
                    'UPPER_BASE_ENDPOINT_FRAME_HORIZONTAL_OFFSET_MM',
                    'EASEL_FRAME_BEAM_WIDTH_MM',
                    'SLED_EDGE_IMPLEMENT_TOP_OFFSET_MM',
                    'SLED_EDGE_IMPLEMENT_HORIZONTAL_OFFSET_MM',
                    'TOP_KEEPOUT_MM',
                    'SIDE_KEEPOUT_MM',
                )
            },
            'left_stepper_motor_assembly': {
                k: getattr(weezel.left_stepper_motor_assembly, k) for k in (
                    'STEPS_PER_REVOLUTION',
                    'TIMING_PULLEY_BELT_MATING_SURFACE_DIAMETER_MM',
                    'TIMING_PULLEY_BELT_MATING_SURFACE_CURCUMFERENCE_MM',
                    'MM_PER_STEP',
                )
            },
            'right_stepper_motor_assembly': {
                k: getattr(weezel.left_stepper_motor_assembly, k) for k in (
                    'STEPS_PER_REVOLUTION',
                    'TIMING_PULLEY_BELT_MATING_SURFACE_DIAMETER_MM',
                    'TIMING_PULLEY_BELT_MATING_SURFACE_CURCUMFERENCE_MM',
                    'MM_PER_STEP',
                )
            },
            'z_axis': {
                k: getattr(weezel.z_axis, k) for k in (
                    'LIFTED_POSITION_DEGREES',
                    'DROPPED_POSITION_DEGREES',
                    'PULSE_PERIOD_MS',
                    'MIN_ROTATION_DEGREES',
                    'MAX_ROTATION_DEGREES',
                    'MIN_ROTATION_PULSE_WIDTH_MS',
                    'MAX_ROTATION_PULSE_WIDTH_MS',
                    'PULSE_WIDTH_MS_PER_ROTATION_DEGREE',
                )
            }
        }
        return _200(body=data)


    @route('/', methods=(GET,))
    def index(request):
        return default_http_endpoints._fs_GET('/public/index.html')


    @route('/demo', methods=(GET,))
    def _demo(request):
        draw_text(weezel, 'WEEZEL', char_height=64, char_spacing=16,
                  x_offset=0, y_offset=MAX_Y / 2 - 64)
        return _200()


    @route('/trace_perimeter', methods=(GET,))
    def _trace_perimeter(request):
        for x, y in (
                (0, 0),
                (0, weezel.MAX_Y),
                (weezel.MAX_X, weezel.MAX_Y),
                (weezel.MAX_X, 0),
                (0, 0),
        ):
            weezel.move_xy(x, y)
        return _200()


    @route('/write', methods=(GET,), query_param_parser_map={
        'text': as_type(str),
        'char_height': as_with_default(as_type(float), 10),
        'char_spacing': as_with_default(as_type(int), 10),
        'word_spacing': as_with_default(as_type(int), 40),
        'x_offset': as_maybe(as_type(int)),
        'y_offset': as_maybe(as_type(int)),
       })
    def _write(request, text, char_height, char_spacing, word_spacing,
               x_offset, y_offset):
        draw_text(weezel, text, char_height, char_spacing, word_spacing,
                  x_offset, y_offset)
        return _200()


    @route('/move', methods=(GET,), query_param_parser_map={
        'x': as_maybe(as_type(int)),
        'y': as_maybe(as_type(int)),
        'z': as_maybe(as_type(int)),
       })
    def _move(request, x, y, z):
        if x is None:
            x = weezel.x
        if y is None:
            y = weezel.y
        if z is None:
            z = weezel.z
        weezel.move_z(z)
        weezel.move_xy(x, y)
        return _200()


    _draw_dq = deque((), 512)
    @route('/draw', methods=(GET,))
    @as_websocket
    def _draw(request, ws):
        def callback(timer):
            nonlocal _draw_dq
            # Expect the first 2 bytes to comprise the payload length.
            payload_len = ws.read(2)
            if payload_len is not None:
                data = json.loads(ws.read(int(payload_len)))
                _draw_dq.append((
                    data['event'],
                    int(data['x']),
                    int(data['y'])
                ))

            if not weezel.in_motion and _draw_dq:
                event, x, y = _draw_dq.popleft()
                if event == 'draw':
                    weezel.z_axis.drop()
                else:
                    weezel.z_axis.lift()
                weezel.move_xy(x, y)

            timer.init(period=20, mode=Timer.ONE_SHOT, callback=callback)
        callback(Timer(-1))


    @route('/home', methods=(GET,))
    def _home(request):
        weezel.move_xy(0, 0)
        return _200()


    @route('/reset_home', methods=(GET,))
    def _reset_home(request):
        weezel.x = weelzel.HOME_X
        weezel.y = weelzel.HOME_Y
        weezel.z = weelzel.HOME_Z
        weezel.move_z(weezel.z)
        weezel.left_leg_length, weezel.right_leg_length = \
            weezel.calc_legs(weezel.x, weezel.y)
        return _200()


    @route('/move_to_center', methods=(GET,))
    def _move_to_center(request):
        """Move to the center.
        """
        weezel.move_xy(weezel.MAX_X / 2, weezel.MAX_Y / 2)
        return _200()


    @route('/execute_gcode', methods=(PUT,))
    def _execute_gcode(request):
        # Upload the file to a temporary location.
        file_path = '/tmp/gcode.{}'.format(time.time())
        default_http_endpoints._fs_PUT(file_path, request)
        try:
            with open(file_path, 'r') as fh:
                execute_gcode(weezel, fh)
        finally:
            # Delete the temporary file.
            os.remove(file_path)
        weezel.move_xy(0, 0)
        return _200()


if __name__ == '__main__':
    ensure_erase_tmp_dir()
    ensure_data_dir()


    weezel = Weezel(
        left_stepper_motor_assembly=StepperMotorAssembly(
            not_enable_pin_num=0,
            dir_pin_num=2,
            step_pin_num=4,
        ),
        right_stepper_motor_assembly=StepperMotorAssembly(
            not_enable_pin_num=0,
            dir_pin_num=13,
            step_pin_num=15,
        ),
        z_axis=ZAxis(pin_num=21)
    )
    attach_routes(weezel)
    serve()
