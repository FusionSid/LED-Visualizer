import time

import mido

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
