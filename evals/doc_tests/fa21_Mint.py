# === SKELETON CODE FIXED ===

class Mint:
    """A mint creates coins by stamping on years.

    The update method sets the mint's stamp to Mint.present_year.
    """
    present_year = 2021

    def __init__(self):
        self.update()

    def create(self, kind):
        "*** YOUR CODE HERE ***"

    def update(self):
        "*** YOUR CODE HERE ***"


class Coin:
    def __init__(self, year):
        self.year = year

    def worth(self):
        "*** YOUR CODE HERE ***"
        

class Nickel(Coin):
    cents = 5

class Dime(Coin):
    cents = 10


mint = Mint()
dime = mint.create(Dime)
Mint.present_year = 2101     # Time passes
nickel = mint.create(Nickel) # still stamped 2021
mint.update()                # stamp updated to 2101
Mint.present_year = 2176     # More time passes
# upgrade all dimes
Dime.cents = 20


"""
>>> mint.year
2021
>>> dime.year
2021
>>> nickel.year
2021
>>> nickel.worth()
35
>>> mint.create(Dime).worth()
35
>>> Mint().create(Dime).worth()
10
>>> dime.worth()
115
>>> dime.worth()
125

"""

# === SKELETON CODE TODO ===

class Mint:
    """A mint creates coins by stamping on years.

    The update method sets the mint's stamp to Mint.present_year.
    """
    present_year = 2021

    def __init__(self):
        self.update()

    def create(self, kind):
        "*** YOUR CODE HERE ***"

    def update(self):
        "*** YOUR CODE HERE ***"
