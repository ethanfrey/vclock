# for consistency, use Py3 definition that returns an iterator, not a list
from builtins import map
from future import standard_library
standard_library.install_aliases()

from itertools import zip_longest

from .codec import ArrayCodec, DictCodec


class VClockArray(object):
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
    codec = ArrayCodec()

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
        combined = list(map(max, (zip_longest(self.vector, clock.vector, fillvalue=0))))
        # then increment my local clock by one for this action
        combined[idx] += 1
        # and now wrap up the solution to return it safely
        return self.__class__(combined)

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

    def serialize(self):
        return self.codec.encode_vector(self.vector)

    @classmethod
    def deserialize(cls, line):
        return cls(cls.codec.decode_vector(line))

    def __gt__(self, clock):
        return self.after(clock)

    def __lt__(self, clock):
        return clock.after(self)

    def __eq__(self, clock):
        return self.vector == clock.vector

    def __str__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.vector)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.vector)


class VClockDict(VClockArray):
    """
    This is a more flexible form of the VClockArray, that uses hash tables instead of arrays to store the data.
    This means, for sparse sets (only a small percentage of actors touch any given object), this is much more
    efficient for storage and encoding.
    """
    code = DictCodec()

    def __init__(self, vector=None):
        if vector is None:
            self.vector = {}
        else:
            self.vector = dict(vector)

    def increment(self, idx):
        """
        Increment count by one for this slot.
        Extend vector if needed for this id.
        """
        result = VClock(self.vector)
        result.vector[idx] = result.vector.get(idx, 0) + 1
        return result

    def merge(self, clock, idx):
        """
        This merges together two vector clocks.
        idx is the index of the actor performing the merge
        """
        combined = dict()
        a, b = self.vector, clock.vector
        # first, make a dict with the max values for all elements from self and clock
        for key in set(a.keys()).union(b.keys()):
            combined[key] = max(a.get(key, 0), b.get(key, 0))
        # then increment my local clock by one for this action
        combined[idx] += 1
        # and now wrap up the solution to return it safely
        return self.__class__(combined)

    def after(self, clock):
        """
        clock must not have any actors that are not in self.
        all actors that are in both must have an equal or lower count in clock.
        they must not be equal.
        """
        a, b = self.vector, clock.vector
        missing = set(b.keys()).difference(a.keys())
        if missing:
            return False
        if a == b:
            return False
        for key, value in a.items():
            if b.get(key, 0) > value:
                return False
        return True


# set the default implementation
VClock = VClockDict
