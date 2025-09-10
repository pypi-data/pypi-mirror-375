from deliciousbytes import (
    String,
    ASCII,
    UTF8,
    UTF16,
    UTF32,
    Unicode,
    UInt,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
    Int,
    Int8,
    Int16,
    Int32,
    Int64,
    Char,
    UnsignedChar,
    SignedChar,
    Short,
    UnsignedShort,
    SignedShort,
    Long,
    UnsignedLong,
    SignedLong,
    LongLong,
    UnsignedLongLong,
    SignedLongLong,
    Size,
    UnsignedSize,
    SignedSize,
    Float,
    Float16,
    Float32,
    Float64,
    Double,
    Bytes,
    Bytes8,
    Bytes16,
    Bytes32,
    Bytes64,
    Bytes128,
    Bytes256,
)

from deliciousbytes.utilities import (
    hexbytes,
    print_hexbytes,
    isinstantiable,
)


def test_hexbytes():
    """Test the 'hexbytes' utility function."""

    value: bytes = b"\x01\x02\x03\x04\x05\x06"

    assert hexbytes(value) == "[> 01 02 03 04 05 06 <]"


def test_hexbytes_with_prefixing_enabled():
    """Test the 'hexbytes' utility function with the optional 'prefix' option."""

    value: bytes = b"\x01\x02\x03\x04\x05\x06"

    # The 'prefix' option changes the output to look like a formatted bytes string:
    assert hexbytes(value, prefix=True) == r'b"\x01\x02\x03\x04\x05\x06"'


def test_hexbytes_with_limiting_enabled():
    """Test the 'hexbytes' utility function with the optional 'limit' option."""

    value: bytes = b"\x01\x02\x03\x04\x05\x06"

    # The optional `limit` option, limits how many bytes are included in the output:
    assert hexbytes(value, limit=4) == "[> 01 02 03 04 ... <]"


def test_print_hexbytes(capsys):
    """Test the 'print_hexbytes' utility function."""

    value: bytes = b"\x01\x02\x03\x04\x05\x06"

    print_hexbytes(value)

    captured = capsys.readouterr()

    assert captured.out == "[> 01 02 03 04 05 06 <]\n"


def test_print_hexbytes_with_prefixing_enabled(capsys):
    """Test the 'print_hexbytes' utility function with the optional 'prefix' option."""

    value: bytes = b"\x01\x02\x03\x04\x05\x06"

    print_hexbytes(value, prefix=True)

    captured = capsys.readouterr()

    assert captured.out == r'b"\x01\x02\x03\x04\x05\x06"' + "\n"


def test_print_hexbytes_with_limiting_enabled(capsys):
    """Test the 'print_hexbytes' utility function with the optional 'limit' option."""

    value: bytes = b"\x01\x02\x03\x04\x05\x06"

    print_hexbytes(value, limit=4)

    captured = capsys.readouterr()

    assert captured.out == "[> 01 02 03 04 ... <]\n"


def test_isinstantiable_string():
    """Test the 'isinstantiable' utility function with string types."""

    value: str = "Hello World"

    assert isinstance(value, str)
    assert value == "Hello World"

    assert isinstantiable(value, String)
    assert isinstantiable(value, ASCII)
    assert isinstantiable(value, UTF8)
    assert isinstantiable(value, UTF16)
    assert isinstantiable(value, UTF32)
    assert isinstantiable(value, Unicode)


def test_isinstantiable_integer():
    """Test the 'isinstantiable' utility function with integer types."""

    value: int = 123

    assert isinstance(value, int)
    assert value == 123

    assert isinstantiable(value, Int)
    assert isinstantiable(value, Int8)
    assert isinstantiable(value, Int16)
    assert isinstantiable(value, Int32)
    assert isinstantiable(value, Int64)

    assert isinstantiable(value, UInt)
    assert isinstantiable(value, UInt8)
    assert isinstantiable(value, UInt16)
    assert isinstantiable(value, UInt32)
    assert isinstantiable(value, UInt64)

    assert isinstantiable(value, Char)
    assert isinstantiable(value, UnsignedChar)
    assert isinstantiable(value, SignedChar)

    assert isinstantiable(value, Short)
    assert isinstantiable(value, UnsignedShort)
    assert isinstantiable(value, SignedShort)

    assert isinstantiable(value, Long)
    assert isinstantiable(value, UnsignedLong)
    assert isinstantiable(value, SignedLong)

    assert isinstantiable(value, LongLong)
    assert isinstantiable(value, UnsignedLongLong)
    assert isinstantiable(value, SignedLongLong)

    assert isinstantiable(value, Size)
    assert isinstantiable(value, UnsignedSize)
    assert isinstantiable(value, SignedSize)


def test_isinstantiable_float():
    """Test the 'isinstantiable' utility function with float types."""

    value: int = 123.456

    assert isinstance(value, float)
    assert value == 123.456

    assert isinstantiable(value, Float)
    assert isinstantiable(value, Float16)
    assert isinstantiable(value, Float32)
    assert isinstantiable(value, Float64)

    assert isinstantiable(value, Double)


def test_isinstantiable_bytes():
    """Test the 'isinstantiable' utility function with bytes types."""

    value: bytes = b"\x01\x02\x03\x04"

    assert isinstance(value, bytes)
    assert value == b"\x01\x02\x03\x04"

    assert isinstantiable(value, Bytes)
    assert isinstantiable(value, Bytes8)
    assert isinstantiable(value, Bytes16)
    assert isinstantiable(value, Bytes32)
    assert isinstantiable(value, Bytes64)
    assert isinstantiable(value, Bytes128)
    assert isinstantiable(value, Bytes256)
