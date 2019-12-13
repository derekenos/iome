
CHARS = {
    'A': (
        """

        1xx2
        x  x
        5xx4
        x  x
        0  3

        """,

        {
        }
    ),


    'B': (
        """

        1x2
        x  3
        x54
        x  7
        0x8

        """,

        {'4': '6'
        }
    ),


    'C': (
        """
        1xx2
        x
        x
        x
        0xx5
        """,

        {'1': '3',
         '0': '4'
        }
    ),


    'D': (
        """
        456
        3  7
        2  8
        1  9
        0BA
        """,

        {}
    ),


    'E': (
        """
        1xx2
        x
        4x5
        x
        0xx8
        """,

        {'1': '3',
         '4': '6',
         '0': '7',
        }
    ),


    'F': (
        """
        1xx2
        x
        4xx5
        x
        0
        """,

        {'1': '3',
         '4': '6',
        }
    ),

    'G': (
        """
         3x4
        2   5
        x
        x ExD
        1   C
         0xB
        """,

        {'4': '6',
         '3': '7',
         '2': '8',
         '1': '9',
         '0': 'A',
         'D': 'F',
         'C': 'G',
         'B': 'H',
        }
    ),


    'H': (
        """
        1  4
        x  x
        2xx3
        x  x
        0  5
        """,

        {'3': '6',
         '2': '7',
        }
    ),


    'I': (
        """
        4x3x5
          x
          x
          x
        0x2x1
        """,

        {'3': '6',
         '2': '7',
        }
    ),


    'J': (
        """
        5x4x6
          x
          x
       1  3
        02
        """,

        {'4': '7',
         '3': '8',
         '2': '9',
        }
    ),


    'K': (
        """
        1  4
        x x
        23
        x x
        0  6
        """,

        {'3': '57',
         '2': '8',
        }
    ),


    'L': (
        """
        1
        x
        x
        x
        0xx3
        """,

        {'0': '2',
        }
    ),


    'M': (
        """
        12   45
        x x x x
        x  3  x
        x     x
        0     6
        """,

        {'5': '7',
         '4': '8',
         '3': '9',
         '2': 'A',
         '1': 'B',
        }
    ),


    'N': (
        """
        1   3
        xx  x
        x x x
        x  xx
        0   2
        """,

        {'2': '4',
         '1': '5',
        }
    ),


    'O': (
        """
         3xx4
        2    5
        x    x
        1    6
         0xx7
        """,

        {}
    ),


    'P': (
        """
        1xxx2
        x    3
        x    4
        6xxx5
        x
        x
        0
        """,

        {}
    ),


    'Q': (
        """
         3xx4
        2    5
        x    x
        1  8 6
         0x 7
             9
        """,

        {'7': 'A',
        }
    ),


    'R': (
        """
        1xxx2
        x    3
        x    4
        9x6x5
        x  x
        x   x
        0    7
        """,

        {'6': '8',
        }
    ),


    'S': (
        """
         AxxB
        9    C
        8
         7xx6
             5
        1    4
         0xx3
        """,

        {'0': '2',
         'B': 'D',
         'A': 'E',
         '9': 'F',
         '8': 'G',
         '7': 'H',
         '6': 'I',
         '5': 'J',
         '4': 'K',
         '3': 'L',
        }
    ),

    'T': (
        """
        2x1x3
          x
          x
          x
          0
        """,

        {'1': '4',
        }
    ),


    'U': (
        """
        2    7
        x    x
        x    x
        1    6
         0xx5
        """,

        {'1': '3',
         '0': '4',
         '6': '8',
         '5': '9'
        }
    ),


    'U': (
        """
        1     3
         x   x
          x x
           0
        """,

        {'0': '2',
        }
    ),


    'W': (
        """
        2     8
        x     x
        x  5  x
        1 x x 7
         0   6
        """,

        {'1': '3',
         '0': '4',
         '7': '9',
         '6': 'A',
         '5': 'B'
        }
    ),


    'X': (
        """
        3   1
         x x
          2
         x x
        0   4
        """,

        {'2': '5',
        }
    ),


    'Y': (
        """
        3   1
         x x
          2
         x
        0
        """,

        {'2': '4',
        }
    ),


    'Z': (
        """
        2xxx1
           x
          x
         x
        0xxx5
        """,

        {'1': '3',
         '0': '4',
        }
    ),

}
