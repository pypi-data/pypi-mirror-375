import pytest

from yamja import lookup

TEST_DATA = {
    "a": {
        "b": {
            "c": 11,
            "d": 22,
        },
        "e": {
            "f": "this is a string",
            "g": "this is a\nmultiline\nstring",
        },
        "h": [555, 666, 777],
    },
    "z": [1, 2, 3],
}


def test_simple_lookup():
    assert lookup(TEST_DATA, "a.b.c") == 11


def test_lookup_with_default():
    assert lookup(TEST_DATA, "a.b.c", default=999) == 11


def test_lookup_with_default_and_no_value():
    assert lookup(TEST_DATA, "a.x.c", default=999) == 999


def test_lookup_exception():
    with pytest.raises(KeyError):
        lookup(TEST_DATA, "a.x.c")


def test_lookup_with_negative_index():
    assert lookup(TEST_DATA, "a.h.-1") == 777


def test_lookup_with_positive_index():
    assert lookup(TEST_DATA, "a.h.1") == 666
