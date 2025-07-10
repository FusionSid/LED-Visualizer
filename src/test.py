import time
import random
import colorsys

from rpi_ws281x import PixelStrip, Color  # type: ignore
import mido  # type: ignore

from consts import (
    LED_BRIGHTNESS,
    LED_CHANNEL,
    LED_DMA,
    LED_FREQ_HZ,
    LED_INVERT,
    LED_PIN,
    KEY_COUNT,
    LED_STRIP_LENGTH,
    LEDS_PER_KEY,
)

LED_OFF = Color(0, 0, 0)


def clear_all_leds(strip: PixelStrip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, LED_OFF)
    strip.show()


def note_to_led_range(note):
    idx = note - 21  # MIDI note 21 (A0) is index 0
    if 0 <= idx < KEY_COUNT:
        led_start = LED_STRIP_LENGTH - (idx + 1) * LEDS_PER_KEY
        return range(led_start, led_start + LEDS_PER_KEY)
    return []


def set_note_led(strip, note, color):
    for i in note_to_led_range(note):
        strip.setPixelColor(i, color)
    strip.show()


def random_vibrant_color():
    r, g, b = colorsys.hsv_to_rgb(random.random(), 1, 1)
    return Color(int(r * 255), int(g * 255), int(b * 255))


def wait_for_midi_device():
    print("Waiting for MIDI input device...")
    while True:
        inputs = mido.get_input_names()
        if len(inputs) > 1:
            return inputs[1]
        time.sleep(1)


def handle_midi_messages(strip, midi_input):
    for msg in midi_input:
        if msg.type == "note_on":
            if msg.velocity > 0:
                set_note_led(strip, msg.note, random_vibrant_color())
            else:
                set_note_led(strip, msg.note, LED_OFF)
        elif msg.type == "note_off":
            set_note_led(strip, msg.note, LED_OFF)


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

    # main program loop
    while True:
        try:
            device_name = wait_for_midi_device()
            with mido.open_input(device_name) as midi_input:
                print(f"Connected to MIDI device: {device_name}")
                handle_midi_messages(strip, midi_input)
        except KeyboardInterrupt:
            clear_all_leds(strip)
            print("Exiting. Turning off LEDs...")
            return


if __name__ == "__main__":
    main()
