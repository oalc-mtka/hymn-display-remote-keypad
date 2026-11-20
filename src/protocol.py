# The UART1 byte protocol, mirroring the original C firmware for the display controller.
# Pure functions only: no MicroPython-specific imports, so tests run on a laptop.

# One byte per key on the Bottom Display.
KEYPAD_CODES = {
    '0': 0x17, '1': 0x33, '2': 0x67, '3': 0x19, '4': 0x32,
    '5': 0x65, '6': 0x0C, '7': 0x5F, '8': 0x63, '9': 0x5E
}
KEYPAD_SEND = bytes([0x5D])  # defined by the C firmware, never sent (#7)
KEYPAD_CLEAR = bytes([0x06])

# 7-segment bit patterns for each digit on the Top Display.
SEVEN_SEG_CODES = {
    '0': 0b00111111, '1': 0b00000110, '2': 0b01011011, '3': 0b01001111, '4': 0b01100110,
    '5': 0b01101101, '6': 0b01111101, '7': 0b00000111, '8': 0b01111111, '9': 0b01100111
}
SEVEN_SEG_BLANK = 0b00000000

# clearTop(): three blank bytes with bit 7 cleared, then set. Always sent twice.
CLEAR_TOP = bytes([0x00, 0x00, 0x00, 0x80, 0x80, 0x80]) * 2


def parse_song_number(text):
    """Returns the Song Number in `text` with leading zeros stripped ("007" -> "7").

    Raises ValueError unless `text` is digits only and its value is 1-999.
    """
    if not text.isdigit():
        raise ValueError("not digits: %r" % text)
    value = int(text)
    if not 1 <= value <= 999:
        raise ValueError("out of range: %r" % text)
    return str(value)


def keypad_bytes(song_number):
    """The Bottom Display keypad codes for a Song Number from parse_song_number(), one byte per digit."""
    return bytes([KEYPAD_CODES[digit] for digit in song_number])


def top_frame(song_number):
    """The sendToTop() frame for a Song Number from parse_song_number(), already doubled.

    6 bytes: the 7-segment patterns for the third, second and first position with bit 7
    cleared, then the same with bit 7 set. Leading positions are blank. Always sent twice.
    """
    padded = ' ' * (3 - len(song_number)) + song_number  # str.rjust isn't in MicroPython
    first, second, third = [SEVEN_SEG_CODES.get(c, SEVEN_SEG_BLANK) for c in padded]
    frame = bytes([third & 0x7F, second & 0x7F, first & 0x7F,
                   third | 0x80, second | 0x80, first | 0x80])
    return frame * 2
