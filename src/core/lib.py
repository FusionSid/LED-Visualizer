import time
import random
import colorsys

import mido
from rpi_ws281x import Color  # type: ignore

from core.config import (
    shared_config,
    LED_OFF,
    KEY_COUNT,
    LED_STRIP_LENGTH,
    LEDS_PER_KEY,
    UPDATE_INTERVAL,
)
from core.models import NoteState


def handle_midi(strip, midi_input, shutdown_event):
    active_notes: dict[int, NoteState] = {}

    while not shutdown_event.is_set():
        for msg in midi_input.iter_pending():
            if msg.type in ("note_on", "note_off"):
                note = msg.note
                leds = note_to_led_range(note)

                if not leds:
                    continue

                if msg.type == "note_on" and msg.velocity > 0:
                    target_color = color_to_tuple(
                        velocity_color(msg.velocity, shared_config["hue"])
                    )
                    active_notes[note] = NoteState(
                        note, (0, 0, 0), target_color, duration=0.07
                    )
                else:
                    current_color = color_to_tuple(strip.getPixelColor(leds[0]))

                    active_notes[note] = NoteState(
                        note, current_color, (0, 0, 0), duration=0.07
                    )

        notes_to_remove: set[int] = set()
        for note, state in active_notes.items():
            for led in note_to_led_range(note):
                strip.setPixelColor(led, state.color)

            if state.is_done:
                notes_to_remove.add(note)

        strip.show()

        for note in notes_to_remove:
            del active_notes[note]

        # every 5 seconds check that midi device is still connected
        if int(time.time()) % 5 == 0 and len(mido.get_input_names()) < 2:  # type: ignore
            break

        time.sleep(1 / UPDATE_INTERVAL)


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
