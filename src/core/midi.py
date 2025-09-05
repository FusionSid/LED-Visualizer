import time
import mido

from core.config import (
    shared_config,
    FADE_DURATION,
    UPDATE_INTERVAL,
    MIN_MIDI_DEVICES,
    CHECK_CONNECTED_INTERVAL,
)
from core.models import NoteState
from core.lib import color_to_tuple, note_to_led_range, velocity_color


def midi_handler_loop(strip, midi_input, shutdown_event):
    """
    Main midi handling loops
    Constantly runs to update leds and ensure midi connection
    """

    active_notes: dict[int, NoteState] = {}

    while not shutdown_event.is_set():
        ignore_events = shared_config["hue"] == 1

        msgs = midi_input.iter_pending() if not ignore_events else iter(())

        for msg in msgs:
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
                        note, (0, 0, 0), target_color, FADE_DURATION
                    )
                else:
                    current_color = color_to_tuple(strip.getPixelColor(leds[0]))

                    active_notes[note] = NoteState(
                        note, current_color, (0, 0, 0), FADE_DURATION
                    )

        notes_to_remove: set[int] = set()
        for note, state in active_notes.items():
            for led in note_to_led_range(note):
                strip.setPixelColor(led, state.color)

            if state.is_done:
                notes_to_remove.add(note)

        strip.show()

        # im running this after updating leds opposed to in that loop as it introduces delay
        for note in notes_to_remove:
            active_notes.pop(note, None)

        # every 5 seconds checks that midi device is still connected
        curr_time = int(time.time())
        if curr_time % CHECK_CONNECTED_INTERVAL == 0 and len(mido.get_input_names()) < MIN_MIDI_DEVICES:  # type: ignore
            break

        time.sleep(UPDATE_INTERVAL)
