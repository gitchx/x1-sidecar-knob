# SPDX-License-Identifier: GPL-3.0-only
"""Configure the USB MIDI interface before CircuitPython starts code.py."""

import usb_midi


# USB MIDI is normally enabled by default. Keeping this explicit makes the
# firmware intention clear if CircuitPython's default USB configuration changes.
usb_midi.enable()
usb_midi.set_names(
    streaming_interface_name="X1 Sidecar Knob MIDI",
    audio_control_interface_name="X1 Sidecar Knob",
    in_jack_name="X1 Sidecar Knob In",
    out_jack_name="X1 Sidecar Knob Out",
)
