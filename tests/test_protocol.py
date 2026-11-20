# Run from the repo root on MicroPython's Unix port or CPython:
#   micropython tests/test_protocol.py
#   python3 tests/test_protocol.py
import sys

sys.path.insert(0, "src")

import protocol


def raises_value_error(text):
    try:
        protocol.parse_song_number(text)
    except ValueError:
        return True
    return False


def test_parse_strips_leading_zeros():
    assert protocol.parse_song_number("7") == "7"
    assert protocol.parse_song_number("007") == "7"
    assert protocol.parse_song_number("120") == "120"
    assert protocol.parse_song_number("999") == "999"


def test_parse_rejects_non_song_numbers():
    for text in ("", "0", "000", "1000", "12a", "-5", " 5", "1.5"):
        assert raises_value_error(text), text


def test_keypad_bytes_one_per_digit():
    assert protocol.keypad_bytes("7") == bytes([0x5F])
    assert protocol.keypad_bytes("120") == bytes([0x33, 0x67, 0x17])


def test_top_frame_pads_and_doubles():
    # "7" shows as blank, blank, 7: third position first, bit 7 cleared then set.
    frame = bytes([0b00000111, 0x00, 0x00, 0b10000111, 0x80, 0x80])
    assert protocol.top_frame("7") == frame * 2


def test_top_frame_three_digits():
    one, two, three = 0b00000110, 0b01011011, 0b01001111
    frame = bytes([three, two, one, three | 0x80, two | 0x80, one | 0x80])
    assert protocol.top_frame("123") == frame * 2


def test_clear_top():
    assert protocol.CLEAR_TOP == bytes([0, 0, 0, 0x80, 0x80, 0x80, 0, 0, 0, 0x80, 0x80, 0x80])


if __name__ == "__main__":
    tests = [(name, f) for name, f in sorted(globals().items()) if name.startswith("test_")]
    for name, test in tests:
        test()
        print("ok", name)
    print(len(tests), "passed")
