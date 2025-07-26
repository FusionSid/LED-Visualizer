import random
import colorsys

from rpi_ws281x import Color  # type: ignore

from core.config import (
    LED_OFF,
    KEY_COUNT,
    LED_STRIP_LENGTH,
    LEDS_PER_KEY,
)


def clear_all_leds(strip) -> None:
    """
    Turns off all leds
    """

    for led in range(strip.numPixels()):
        strip.setPixelColor(led, LED_OFF)

    strip.show()


def note_to_led_range(note: int):
    """
    Gets a range of led indices that are accoiated with a single note
    This range is typically 2 leds as I have 2 leds per note
    """

    A0 = 21
    idx = note - A0

    if 0 <= idx < KEY_COUNT:
        led_start = LED_STRIP_LENGTH - (idx + 1) * LEDS_PER_KEY
        return range(led_start, led_start + LEDS_PER_KEY)

    return []


def color_to_tuple(color: int):
    """
    Converts the 24 bit number color returned by the strips get color function to rgb
    """

    return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)


def velocity_color(velocity: int, hue: float):
    """
    Returns the rgb color given velocity and hue
    The greater the velocity (how hard i hit the note), the brighter the color
    The hue lies on a range from 0 -> 1
    If the hue is exactly equal to 0, then the color will be a random color
    """

    if hue == 0:
        hue = random.random()

    brightness = max(0.2, min(1.0, velocity / 127))  # puts in range 0.2 - 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1, brightness)

    return Color(int(r * 255), int(g * 255), int(b * 255))
