# === SKELETON CODE FIXED ===
class Link:
    empty = ()

    def __init__(self, first, rest=empty):
        assert rest is Link.empty or isinstance(rest, Link)
        self.first = first
        self.rest = rest

    def __repr__(self):
        if self.rest is not Link.empty:
            rest_repr = ', ' + repr(self.rest)
        else:
            rest_repr = ''
        return 'Link(' + repr(self.first) + rest_repr + ')'

    # def __str__(self):
    #     string = '<'
    #     while self.rest is not Link.empty:
    #         string += str(self.first) + ' '
    #         self = self.rest
    #     return string + str(self.first) + '>'

# === SKELETON CODE TODO ===

def two_list(vals, amounts):
    """
    >>> two_list([1, 3, 2], [1, 1, 1])
    Link(1, Link(3, Link(2)))
    >>> two_list([1, 3, 2], [2, 2, 1])
    Link(1, Link(1, Link(3, Link(3, Link(2)))))
    
    """
    pass

