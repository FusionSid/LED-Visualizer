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

HOST: Final = "0.0.0.0"
PORT: Final = 5000


class SharedConfig(TypedDict):
    hue: float


shared_config: SharedConfig = {"hue": 0}
config_lock = Lock()
