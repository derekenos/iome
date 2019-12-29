
# TODO: define explicit entry point in char def instead of implicit return to 0


def char_def_to_points(char_def):
    """Return a generator of (<x>, <y>) coordinate tuples that
    represent the path defined by the specified ASCII art character definition.

    For example, for this char_def with an empty revisit_map:

    (
      '''

      1xx2
      x  x
      5xx4
      x  x
      0  3

      ''',

      {}
    )

    Return a generator for the points:

      [(0, 0), (0, 4), (3, 4), (3, 0), (3, 2), (0, 2), (0, 0)]
                                      back to the start ^

    """
    ascii_art, revisit_map = char_def
    rows = ascii_art.splitlines()

    # Remove any leading and/or trailing empty rows.
    while rows and rows[0].strip() == '':
        rows = rows[1:]
    while rows and rows[-1].strip() == '':
        rows = rows[:-1]

    # Return if character contains no data.
    if not rows:
        return

    # Collect all the order character coordinates and determine the column
    # position of the leftmost non-empty character.
    order_char_coord_tuples = []
    min_nonempty_col_num = max(len(row) for row in rows)
    IGNORE_CHARS = (' ', 'x')
    for row_num, row in enumerate(rows):
        for col_num, char in enumerate(row):
            if char in IGNORE_CHARS:
                continue
            if col_num < min_nonempty_col_num:
                min_nonempty_col_num = col_num
            order_char_coord_tuples.append((char, (col_num, row_num)))
            # If this order char is defined in the revisit_map, duplicate its
            # coordinate under the specified revisit order value(s).
            if char in revisit_map:
                for order_char in revisit_map[char]:
                    order_char_coord_tuples.append(
                        (order_char, (col_num, row_num))
                    )

    # Subtract the number of leading empty columns from the x coordinate values
    # and invert the y axis coordinates to place the grid origin at the
    # bottom left.
    num_rows = len(rows)
    order_char_coord_tuples = [
        (order_char, (x - min_nonempty_col_num, num_rows - 1 - y))
        for (order_char, (x, y)) in order_char_coord_tuples
    ]

    # Sort the collected coords by order chars.
    order_char_coord_tuples = sorted(order_char_coord_tuples)

    # Duplicate the first coord at the end so that we always return back where
    # we started.
    order_char_coord_tuples.append(order_char_coord_tuples[0])

    # Yield the coordinates.
    for _, coord in order_char_coord_tuples:
        yield coord
