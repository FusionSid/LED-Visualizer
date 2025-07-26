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
    for led in range(strip.numPixels()):
        strip.setPixelColor(led, LED_OFF)

    strip.show()


def note_to_led_range(note: int):
    A0 = 21
    idx = note - A0

    if 0 <= idx < KEY_COUNT:
        led_start = LED_STRIP_LENGTH - (idx + 1) * LEDS_PER_KEY
        return range(led_start, led_start + LEDS_PER_KEY)

    return []


def color_to_tuple(color: int):
    return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)


def velocity_color(velocity: int, hue: float):
    if hue == 0:
        hue = random.random()

    brightness = max(0.2, min(1.0, velocity / 127))  # puts in range 0.2 - 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 1, brightness)

    return Color(int(r * 255), int(g * 255), int(b * 255))
