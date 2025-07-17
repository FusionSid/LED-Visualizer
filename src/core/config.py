from threading import Lock
from typing import Final, TypedDict

from rpi_ws281x import Color  # type: ignore

__all__ = (
    "KEY_COUNT",
    "LEDS_PER_KEY",
    "LED_STRIP_LENGTH",
    "LED_PIN",
    "LED_FREQ_HZ",
    "LED_DMA",
    "LED_BRIGHTNESS",
    "LED_INVERT",
    "LED_CHANNEL",
    "LED_OFF",
    "config_lock",
    "shared_config",
    "SharedConfig",
)

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


class SharedConfig(TypedDict):
    hue: float


shared_config: SharedConfig = {"hue": 0}
config_lock = Lock()
