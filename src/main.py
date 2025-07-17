# the type: ignore comments are to tell my type chcker to stfu
# It's because i'm writing the code on a mac, but the library can only be installed on my Pi so the types won't work

import threading

from rpi_ws281x import PixelStrip  # type: ignore

from core.server import webapp
from core.models import MidiContextManager
from core.lib import clear_all_leds, handle_midi
from core.config import (
    LED_BRIGHTNESS,
    LED_CHANNEL,
    LED_DMA,
    LED_FREQ_HZ,
    LED_INVERT,
    LED_PIN,
    LED_STRIP_LENGTH,
    HOST,
    PORT,
    config_lock,
    shared_config,
)


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

    threading.Thread(
        target=lambda: webapp.run(host=HOST, port=PORT), daemon=True
    ).start()

    try:
        while True:
            with MidiContextManager(strip) as midi_input, config_lock:
                handle_midi(strip, midi_input, shared_config)
    except KeyboardInterrupt:
        clear_all_leds(strip)
        print("Exiting. Turning off LEDs...")


if __name__ == "__main__":
    main()
