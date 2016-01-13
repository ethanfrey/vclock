from vclock import VClock


def _assert_order(a, b):
    print(a)
    print(b)
    assert b.after(a)
    assert b > a
    assert a.before(b)
    assert a < b


def test_basic_increment():
    one = VClock()
    two = one.copy()
    assert isinstance(two, VClock)
    assert one == two
    two.increment(1)
    _assert_order(one, two)


def test_multiple_increments():
    start = VClock()
    one = start.copy()
    one.increment(1).increment(3)
    two = one.copy()
    assert one == two
    two.increment(2).increment(0)
    _assert_order(one, two)

