"""SVG Parsing Utilities
"""

import re
from collections import deque

from . import xmltok


NUMBER_UNIT_REGEX = re.compile('^(\d+)(.*)$')
FLOAT_RE_PATTERN = '\-?\d+(?:\.\d+)?'
FLOAT_REGEX = re.compile(FLOAT_RE_PATTERN)
PATH_COORD_REGEX = re.compile('({0}),({0})'.format(FLOAT_RE_PATTERN))
TRANSLATE_REGEX = re.compile(
    'translate\(({0}),({0})\)'.format(FLOAT_RE_PATTERN)
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


def take_while(pred, s):
    """Consume characters a string until the predicate becomes false, returning
    both the consumed string and any unconsumed tail.
    """
    i = 0
    max_i = len(s) - 1
    while i <= max_i and pred(s[i]):
        if i == max_i:
            break
        i += 1
    return s[:i], s[i:]


def drop_while(pred, s):
    """Ignore characters until the predicate becomes false and return the tail.
    """
    i = 0
    max_i = len(s) - 1
    while i <= max_i and pred(s[i]):
        if i == max_i:
            break
        i += 1
    return s[i:]


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

    def take_params(s):
        params = []
        tail = s
        while True:
            head, tail = take_while(
                lambda s: s != ' ' and not s.isalpha(),
                tail.strip()
            )
            if not head:
                # Param not found.
                break
            # Strip any leading whitespace.
            head = head.strip()

            # Attempt to parse as a coordinate pair.
            match = PATH_COORD_REGEX.match(head)
            if match:
                x = float(match.group(1))
                y = float(match.group(2))
                params.append((x, y))
                continue

            # Attempt to parse as a single number.
            match = FLOAT_REGEX.match(head)
            if match:
                x = float(match.group(1))
                params.append(x)
                continue

            raise CouldNotParse('d ATTR coordinate: {}'.format(head))

        return params, tail

    def process_command_with_params(command, params, arity):
        while params:
            param_set = params[:arity]
            if len(param_set) != arity:
                raise CouldNotParse(
                    'd ATTR {} param: {}'.format(command, param_set)
                )
            commands.append((command, param_set))
            params = params[arity:]

    while True:
        # Find the next command.
        s = drop_while(lambda s: not s.isalpha(), s)
        if not s:
            break

        command = s[0]
        params, s = take_params(s[1:])

        if command == 'm':
            commands.append((command, params[0]))
            # Any additional params are implicit 'l' commands.
            for param in params[1:]:
                commands.append(('l', param))

        elif command == 'M':
            commands.append((command, params[0]))
            # Any additional params are implicit 'L' commands.
            for param in params[1:]:
                commands.append(('L', param))

        elif command in ('L', 'l', 'H', 'h', 'V', 'v'):
            process_command_with_params(command, params, arity=1)

        elif command in ('C', 'c'):
            process_command_with_params(command, params, arity=3)

        elif command in ('S', 's', 'Q', 'q'):
            process_command_with_params(command, params, arity=2)

        elif command in ('T', 't'):
            process_command_with_params(command, params, arity=1)

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
