import base64
import math

from .country import Country
from .color import Color


def total_needed_pixels(level: int) -> int:
    """Return the total number of pixels a user needs to place to reach the
    given `level`.
    """
    return math.ceil(math.pow((level - 1) * math.pow(30, 0.65), (1 / 0.65)))


def needed_pixels(level: int) -> int:
    """Return the number of pixels a user needs to place to reach the next level
    from their current `level`.
    """
    return total_needed_pixels(level + 1) - total_needed_pixels(level)


def decode_color_bitmap(bitmap: int) -> tuple[Color, ...]:
    """Extract list of unlocked premium colors from `extraColorsBitmap` within
    https://backend.wplace.live/me.
    """
    colors = []
    for color in Color:
        if not color.premium:
            continue
        if (bitmap >> (color.id - 32)) & 0b1:
            colors.append(color)
    return tuple(colors)


def decode_country_bitmap(bitmap: str) -> tuple[Country, ...]:
    """Extract list of unlocked country flags from `flagsBitmap` within
    https://backend.wplace.live/me.
    """
    bitmap = int.from_bytes(base64.b64decode(bitmap), byteorder="big")
    countries = []
    for country in Country:
        if (bitmap >> country.id) & 0b1:
            countries.append(country)
    return tuple(countries)
