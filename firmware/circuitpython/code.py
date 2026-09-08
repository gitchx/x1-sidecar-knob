# SPDX-License-Identifier: GPL-3.0-only
"""X1 Sidecar Knob: ADC potentiometers to USB MIDI Control Change."""

import analogio
import time
import usb_midi

from config import (
    ADC_CHANGE_THRESHOLD,
    CONTROL_CONFIGS,
    DEBUG,
    MIDI_CHANNEL,
    POLL_INTERVAL_SECONDS,
    SMOOTHING_ALPHA,
)
from x1_sidecar import KnobState, control_change_message


class AnalogKnob:
    """One direct ADC input and its MIDI CC assignment."""

    def __init__(self, control_config):
        self.name = control_config["name"]
        self.cc_number = control_config["cc"]
        self.input = analogio.AnalogIn(control_config["pin"])
        self.state = KnobState(
            adc_min=control_config["adc_min"],
            adc_max=control_config["adc_max"],
            change_threshold=ADC_CHANGE_THRESHOLD,
            smoothing_alpha=SMOOTHING_ALPHA,
        )

    def poll(self):
        """Read this knob and return a MIDI value only when it changed."""
        return self.state.update(self.input.value)


if not 1 <= MIDI_CHANNEL <= 16:
    raise ValueError("MIDI_CHANNEL must be in 1..16")

midi_out = None
for port in usb_midi.ports:
    if isinstance(port, usb_midi.PortOut):
        midi_out = port
        break
if midi_out is None:
    raise RuntimeError("USB MIDI output port is unavailable; check boot.py")

knobs = tuple(AnalogKnob(control) for control in CONTROL_CONFIGS)

print(
    "X1 Sidecar Knob ready: channel {}, {} control(s)".format(
        MIDI_CHANNEL, len(knobs)
    )
)

while True:
    for knob in knobs:
        midi_value = knob.poll()
        if midi_value is None:
            continue

        message = control_change_message(
            MIDI_CHANNEL, knob.cc_number, midi_value
        )
        midi_out.write(message)
        if DEBUG:
            print("{}: CC{} = {}".format(knob.name, knob.cc_number, midi_value))

    time.sleep(POLL_INTERVAL_SECONDS)
