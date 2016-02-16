from __future__ import print_function

from pytest import mark
from vclock import VClockArray, VClockDict, VClockDictInt


def _assert_serialization_order_valid(events):
    """
    sort all items by their serialized keys, then compare
    an item must be "before" or "concurrent" with all items that come after it in the list
    an item must be "after" or "concurrent" with all items that come before it in the list
    """
    events.sort(key=lambda x: x.serialize())
    for idx, event in enumerate(events):
        # compare to all items before it in the list
        for earlier in events[:idx]:
            assert event.after(earlier) or event.concurrent(earlier)
        # compare to all items after it in the list
        for later in events[idx+1:]:
            assert event.before(later) or event.concurrent(later)


@mark.parametrize("cls,init", [
    (VClockArray, [3, 4, 1]),
    (VClockDictInt, {0: 3, 1: 4, 2: 1}),
    (VClockDict, {'aa': 3, 'ab': 4, 'ac': 1})
    ])
def test_serialize_deserialize(cls, init):
    orig = cls(init)
    store = orig.serialize()
    assert store
    loaded = cls.deserialize(store)
    assert loaded == orig


@mark.parametrize("cls,init,idx", [
    (VClockArray, [3, 4, 1], 1),
    (VClockDictInt, {0: 3, 1: 4, 2: 1}, 1),
    (VClockDict, {'aa': 3, 'ab': 4, 'ac': 1}, 'ab')
    ])
def test_serialization_order(cls, init, idx):
    one = cls(init)
    two = one.increment(idx)
    assert two > one
    one_store = one.serialize()
    two_store = two.serialize()
    assert two_store > one_store

    # all causes and effects should be clear, but no valid tests on concurrent items


@mark.parametrize("cls,A,B", [
    (VClockArray, 0, 1),
    (VClockDictInt, 0, 1),
    (VClockDict, 'aa', 'ab')
    ])
def test_serialized_merge_cause_effect(cls, A, B):
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

    # all causes and effects should be clear, but no valid tests on concurrent items
    assert merge.serialize() > a1.serialize()
    assert merge.serialize() > b1.serialize()
    assert a2.serialize() > merge.serialize()
    assert b2.serialize() > merge.serialize()


@mark.parametrize("cls,A,B,C", [
    (VClockArray, 0, 1, 2),
    (VClockDictInt, 0, 1, 2),
    (VClockDict, 'aa', 'cb', 'fe')
    ])
def test_serialized_three_way_merging(cls, A, B, C):
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
    assert merge.serialize() > a1.serialize()
    assert merge.serialize() > a2.serialize()
    assert merge.serialize() > b1.serialize()
    assert merge.serialize() > b2.serialize()
    assert merge.serialize() > b3.serialize()
    assert merge.serialize() > c1.serialize()

    # these were all after the merge
    assert a4.serialize() > merge.serialize()
    assert b5.serialize() > merge.serialize()
    assert c4.serialize() > merge.serialize()
    assert c5.serialize() > merge.serialize()

    # now, let's try a global query, that all items ordered in a possible global ordering
    events = [a1, a2, a3, a4, b1, b2, b3, b4, b5, c1, c2, c3, c4, c5]
    _assert_serialization_order_valid(events)


@mark.parametrize("cls", [VClockArray, VClockDictInt])
def test_crazy_merge_with_ordering(cls):
    A, B, C, D = 0, 1, 2, 3
    a1 = cls().increment(A)
    b1 = a1.increment(B)
    b2 = b1.increment(B)
    c1 = b1.increment(C)
    d1 = b2.increment(D)
    a2 = a1.increment(A)
    d2 = d1.increment(D)
    b3 = b2.merge(c1, B)
    a3 = a2.merge(d2, A)
    c2 = c1.merge(d2, C)
    a4 = a3.increment(A)
    b4 = b3.merge(c2, B)
    a5 = a4.merge(b3, A)
    d3 = d2.merge(a5, D)
    d4 = d3.merge(b4, D)

    # test a few random objects
    assert a4.after(b2)
    assert d3.after(c1)
    assert a5.concurrent(b4)
    assert b3.concurrent(c2)
    assert b4.after(d2)

    # make sure serialization order is a possible ordering
    events = [a1, b1, b2, c1, d1, a2, d2, b3, a3, c2, a4, b4, a5, d3, d4]
    _assert_serialization_order_valid(events)
