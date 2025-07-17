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
)


def clear_all_leds(strip) -> None:
    for led in range(strip.numPixels()):
        strip.setPixelColor(led, LED_OFF)

    strip.show()


def handle_midi(strip, midi_input, shutdown_event):
    active_notes = {}

    while not shutdown_event.is_set():
        for msg in midi_input.iter_pending():
            if msg.type in ("note_on", "note_off"):
                note = msg.note
                leds = note_to_led_range(note)
                if not leds:
                    continue

                first_led = leds[0]
                current_color = color_to_tuple(strip.getPixelColor(first_led))

                if msg.type == "note_on" and msg.velocity > 0:
                    target_color = color_to_tuple(
                        velocity_color(msg.velocity, shared_config["hue"])
                    )
                    active_notes[note] = NoteState(
                        note, (0, 0, 0), target_color, duration=0.07
                    )
                else:
                    active_notes[note] = NoteState(
                        note, current_color, (0, 0, 0), duration=0.07
                    )

        notes_to_remove = []
        for note, fade in active_notes.items():
            color = fade.get_current_color()
            for i in note_to_led_range(note):
                strip.setPixelColor(i, color)
            if fade.is_done():
                notes_to_remove.append(note)

        strip.show()

        for note in notes_to_remove:
            del active_notes[note]

        if int(time.time()) % 5 == 0 and len(mido.get_input_names()) < 2:  # type: ignore
            break

        time.sleep(1 / 60)


def note_to_led_range(note):
    idx = note - 21  # MIDI note 21 is A0
    if 0 <= idx < KEY_COUNT:
        led_start = LED_STRIP_LENGTH - (idx + 1) * LEDS_PER_KEY
        return range(led_start, led_start + LEDS_PER_KEY)
    return []


def color_to_tuple(color):
    return ((color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF)


def tuple_to_color(rgb):
    r, g, b = rgb
    return Color(r, g, b)


def random_vibrant_color():
    r, g, b = colorsys.hsv_to_rgb(random.random(), 1, 1)
    return Color(int(r * 255), int(g * 255), int(b * 255))


class NoteState:
    def __init__(self, note, start_color, end_color, duration=0.1):
        self.note = note
        self.start_color = start_color
        self.end_color = end_color
        self.start_time = time.time()
        self.duration = duration

    def is_done(self):
        return time.time() - self.start_time >= self.duration

    def get_current_color(self):
        t = (time.time() - self.start_time) / self.duration
        t = min(max(t, 0), 1)
        sr, sg, sb = self.start_color
        er, eg, eb = self.end_color
        r = int(sr + (er - sr) * t)
        g = int(sg + (eg - sg) * t)
        b = int(sb + (eb - sb) * t)
        return Color(r, g, b)


def wait_for_midi_device():
    print("Waiting for MIDI input device...")
    while True:
        inputs = mido.get_input_names()  # type: ignore
        if len(inputs) > 1:
            return inputs[1]
        time.sleep(1)


def velocity_color(velocity, hue: float):
    brightness = max(0.2, min(1.0, velocity / 127))

    if hue == 0:
        hue = random.random()

    r, g, b = colorsys.hsv_to_rgb(hue, 1, brightness)
    return Color(int(r * 255), int(g * 255), int(b * 255))
