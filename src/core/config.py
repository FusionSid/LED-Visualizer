from threading import Lock
from typing import Final, TypedDict

from rpi_ws281x import Color  # type: ignore

KEY_COUNT: Final = 88
LEDS_PER_KEY: Final = 2
LED_STRIP_LENGTH: Final = 288

LED_PIN: Final = 18
LED_FREQ_HZ: Final = 800000
LED_DMA: Final = 10
LED_BRIGHTNESS: Final = 65
LED_INVERT: Final = False
LED_CHANNEL: Final = 0
LED_OFF: Final = Color(0, 0, 0)

UPDATE_INTERVAL: Final = 1 / 60  # so should run about 60 times a sec
CHECK_CONNECTED_INTERVAL: Final = 5
MIN_MIDI_DEVICES: Final = 2
FADE_DURATION: Final = 0.07

HOST: Final = "0.0.0.0"
PORT: Final = 5000


class SharedConfig(TypedDict):
    hue: float


# this will be shared accross the server and midi handler thread
shared_config: SharedConfig = {"hue": 0}
config_lock = Lock()
