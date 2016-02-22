from pytest import mark

from vclock.codec import DictCodec, ArrayCodec


@mark.parametrize("cls", [ArrayCodec, DictCodec])
def test_codec_order(cls):
    codec = cls()
    last_code = ''
    for i in range(1000):
        code = codec.encode_count(i)
        assert code > last_code
        assert codec.decode_count(code) == i
        last_code = code
