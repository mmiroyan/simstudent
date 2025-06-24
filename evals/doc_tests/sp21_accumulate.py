# === SKELETON CODE FIXED ===
from operator import add, mul, sub

square = lambda x: x * x

identity = lambda x: x

triple = lambda x: 3 * x

increment = lambda x: x + 1

# === SKELETON CODE TODO ===

def accumulate(combiner, base, n, term):
    """Return the result of combining the first n terms in a sequence and base.
    The terms to be combined are term(1), term(2), ..., term(n).  combiner is a
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
    >>> accumulate(lambda x, y: 2 * (x + y), 2, 3, square)
    58
    >>> accumulate(lambda x, y: (x + y) % 17, 19, 20, square)
    16
    
    """
    pass