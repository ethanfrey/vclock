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


@mark.parametrize("cls", [VClockArray, VClockDictInt])
def test_basic_increment(cls):
    one = cls()
    two = one.increment(1)
    assert two != one
    _assert_order(one, two)
    # should have two places [0, 1]
    # assert len(two.vector) == 2


@mark.parametrize("cls", [VClockArray, VClockDictInt])
def test_multiple_increments(cls):
    start = cls()
    one = start.increment(1).increment(3)
    two = one.increment(2).increment(0)
    _assert_order(one, two)
    # should have four places [0, 1, 0, 1]
    # assert len(one.vector) == 4
    # assert len(two.vector) == 4


@mark.parametrize("cls", [VClockArray, VClockDictInt])
def test_concurrent_increments(cls):
    one = cls().increment(0).increment(2)
    two = one.increment(4)
    three = one.increment(2)
    assert two > one
    assert three > one
    assert not three > two
    assert not two > three
    assert three.concurrent(two)


def test_dict_strings():
    one = VClockDict().increment('a2').increment('b5')
    two = one.increment('cc')
    three = one.increment('af')
    _assert_order(one, two)
    _assert_order(one, three)
    assert not three > two
    assert not two > three
    assert three.concurrent(two)
