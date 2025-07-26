import time

import mido
from rpi_ws281x import Color  # type: ignore

from core.lib import clear_all_leds


class MidiContextManager:
    def __init__(self, strip):
        self.strip = strip
        self.midi_input = None

    def __enter__(self):
        print("Waiting for MIDI input device...")
        while True:
            inputs: list[str] = mido.get_input_names()  # type: ignore
            if len(inputs) > 1:
                break
            time.sleep(1)

        device_name = inputs[1]  # inputs[1] is my piano
        self.midi_input = mido.open_input(device_name)  # type: ignore
        print(f"Connected to MIDI device: {device_name}")

        return self.midi_input

    def __exit__(self, *_):
        print("Exiting. Turning off LEDs...")
        clear_all_leds(self.strip)
        if self.midi_input is not None:
            self.midi_input.close()


class NoteState:
    def __init__(self, note, start_color, end_color, duration=0.1):
        self.note = note
        self.start_color = start_color
        self.end_color = end_color
        self.duration = duration

        self.start_time = time.time()

    @property
    def is_done(self):
        return time.time() - self.start_time >= self.duration

    @property
    def color(self):
        t = (time.time() - self.start_time) / self.duration
        t = min(max(t, 0), 1)  # ensures it in the range 0 -> 1

        sr, sg, sb = self.start_color
        er, eg, eb = self.end_color

        r = int(sr + (er - sr) * t)
        g = int(sg + (eg - sg) * t)
        b = int(sb + (eb - sb) * t)

        return Color(r, g, b)
