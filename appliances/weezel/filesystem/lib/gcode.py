"""Weezel-specific gcode decoding functions.
"""

import re
from collections import deque
from decimal import Decimal
from enum import Enum
from argparse import (
    ArgumentParser,
    FileType,
)


# Define the supported commands that we'll decode.
COMMANDS = Enum('Commands', (
    'EMPTY',
    'COMMENT',
    'RAPID_POSITIONING',
    'LINEAR_INTERPOLATION',
    'PROGRAMMING_IN_INCHES',
    'PROGRAMMING_IN_MILLIMETERS',
    'UNSUPPORTED',
))

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
                params = {k: Decimal(v) if v is not None else v for k, v in params.items()}
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
    CMDS = COMMANDS
    for line, expected in (
            ('', (CMDS.EMPTY, {})),
            (' ', (CMDS.EMPTY, {})),
            ('; A comment', (CMDS.COMMENT, { 'text': 'A comment' })),

            ('G0 X20.2 Y30.3', (CMDS.RAPID_POSITIONING, {
                'x': Decimal('20.2'),
                'y': Decimal('30.3')
            })),

            ('G1 X10.1 Y40.4',
             (CMDS.LINEAR_INTERPOLATION, {
                 'x': Decimal('10.1'),
                 'y': Decimal('40.4'),
                 'z': None,
                 'feed_rate': None,
             })),

            ('G1 X-10.1 Y-40.4 Z20',
             (CMDS.LINEAR_INTERPOLATION, {
                 'x': Decimal('-10.1'),
                 'y': Decimal('-40.4'),
                 'z': Decimal('20'),
                 'feed_rate': None,
             })),

            ('G1 X-10.1 Y-40.4 Z20 F30',
             (CMDS.LINEAR_INTERPOLATION, {
                 'x': Decimal('-10.1'),
                 'y': Decimal('-40.4'),
                 'z': Decimal('20'),
                 'feed_rate': Decimal('30'),
             })),

            ('G1 Z20',
             (CMDS.LINEAR_INTERPOLATION, {
                 'x': None,
                 'y': None,
                 'z': Decimal('20'),
                 'feed_rate': None,
             })),

            ('G1 Z20 F30',
             (CMDS.LINEAR_INTERPOLATION, {
                 'x': None,
                 'y': None,
                 'z': Decimal('20'),
                 'feed_rate': Decimal('30'),
             })),

    ):
        _assert(parse_line(line), expected)


if __name__ == '__main__':
    from argparse import ArgumentParser
    from inspect import isfunction
    from sys import stdout

    parser = ArgumentParser()
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if not args.test:
        parser.error('specify --test if you want to run the tests')

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
