"""Weezel-specific gcode decoding functions.
"""

import re
from collections import namedtuple


# Define the supported commands that we'll decode.
class COMMANDS:
    EMPTY = 0
    COMMENT = 1
    RAPID_POSITIONING = 2
    LINEAR_INTERPOLATION = 3
    PROGRAMMING_IN_INCHES = 4
    PROGRAMMING_IN_MILLIMETERS = 5
    ABSOLUTE_PROGRAMMING = 6
    INCREMENTAL_PROGRAMMING = 7
    UNSUPPORTED = 8

    @staticmethod
    def get_name(id):
        """Helper to do a reverse lookup on the integer command ID.
        """
        for k in dir(COMMANDS):
            if not k.startswith('__'):
                v = getattr(COMMANDS, k)
                if isinstance(v, int) and v == id:
                    return k


# Define regular expressions to parse values from each supported command type.
COMMENT_REGEX_STR = '(\s*;\s*.*)'
DECIMAL_REGEX_STR = '(\-?\d+(\.\d+)?)'
DecimalParamRegexStr = lambda var: '(({}){})'.format(
    var,
    DECIMAL_REGEX_STR,
)


COMMAND_REGEX_MAP = {
    COMMANDS.EMPTY: re.compile('^$'),
    COMMANDS.COMMENT: re.compile(
        '^{}$'.format(COMMENT_REGEX_STR)
    ),

    COMMANDS.RAPID_POSITIONING: re.compile(
        '^G0\s({})\s({}){}?$'.format(
            DecimalParamRegexStr('X'),
            DecimalParamRegexStr('Y'),
            COMMENT_REGEX_STR,
        )
    ),

    COMMANDS.LINEAR_INTERPOLATION: re.compile(
        '^G1(\s{})?(\s{})?(\s{})?(\s{})?{}?$'.format(
            DecimalParamRegexStr('X'),
            DecimalParamRegexStr('Y'),
            DecimalParamRegexStr('Z'),
            DecimalParamRegexStr('F'),
            COMMENT_REGEX_STR,
        )
    ),

    COMMANDS.PROGRAMMING_IN_INCHES: re.compile(
        '^G20{}?$'.format(COMMENT_REGEX_STR)
    ),

    COMMANDS.PROGRAMMING_IN_MILLIMETERS: re.compile(
        '^G21{}?$'.format(COMMENT_REGEX_STR)
    ),

    COMMANDS.ABSOLUTE_PROGRAMMING: re.compile(
        '^G90{}?$'.format(COMMENT_REGEX_STR)
    ),

    COMMANDS.INCREMENTAL_PROGRAMMING: re.compile(
        '^G91{}?$'.format(COMMENT_REGEX_STR)
    ),
}

COMMANDS_WITH_PACKED_PARAMS = (
    COMMANDS.RAPID_POSITIONING,
    COMMANDS.LINEAR_INTERPOLATION,
)


def unpack_matched_command_params(match):
    """Micropython doesn't support named or non-capturing RE groups so
    we need to jump through flaming hoops to recover the parameter values.
    """
    # Init i to point at the first captured param name group.
    i = 3
    params = {}
    while True:
        try:
            param_name = match.group(i)
        except IndexError:
            break
        if param_name is not None:
            param_value = float(match.group(i + 1))
            params[param_name] = param_value
        # Increment i to what would be the next param name group.
        i += 5
    return params


def parse_line(line):
    """Attempt to parse a GCODE line. If parsing succeeds, return a (<command>, <params>)
    tuple, otherwise return (<COMMANDS.UNSUPPORTED>, {})
    """
    line = line.strip()
    for command, regex in COMMAND_REGEX_MAP.items():
        match = regex.match(line)
        params = {}
        if match:
            if command in COMMANDS_WITH_PACKED_PARAMS:
                params = unpack_matched_command_params(match)
            return command, params
    return COMMANDS.UNSUPPORTED, params


def parse(fh):
    """Parse a gcode file and yield each supported command.
    """
    fh.seek(0)
    for command, params in map(parse_line, fh):
        yield command, params


###############################################################################
# Tests
###############################################################################

def _assert(actual, expected):
    if actual != expected:
        raise AssertionError('expected: {}, got: {}'.format(actual, expected))


def test_parse_line():
    for line, expected in (
            ('', (COMMANDS.EMPTY, {})),
            (' ', (COMMANDS.EMPTY, {})),
            ('; A comment', (COMMANDS.COMMENT, {})),

            ('G0 X20.2 Y30.3', (COMMANDS.RAPID_POSITIONING, {
                'X': float('20.2'),
                'Y': float('30.3')
            })),

            ('G0 X20.2 Y30.3 ; with a comment', (COMMANDS.RAPID_POSITIONING, {
                'X': float('20.2'),
                'Y': float('30.3')
            })),

            ('G1 X10.1 Y40.4',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'X': float('10.1'),
                 'Y': float('40.4'),
             })),

            ('G1 X10.1 Y40.4 ; with a comment',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'X': float('10.1'),
                 'Y': float('40.4'),
             })),

            ('G1 X-10.1 Y-40.4 Z20',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'X': float('-10.1'),
                 'Y': float('-40.4'),
                 'Z': float('20'),
             })),

            ('G1 X-10.1 Y-40.4 Z20 F30',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'X': float('-10.1'),
                 'Y': float('-40.4'),
                 'Z': float('20'),
                 'F': float('30'),
             })),

            ('G1 Z20',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'Z': float('20'),
             })),

            ('G1 Z20 F30',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'Z': float('20'),
                 'F': float('30'),
             })),

            ('G20', (COMMANDS.PROGRAMMING_IN_INCHES, {})),
            ('G21', (COMMANDS.PROGRAMMING_IN_MILLIMETERS, {})),
            ('G90', (COMMANDS.ABSOLUTE_PROGRAMMING, {})),
            ('G91', (COMMANDS.INCREMENTAL_PROGRAMMING, {})),

            ('G20 ; with a comment', (COMMANDS.PROGRAMMING_IN_INCHES, {})),
            ('G21 ; with a comment', (COMMANDS.PROGRAMMING_IN_MILLIMETERS, {})),
            ('G90 ; with a comment', (COMMANDS.ABSOLUTE_PROGRAMMING, {})),
            ('G91 ; with a comment', (COMMANDS.INCREMENTAL_PROGRAMMING, {})),
    ):
        _assert(parse_line(line), expected)


def run_tests():
    # Run all global functions with a name that starts with "test_".
    for k, v in sorted(globals().items()):
        if k.startswith('test_') and isfunction(v):
            test_name = v.__name__[5:]
            stdout.write('testing {}'.format(test_name))
            stdout.flush()
            try:
                v()
            except AssertionError as e:
                stdout.write(' - FAILED\n')
                raise
            else:
                stdout.write(' - ok\n')
            finally:
                stdout.flush()


def parse_file(fh):
    for line in fh:
        command, params = parse_line(line)
        command = COMMANDS.get_name(command)
        print('"{}" => {}'.format(line.strip(), (command, params)))


if __name__ == '__main__':
    import argparse
    from inspect import isfunction
    from sys import stdout

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--parse-file', type=argparse.FileType('r'))
    group.add_argument('--test', action='store_true', help="Run the tests")
    args = parser.parse_args()

    if args.test:
        run_tests()
    else:
        parse_file(args.parse_file)
