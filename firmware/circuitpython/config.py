# SPDX-License-Identifier: GPL-3.0-only
"""User-editable settings for the X1 Sidecar Knob prototype."""

import board


# User-facing MIDI channels are numbered 1 through 16.
MIDI_CHANNEL = 1

# Add another dictionary here when direct ADC inputs are added. The runtime
# creates one AnalogKnob for each entry, so the processing logic is not copied.
CONTROL_CONFIGS = (
    {
        "name": "knob_1",
        "pin": board.GP26,
        "cc": 20,
        "adc_min": 0,
        "adc_max": 65535,
    },
)

# Poll every 5 ms (200 Hz). MIDI is sent only after the checks below pass.
POLL_INTERVAL_SECONDS = 0.005

# Ignore changes smaller than this many filtered 16-bit ADC counts relative to
# the last transmitted value. 256 is about 0.4% of the ADC range.
ADC_CHANGE_THRESHOLD = 256

# Exponential smoothing: 1.0 disables smoothing; smaller values are smoother
# but add more response lag. 0.25 is intentionally modest for the prototype.
SMOOTHING_ALPHA = 0.25

# Print transmitted values to the CircuitPython serial console when True.
DEBUG = False
