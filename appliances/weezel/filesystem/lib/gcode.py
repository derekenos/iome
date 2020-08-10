"""Weezel-specific gcode decoding functions.
"""

import re
from collections import deque


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
    UNSUPPORTED  = 8


# Define regular expressions to parse values from each supported command type.
DECIMAL_REGEX_STR = '\-?\d+(?:\.\d+)?'
DecimalVariableRegexStr = lambda symbol, name: '{}(?P<{}>{})'.format(
    symbol,
    name,
    DECIMAL_REGEX_STR,
)

COMMAND_REGEX_MAP = {
    COMMANDS.EMPTY: re.compile('^$'),
    COMMANDS.COMMENT: re.compile('^;\s*(?P<text>.*)$'),

    COMMANDS.RAPID_POSITIONING: re.compile(
        '^G0\s{}\s{}$'.format(
            DecimalVariableRegexStr('X', 'x'),
            DecimalVariableRegexStr('Y', 'y'),
        )
    ),

    COMMANDS.LINEAR_INTERPOLATION: re.compile(
        '^G1(?:\s{})?(?:\s{})?(?:\s{})?(?:\s{})?$'.format(
            DecimalVariableRegexStr('X', 'x'),
            DecimalVariableRegexStr('Y', 'y'),
            DecimalVariableRegexStr('Z', 'z'),
            DecimalVariableRegexStr('F', 'feed_rate'),
        )
    ),

    COMMANDS.PROGRAMMING_IN_INCHES: re.compile('^G20$'),
    COMMANDS.PROGRAMMING_IN_MILLIMETERS: re.compile('^G21$'),
    COMMANDS.ABSOLUTE_PROGRAMMING: re.compile('^G90$'),
    COMMANDS.INCREMENTAL_PROGRAMMING: re.compile('^G91$'),
}


def parse_line(line):
    """Attempt to parse a GCODE line. If parsing succeeds, return a (<command>, <params>)
    tuple, otherwise return (<COMMANDS.UNSUPPORTED>, {})
    """
    line = line.strip()
    for command, regex in COMMAND_REGEX_MAP.items():
        match = regex.match(line)
        if match:
            params = match.groupdict()
            if command != COMMANDS.COMMENT:
                # Convert numerical params.
                params = {k: float(v) if v is not None else v for k, v in params.items()}
            return command, params
    return COMMANDS.UNSUPPORTED, {}


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


def test_DECIMAL_REGEX_STR():
    for value, expected in (
            ('', None),
            ('0', '0'),
            ('1', '1'),
            ('-1', '-1'),
            ('0.01', '0.01'),
            ('-0.01', '-0.01'),
        ):
        actual = re.match(DECIMAL_REGEX_STR, value)
        if actual is not None:
            actual = actual.group(0)
        _assert(actual, expected)


def test_DecimalVariableRegexStr():
    for symbol, name, value, expected in (
            ('X', 'x', '', None),
            ('X', 'x', 'Y1', None),
            ('X', 'x', 'x1', None),
            ('X', 'x', 'X1', { 'x': '1' }),
            ('X', 'x', 'X1.0', { 'x': '1.0' }),
            ('X', 'x', 'X-1.0', { 'x': '-1.0' }),
            ('F', 'feed_rate', 'F20', { 'feed_rate': '20' }),
            ('F', 'feed_rate', 'F20.6', { 'feed_rate': '20.6' }),
        ):
        actual = re.match(DecimalVariableRegexStr(symbol, name), value)
        if actual is not None:
            actual = actual.groupdict()
        _assert(actual, expected)


def test_parse_line():
    for line, expected in (
            ('', (COMMANDS.EMPTY, {})),
            (' ', (COMMANDS.EMPTY, {})),
            ('; A comment', (COMMANDS.COMMENT, { 'text': 'A comment' })),

            ('G0 X20.2 Y30.3', (COMMANDS.RAPID_POSITIONING, {
                'x': float('20.2'),
                'y': float('30.3')
            })),

            ('G1 X10.1 Y40.4',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'x': float('10.1'),
                 'y': float('40.4'),
                 'z': None,
                 'feed_rate': None,
             })),

            ('G1 X-10.1 Y-40.4 Z20',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'x': float('-10.1'),
                 'y': float('-40.4'),
                 'z': float('20'),
                 'feed_rate': None,
             })),

            ('G1 X-10.1 Y-40.4 Z20 F30',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'x': float('-10.1'),
                 'y': float('-40.4'),
                 'z': float('20'),
                 'feed_rate': float('30'),
             })),

            ('G1 Z20',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'x': None,
                 'y': None,
                 'z': float('20'),
                 'feed_rate': None,
             })),

            ('G1 Z20 F30',
             (COMMANDS.LINEAR_INTERPOLATION, {
                 'x': None,
                 'y': None,
                 'z': float('20'),
                 'feed_rate': float('30'),
             })),

            ('G20', (COMMANDS.PROGRAMMING_IN_INCHES, {})),
            ('G21', (COMMANDS.PROGRAMMING_IN_MILLIMETERS, {})),
            ('G90', (COMMANDS.ABSOLUTE_PROGRAMMING, {})),
            ('G91', (COMMANDS.INCREMENTAL_PROGRAMMING, {})),
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
        result = parse_line(line)
        print('"{}" => {}'.format(line.strip(), result))


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
