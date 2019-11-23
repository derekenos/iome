

def first_false_index(pred, it):
    """Return the index of the first element that doesn't satisfy the predicate
    , or if no unsatisfactory element was found, return the first index beyond
    the length of the iterable to optimize for blind slicing.
    """
    i = 0
    max_i = len(it) - 1
    while i <= max_i and pred(it[i]):
        i += 1
    return i


def take_while(pred, it):
    """Consume elements until the predicate becomes false and return both the
    consumed and unconsumed elements.
    """
    i = first_false_index(pred, it)
    return it[:i], it[i:]


def drop_while(pred, it):
    """Ignore elements until the predicate becomes false and return the
    remaining elements.
    """
    i = first_false_index(pred, it)
    return it[i:]


###############################################################################
# Tests
###############################################################################

from unittest import TestCase


class UtilsTester(TestCase):
    def test_first_false_index(self):
        pred = lambda x: x < 2

        x = []
        expected = 0
        self.assertEqual(first_false_index(pred, x), expected)

        x = [0, 1]
        expected = 2
        self.assertEqual(first_false_index(pred, x), expected)

        x = [0, 1, 2]
        expected = 2
        self.assertEqual(first_false_index(pred, x), expected)


    def test_take_while(self):
        pred = lambda x: x < 2

        x = []
        expected = ([], [])
        self.assertEqual(take_while(pred, x), expected)

        x = [0, 1]
        expected = ([0, 1], [])
        self.assertEqual(take_while(pred, x), expected)

        x = [0, 1, 2, 3, 4]
        expected = ([0, 1], [2, 3, 4])
        self.assertEqual(take_while(pred, x), expected)


    def test_drop_while(self):
        pred = lambda x: x < 2

        x = []
        expected = []
        self.assertEqual(drop_while(pred, x), expected)

        x = [0, 1]
        expected = []
        self.assertEqual(drop_while(pred, x), expected)

        x = [0, 1, 2, 3, 4]
        expected = [2, 3, 4]
        self.assertEqual(drop_while(pred, x), expected)
