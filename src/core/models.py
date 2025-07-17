import time

import mido

from core.lib import clear_all_leds


class MidiContextManager:
    def __init__(self, strip):
        self.strip = strip

    def __enter__(self):
        print("Waiting for MIDI input device...")
        while True:
            inputs: list[str] = mido.get_input_names()  # type: ignore
            if len(inputs) > 1:
                break
            time.sleep(1)

        device_name = inputs[0]
        with mido.open_input(device_name) as midi_input:  # type: ignore
            print(f"Connected to MIDI device: {device_name}")
            return midi_input

    def __exit__(self, *_):
        print("Exiting. Turning off LEDs...")
        clear_all_leds(self.strip)
