# SPDX-License-Identifier: GPL-3.0-only
"""Hardware-independent ADC filtering and MIDI helpers.

This module deliberately uses only Python/CircuitPython built-ins. It can be
unit-tested on a development computer without a connected Pico 2.
"""


MIDI_MIN = 0
MIDI_MAX = 127
ADC_ABSOLUTE_MIN = 0
ADC_ABSOLUTE_MAX = 65535


def clamp(value, minimum, maximum):
    """Return value constrained to the inclusive minimum/maximum range."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def adc_to_midi(adc_value, adc_min=ADC_ABSOLUTE_MIN, adc_max=ADC_ABSOLUTE_MAX):
    """Map a calibrated 16-bit ADC reading to a rounded MIDI value (0-127)."""
    if adc_min < ADC_ABSOLUTE_MIN or adc_max > ADC_ABSOLUTE_MAX:
        raise ValueError("ADC calibration must stay within 0..65535")
    if adc_min >= adc_max:
        raise ValueError("adc_min must be smaller than adc_max")

    clamped = clamp(int(adc_value), adc_min, adc_max)
    offset = clamped - adc_min
    span = adc_max - adc_min
    return (offset * MIDI_MAX + span // 2) // span


class KnobState:
    """Track one knob's smoothing and last transmitted values."""

    def __init__(
        self,
        adc_min=ADC_ABSOLUTE_MIN,
        adc_max=ADC_ABSOLUTE_MAX,
        change_threshold=256,
        smoothing_alpha=0.25,
    ):
        if change_threshold < 0:
            raise ValueError("change_threshold must be zero or greater")
        if smoothing_alpha <= 0.0 or smoothing_alpha > 1.0:
            raise ValueError("smoothing_alpha must be greater than 0 and at most 1")

        # Validate calibration immediately instead of failing inside the loop.
        adc_to_midi(adc_min, adc_min, adc_max)
        self.adc_min = adc_min
        self.adc_max = adc_max
        self.change_threshold = change_threshold
        self.smoothing_alpha = smoothing_alpha
        self.filtered_adc = None
        self.last_sent_adc = None
        self.last_sent_midi = None

    def update(self, raw_adc):
        """Return a new MIDI value when it should be sent, otherwise None."""
        raw_adc = clamp(int(raw_adc), ADC_ABSOLUTE_MIN, ADC_ABSOLUTE_MAX)

        if self.filtered_adc is None:
            self.filtered_adc = float(raw_adc)
        else:
            self.filtered_adc += self.smoothing_alpha * (
                raw_adc - self.filtered_adc
            )

        filtered_adc = int(self.filtered_adc + 0.5)
        midi_value = adc_to_midi(filtered_adc, self.adc_min, self.adc_max)

        if self.last_sent_midi is not None:
            adc_delta = abs(filtered_adc - self.last_sent_adc)
            if adc_delta < self.change_threshold:
                return None
            if midi_value == self.last_sent_midi:
                return None

        self.last_sent_adc = filtered_adc
        self.last_sent_midi = midi_value
        return midi_value


def control_change_message(channel, cc_number, value):
    """Build a standard three-byte MIDI Control Change message."""
    if channel < 1 or channel > 16:
        raise ValueError("MIDI channel must be in 1..16")
    if cc_number < MIDI_MIN or cc_number > MIDI_MAX:
        raise ValueError("CC number must be in 0..127")
    if value < MIDI_MIN or value > MIDI_MAX:
        raise ValueError("CC value must be in 0..127")

    status = 0xB0 | (channel - 1)
    return bytes((status, cc_number, value))
