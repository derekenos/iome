"""SVG Parsing Utilities
"""

import re
from collections import deque

from . import xmltok

from .utils import (
    drop_while,
    take_while,
)


NUMBER_UNIT_REGEX = re.compile('^(\d+)(.*)$')
FLOAT_RE_PATTERN = '(\-?\d+(?:\.\d+)?)'
FLOAT_REGEX = re.compile(FLOAT_RE_PATTERN)
TRANSLATE_REGEX = re.compile(
    'translate\({0},{0}\)'.format(FLOAT_RE_PATTERN)
)


class CouldNotParse(Exception): pass

class State():
    def __init__(self):
        self.width = None
        self.width_unit = None
        self.height = None
        self.height_unit = None
        self.g_translates = []
        self.translate = (0, 0)
        self.first_path_point = None
        self.relative_reference = (0, 0)
        self.paths = deque()


parse_number_unit = NUMBER_UNIT_REGEX.match


def handle_start_tag(state, args):
    """Handle START_TAG token types.
    """
    ((_, tag_name),) = args
    if tag_name == 'g':
        state.g_translates.append((0, 0))
    elif tag_name == 'path':
        state.first_path_point = None


def handle_end_tag(state, args):
    """Handle END_TAG token types.
    """
    ((_, tag_name),) = args
    if tag_name == 'g':
        x, y = state.g_translates.pop()
        state.translate = state.translate[0] - x, state.translate[1] - y


def handle_height_attr(state, value):
    """Handle height ATTR value.
    """
    match = parse_number_unit(value)
    if not match:
        raise CouldNotParse('height attr: {}'.format(height))
    state.height = float(match.group(1))
    state.height_unit = match.group(2)


def handle_width_attr(state, value):
    """Handle width ATTR value.
    """
    match = parse_number_unit(value)
    if not match:
        raise CouldNotParse('width attr: {}'.format(width))
    state.width = float(match.group(1))
    state.width_unit = match.group(2)


def handle_transform_attr(state, value):
    """Handle transform ATTR value.
    """
    match = TRANSLATE_REGEX.match(value)
    if not match:
        raise CouldNotParse('transform attr: {}'.format(transform))
    x = float(match.group(1))
    y = float(match.group(2))
    state.g_translates[-1] = x, y
    state.translate = state.translate[0] + x, state.translate[1] + y


def parse_d_attr_commands(s):
    """Return a list of d ATTR commands in the format:
    [
      [<commandLetter>, <param1>, ...],
      ...
    ]
    """
    commands = []

    # Replace commas with spaces and collapse consecutive whitespace.
    # See: https://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation
    s = ' '.join(s.replace(',', ' ').split(' '))

    def take_params(s):
        params = []
        tail = s
        while True:
            head, tail = take_while(
                lambda s: s.isdigit() or s == '-' or s == '.',
                tail.strip()
            )
            if not head:
                # Param not found.
                break

            # Attempt to parse as a float.
            match = FLOAT_REGEX.match(head)
            if match:
                x = float(match.group(1))
                params.append(x)
                continue

            raise CouldNotParse('d ATTR coordinate: {}'.format(head))

        return params, tail

    def process_command_with_params(command, params, arity, max_sets=None):
        """For the specified command, attempt to parse arity number of floats
        from the params string and append the command + single set of params to
        commands. Attempt to parse additional param sets with the assumption
        that they correspond to implicit repeats of the specified command. If
        max_sets is specified, parse up to that number of param sets and return
        what remains of the params string.
        """
        while params and (max_sets is None or max_sets > 0):
            param_set = params[:arity]
            if len(param_set) != arity:
                raise CouldNotParse(
                    'd ATTR {} param: {}'.format(command, param_set))
            commands.append((command, tuple(param_set)))
            params = params[arity:]
            if max_sets is not None:
                max_sets -= 1
        return params

    while True:
        # Find the next command.
        s = drop_while(lambda s: not s.isalpha(), s)
        if not s:
            break

        command = s[0]
        params, s = take_params(s[1:])

        if command == 'm':
            params = process_command_with_params(command, params, 2, 1)
            # Interpret additional params as implicit 'l' commands.
            process_command_with_params('l', params, 2)

        elif command == 'M':
            params = process_command_with_params(command, params, 2, 1)
            # Interpret additional params as implicit 'L' commands.
            process_command_with_params('L', params, 2)

        elif command in ('L', 'l', 'H', 'h', 'V', 'v'):
            process_command_with_params(command, params, arity=2)

        elif command in ('C', 'c'):
            process_command_with_params(command, params, arity=6)

        elif command in ('S', 's', 'Q', 'q'):
            process_command_with_params(command, params, arity=4)

        elif command in ('T', 't'):
            process_command_with_params(command, params, arity=2)

        elif command in ('z', 'Z'):
            commands.append((command, []))

    return commands


