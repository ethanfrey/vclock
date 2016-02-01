# TODO: py2/3 compatability with builtins, __future__
# http://python-future.org/quickstart.html
# from builtins import map
try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest


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

    *The VClock object is immutable, all modifying methods return a new object*

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

    def _extend(self, size):
        """
        Return a copy of this vector with at least the given size.
        """
        result = self.vector
        extend = size - len(self.vector)
        if extend > 0:
            result += [0] * extend
        return result

    def increment(self, idx):
        """
        Increment count by one for this slot.
        Extend vector if needed for this id.
        """
        # extend vector if needed
        result = VClock(self._extend(idx + 1))
        # now increment index
        result.vector[idx] += 1
        return result

    def merge(self, clock, idx):
        """
        This merges together two vector clocks.
        idx is the index of the actor performing the merge
        """
        # first, make an array with the max values for all elements from self and clock
        combined = map(max, (zip_longest(self.vector, clock.vector, fillvalue=0)))
        # then increment my local clock by one for this action
        combined[idx] += 1
        # and now wrap up the solution to return it safely
        return VClock(combined)

    def concurrent(self, clock):
        return not (clock.after(self) or self.after(clock))

    def before(self, clock):
        """
        self must not have any actors that are not in clock.
        all actors that are in both must have an equal or lower count in self.
        they must not be equal.
        """
        return clock.after(self)

    def after(self, clock):
        """
        clock must not have any actors that are not in self.
        all actors that are in both must have an equal or lower count in clock.
        they must not be equal.
        """
        v1 = clock.vector
        v2 = self.vector
        if len(v1) > len(v2):
            return False
        if v1 == v2:
            return False
        for first, second in zip(v1, v2):
            if first > second:
                return False
        return True

    def _encode(self, val):
        # now, 4 character in decimal
        return '{:04}'.format(val)

    @classmethod
    def _decode(cls, val):
        # parse string as decimal
        return int(val, 10)

    def serialize(self):
        return ''.join(self._encode(x) for x in self.vector)

    @classmethod
    def deserialize(cls, line):
        n = cls.DIGITS
        vector = (cls._decode(line[i:i+n]) for i in range(0, len(line), n))
        return cls(vector)

    def __gt__(self, clock):
        return self.after(clock)

    def __lt__(self, clock):
        return clock.after(self)

    def __eq__(self, clock):
        return self.vector == clock.vector

    def __str__(self):
        return '<VClock: {}>'.format(self.vector)

    def __repr__(self):
        return '<VClock: {}>'.format(self.vector)
