# the type: ignore comments are to tell my type chcker to stfu
# It's because i'm writing the code on a mac, but the library can only be installed on my Pi so the types won't work

from threading import Thread, Event

from rpi_ws281x import PixelStrip  # type: ignore

from core.server import webapp
from core.lib import clear_all_leds
from core.midi import midi_handler_loop
from core.models import MidiContextManager
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

    shutdown_event = Event()

    def midi_loop():
        while not shutdown_event.is_set():
            with MidiContextManager(strip) as midi_input:
                midi_handler_loop(strip, midi_input, shutdown_event)

    midi_thread = Thread(target=midi_loop)
    web_app_thread = Thread(
        target=lambda: webapp.run(
            host=HOST,
            port=PORT,
        ),
        daemon=True,
    )

    midi_thread.start()
    web_app_thread.start()

    try:
        Event().wait()
    except KeyboardInterrupt:
        shutdown_event.set()
        midi_thread.join(timeout=2)


if __name__ == "__main__":
    main()
