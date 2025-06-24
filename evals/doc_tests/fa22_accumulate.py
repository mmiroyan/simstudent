# === SKELETON CODE FIXED ===
from operator import add, mul

square = lambda x: x * x

identity = lambda x: x

triple = lambda x: 3 * x

increment = lambda x: x + 1

# === SKELETON CODE TODO ===

def accumulate(merger, start, n, term):
    """Return the result of merging the first n terms in a sequence and start.
    The terms to be merged are term(1), term(2), ..., term(n). merger is a
    two-argument commutative function.

    >>> accumulate(add, 0, 5, identity)  
    15
    >>> accumulate(add, 11, 5, identity)
    26
    >>> accumulate(add, 11, 0, identity)
    11
    >>> accumulate(add, 11, 3, square)  
    25
    >>> accumulate(mul, 2, 3, square)  
    72
    >>> accumulate(lambda x, y: x + y + 1, 2, 3, square)
    19
    >>> accumulate(lambda x, y: 2 * x * y, 2, 3, square)
    576
    >>> accumulate(lambda x, y: (x + y) % 17, 19, 20, square)
    16
    
    """
    pass
