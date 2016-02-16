from __future__ import print_function

from pytest import mark
from vclock import VClockArray, VClockDict, VClockDictInt


def _assert_order(a, b):
    print(a)
    print(b)
    assert b.after(a)
    assert b > a
    assert a.before(b)
    assert a < b




@mark.parametrize("cls,A,B,C", [
    # merger is the highest key
    (VClockArray, 0, 1, 2),
    (VClockDictInt, 0, 1, 2),
    (VClockDict, 'aa', 'b7', 'dd'),
    # merger is the lowest key
    (VClockArray, 2, 1, 0),
    (VClockDictInt, 2, 1, 0),
    (VClockDict, 'dd', 'b7', 'aa'),
    ])
def test_third_party_merge(cls, A, B, C):
    """
    Two actions before the merge (Causes) - a1, b1
    Two actions after the merge (Effects) - a2, b2
    Make sure they are all classified properly
    """
    start = cls()
    a = start.increment(A)
    b = start.increment(B)
    merged = a.merge(b, C)
    _assert_order(a, merged)
    _assert_order(b, merged)
    _assert_order(start, a)
    _assert_order(start, b)
    assert a.concurrent(b)
    assert merged.serialize() > a.serialize()
    assert merged.serialize() > b.serialize()


@mark.parametrize("cls,A,B", [
    (VClockArray, 0, 1),
    (VClockDictInt, 0, 1),
    (VClockDict, 'aa', 'b7'),
    ])
def test_merge_cause_effect(cls, A, B):
    """
    Two actions before the merge (Causes) - a1, b1
    Two actions after the merge (Effects) - a2, b2
    Make sure they are all classified properly
    """
    a1 = cls().increment(A)
    b1 = cls().increment(B)
    merge = a1.merge(b1, A)
    a2 = merge.increment(A)
    b2 = merge.increment(B)

    # all causes and effects should be clear
    _assert_order(a1, merge)
    _assert_order(b1, merge)
    _assert_order(merge, a2)
    _assert_order(merge, b2)
    _assert_order(a1, a2)
    _assert_order(b1, a2)
    _assert_order(a1, b2)
    _assert_order(b1, b2)

    # parallel actions are also clear
    assert a1.concurrent(b1)
    assert a2.concurrent(b2)


@mark.parametrize("cls,A,B,C", [
    (VClockArray, 0, 1, 2),
    (VClockDictInt, 0, 1, 2),
    (VClockDict, 'A3', 'AF', 'B1'),
    ])
def test_three_way_merging(cls, A, B, C):
    """
    Based on diagram from https://en.wikipedia.org/wiki/Vector_clock
    Let's make sure all causes, effects, and concurrency are properly classified
    """
    # first, everyone touches this data once
    c1 = cls().increment(C)
    b1 = c1.increment(B)
    b2 = b1.increment(B)
    a1 = b2.increment(A)
    # now we start a bit in parallel to be merged together
    b3 = b2.increment(B)
    a2 = a1.increment(A)
    # these are concurrent with the merge
    c2 = c1.merge(b3, C)
    c3 = c2.increment(C)
    a3 = a2.merge(c3, A)
    # merge event and children
    merge = b4 = b3.merge(a2, B)
    b5 = b4.increment(B)
    c4 = c3.merge(b5, C)
    c5 = c4.increment(C)
    a4 = a3.merge(c5, A)

    # okay, confused yet??? Let's asset the causes and effects of the merge
    # these were all before the merge
    _assert_order(a1, merge)
    _assert_order(a2, merge)
    _assert_order(b1, merge)
    _assert_order(b2, merge)
    _assert_order(b3, merge)
    _assert_order(c1, merge)

    # these were all after the merge
    _assert_order(merge, a4)
    _assert_order(merge, b5)
    _assert_order(merge, c4)
    _assert_order(merge, c5)

    # and these were concurrent with the merge
    assert merge.concurrent(a3)
    assert merge.concurrent(c2)
    assert merge.concurrent(c3)

