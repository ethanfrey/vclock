class VClock(object):
    """
    This is a basic model of a vector clock, that is also able to
    serialize itself.  The serialization options are provided in
    the constructor and cannot change without breaking compatibility
    with existing strings.

    The objects offer the following methods:
    * increment(id) - Update the clock by one for this actor.
    * merge(clock) - Merge two clocks and create a new clock that is a
        valid child of both of them.
    * concurrent(clock) - Returns True iff there is no causal relation between
        these two clocks.
    * before(clock), < - Returns True iff there is a causal relationship
        between self and clock.
    * after(clock), > - Returns True iff there is a causal relationship
        between clock and self.

    You can also convert clocks to strings with the following functions:
    * serialize() - Return an ASCII representation of this clock
    * deserialize(bin) - Re-create a clock from an ASCII string

    Note that the < and > operations work for the serialized strings as well.
    However, the string representation of concurrent clocks may be before
    or after one another. (This relaxes the iff in before/after above to
    simply if)

    Note all ids are digits, and for efficiency should be kept below 10 or so.
    Every actor modifying this clock needs its own unique id, generating and
    maintaining these is outside the scope of this class.
    """
    DIGITS = 4
    USE_HEX = True

    def __init__(self, vector=None):
        if vector is None:
            self.vector = []
        else:
            self.vector = list(vector)

    def increment(self, id):
        return self

    def merge(self, clock):
        return self

    def concurrent(self, clock):
        return True

    def before(self, clock):
        return False

    def after(self, clock):
        return False

    def serialize(self):
        return 'VCLOCK'

    @classmethod
    def deserialize(string):
        return VClock()

    def copy(self):
        return VClock(self.vector)

    def __gt__(self, clock):
        return self.after(clock)

    def __lt__(self, clock):
        return self.before(clock)

    def __eq__(self, clock):
        return self.vector == clock.vector

    def __str__(self):
        return '<VClock: {}>'.format(self.vector)
