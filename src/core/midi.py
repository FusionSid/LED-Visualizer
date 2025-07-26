import time
import mido

from core.config import (
    shared_config,
    UPDATE_INTERVAL,
)
from core.models import NoteState
from core.lib import color_to_tuple, note_to_led_range, velocity_color


def midi_handler_loop(strip, midi_input, shutdown_event):
    active_notes: dict[int, NoteState] = {}

    while not shutdown_event.is_set():
        for msg in midi_input.iter_pending():
            if msg.type in ("note_on", "note_off"):
                note = msg.note
                leds = note_to_led_range(note)

                if not leds:
                    continue

                if msg.type == "note_on" and msg.velocity > 0:
                    target_color = color_to_tuple(
                        velocity_color(msg.velocity, shared_config["hue"])
                    )
                    active_notes[note] = NoteState(
                        note, (0, 0, 0), target_color, duration=0.07
                    )
                else:
                    current_color = color_to_tuple(strip.getPixelColor(leds[0]))

                    active_notes[note] = NoteState(
                        note, current_color, (0, 0, 0), duration=0.07
                    )

        notes_to_remove: set[int] = set()
        for note, state in active_notes.items():
            for led in note_to_led_range(note):
                strip.setPixelColor(led, state.color)

            if state.is_done:
                notes_to_remove.add(note)

        strip.show()

        for note in notes_to_remove:
            del active_notes[note]

        # every 5 seconds check that midi device is still connected
        if int(time.time()) % 5 == 0 and len(mido.get_input_names()) < 2:  # type: ignore
            break

        time.sleep(1 / UPDATE_INTERVAL)
