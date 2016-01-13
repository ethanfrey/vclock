from vclock import VClock


def test_serialize_deserialize():
    orig = VClock([3, 4, 1])
    store = orig.serialize()
    assert store
    loaded = VClock.deserialize(store)
    assert loaded == orig


def test_serialization_order():
    one = VClock([1, 0, 2])
    two = one.increment(1)
    assert two > one
    one_store = one.serialize()
    two_store = two.serialize()
    assert two_store > one_store
