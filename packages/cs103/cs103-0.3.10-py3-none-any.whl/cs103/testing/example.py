# Testing example for testing utility wrapper

from testing import *
from typing import NamedTuple

Named = NamedTuple('Named', [('a', int), ('b', str)])
N1 = Named(0, "hi")
T1 = (0, "hi")

def area(width, height):
    """
    Real, Real -> Real

    Produces the area of a rectangle with the given
    width and height
    """
    return width * height

expect(area(0, 0), 0)
expect(area(2, 5), 10)
expect(area(1.2, 3.1), 3.72)
expect(N1, N1)
expect(T1, T1)

# Failing tests as examples
expect(area(1, 1), 2)
expect(area(1, 2), 1)
expect(N1, T1)
expect(1.02, [1,2,3])

summary()