def handle_d_attr(state, value):
    """Handle d ATTR value.
    """
    state.paths.append(parse_d_attr_commands(value))


ATTR_NAME_HANDLER_MAP = {
    'height': handle_height_attr,
    'width': handle_width_attr,
    'transform': handle_transform_attr,
    'd': handle_d_attr,
}


def handle_attr_tag(state, args):
    """Handle ATTR token types.
    """
    (_, attr_name), attr_value = args
    if attr_name in ATTR_NAME_HANDLER_MAP:
        ATTR_NAME_HANDLER_MAP[attr_name](state, attr_value)


TOKEN_TYPE_HANDLER_MAP = {
    'START_TAG': handle_start_tag,
    'END_TAG': handle_end_tag,
    'ATTR': handle_attr_tag,
}


def paths(fh):
    """Parse an SVG file and yield each parsed path element.
    """
    state = State()

    for token in xmltok.tokenize(fh):
        token_type = token[0]
        if token_type in TOKEN_TYPE_HANDLER_MAP:
            TOKEN_TYPE_HANDLER_MAP[token_type](state, token[1:])

        while state.paths:
            yield state.paths.popleft()

    # if not width or not height:
    #     raise AssertionError(
    #         'about to parse path but height and/or width not '
    #         'set: {}/{}'.format(width, height))
    # elif width_unit != height_unit:
    #     raise AssertionError('Different width/height units: {}/{}'
    #                          .format(width_unit, height_unit))

    # is_relative = False
    # for s in v.split():
    #     match = PATH_COORD_REGEX.match(s)
    #     if not match:
    #         if s != 'z':
    #             is_relative = s.islower()
    #             continue
    #         else:
    #             # Close the path.
    #             is_relative = False
    #             relative_reference = (0, 0)
    #             x, y = first_path_point
    #     else:
    #         x = math.floor(float(match.group(1)))
    #         y = math.floor(float(match.group(2)))

    #     if first_path_point is None:
    #         first_path_point = (x, y)

    #     if is_relative:
    #         rel_x, rel_y = relative_reference
    #         x += rel_x
    #         y += rel_y

    #     # Set the current point as the relative reference if not
    #     # closing the path.
    #     if s != 'z':
    #         relative_reference = x, y

    #     # Apply the current cumulative translations.
    #     x += math.floor(translate[0])
    #     y += math.floor(translate[1])


###############################################################################
# Tests
###############################################################################

from unittest import TestCase


class SVGParserTester(TestCase):
    def test_parse_d_attr_commands_m_single_param(self):
        d = 'm 1.2,-1.1'
        expected = [
            ('m', (1.2, -1.1))
        ]
        self.assertEqual(parse_d_attr_commands(d), expected)


    def test_parse_d_attr_commands_M_single_param(self):
        d = 'M 1.2,-1.1'
        expected = [
            ('M', (1.2, -1.1))
        ]
        self.assertEqual(parse_d_attr_commands(d), expected)


    def test_parse_d_attr_commands_m_mutli_param(self):
        # Check that all params after the first are parsed as 'l'-type.
        d = 'm 1.2,-1.1 2.0,3.0 4.1,5.1'
        expected = [
            ('m', (1.2, -1.1)),
            ('l', (2.0, 3.0)),
            ('l', (4.1, 5.1)),
        ]
        self.assertEqual(parse_d_attr_commands(d), expected)


    def test_parse_d_attr_commands_M_mutli_param(self):
        # Check that all params after the first are parsed as 'L'-type.
        d = 'M 1.2,-1.1 2.0,3.0 4.1,5.1'
        expected = [
            ('M', (1.2, -1.1)),
            ('L', (2.0, 3.0)),
            ('L', (4.1, 5.1)),
        ]
        self.assertEqual(parse_d_attr_commands(d), expected)


    def test_parse_d_attr_w3c_(self):
        """https://www.w3.org/TR/SVG/paths.html#PathDataGeneralInformation
        """
        d = 'M 100 100 L 200 200'
        expected = [
            ('M', (100, 100)),
            ('L', (200, 200)),
        ]
        self.assertEqual(parse_d_attr_commands(d), expected)

        d = 'M100 100L200 200'
        # Same expected.
        self.assertEqual(parse_d_attr_commands(d), expected)

        d = 'M 100 200 L 200 100 L -100 -200'
        expected = [
            ('M', (100, 200)),
            ('L', (200, 100)),
            ('L', (-100, -200)),
        ]
        self.assertEqual(parse_d_attr_commands(d), expected)

        d = 'M 100 200 L 200 100 -100 -200'
        # Same expected.
        self.assertEqual(parse_d_attr_commands(d), expected)
