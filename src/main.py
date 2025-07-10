import time
import random
import colorsys

# (I'm unable to install the rpi libraries on the machine where im coding so I gotta just ignore the type errors)
from rpi_ws281x import PixelStrip, Color  # type: ignore
import mido  # type: ignore

from consts import (
    KEY_COUNT,
    LED_BRIGHTNESS,
    LED_CHANNEL,
    LED_DMA,
    LED_FREQ_HZ,
    LED_INVERT,
    LED_PIN,
    LED_STRIP_LENGTH,
    LEDS_PER_KEY,
)

LED_OFF = Color(0, 0, 0)


def clear_all_leds(strip: PixelStrip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, LED_OFF)
    strip.show()


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
        inputs = mido.get_input_names()
        if len(inputs) > 1:
            return inputs[1]
        time.sleep(1)


def velocity_color(velocity, hue=None):
    brightness = max(0.2, min(1.0, velocity / 127))

    if hue is None:
        hue = random.random()
    r, g, b = colorsys.hsv_to_rgb(hue, 1, brightness)
    return Color(int(r * 255), int(g * 255), int(b * 255))


def handle_midi(strip, midi_input, randc=True):
    active_notes = {}
    fixed_hue = random.random()
    while True:
        for msg in midi_input.iter_pending():
            if msg.type in ("note_on", "note_off"):
                note = msg.note
                leds = note_to_led_range(note)
                if not leds:
                    continue

                first_led = leds[0]
                current_color = color_to_tuple(strip.getPixelColor(first_led))

                if msg.type == "note_on" and msg.velocity > 0:
                    hue = None if randc else fixed_hue

                    target_color = color_to_tuple(velocity_color(msg.velocity, hue))
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

        if int(time.time()) % 5 == 0 and len(mido.get_input_names()) < 2:
            break

        time.sleep(1 / 60)


def main() -> None:
    strip = PixelStrip(
        LED_STRIP_LENGTH,
        LED_PIN,
        LED_FREQ_HZ,
        LED_DMA,
        LED_INVERT,
        LED_BRIGHTNESS,
        LED_CHANNEL,
    )

    strip.begin()
    clear_all_leds(strip)
    randc = True
    try:
        while True:
            device_name = wait_for_midi_device()
            with mido.open_input(device_name) as midi_input:
                print(f"Connected to MIDI device: {device_name}")
                print(randc)
                handle_midi(strip, midi_input, randc)
                print("exited")
                randc ^= True
    except KeyboardInterrupt:
        clear_all_leds(strip)
        print("Exiting. Turning off LEDs...")


if __name__ == "__main__":
    main()
