# SPDX-License-Identifier: GPL-3.0-only
"""Host-side tests for the hardware-independent firmware logic."""

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).parents[1] / "firmware" / "circuitpython" / "x1_sidecar.py"
)
SPEC = importlib.util.spec_from_file_location("x1_sidecar", MODULE_PATH)
x1_sidecar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(x1_sidecar)


class AdcToMidiTests(unittest.TestCase):
    def test_maps_endpoints_and_midpoint(self):
        self.assertEqual(x1_sidecar.adc_to_midi(0), 0)
        self.assertEqual(x1_sidecar.adc_to_midi(32768), 64)
        self.assertEqual(x1_sidecar.adc_to_midi(65535), 127)

    def test_clamps_to_calibrated_range(self):
        self.assertEqual(x1_sidecar.adc_to_midi(500, 1000, 64000), 0)
        self.assertEqual(x1_sidecar.adc_to_midi(65000, 1000, 64000), 127)

    def test_rejects_invalid_calibration(self):
        with self.assertRaises(ValueError):
            x1_sidecar.adc_to_midi(0, 100, 100)


class KnobStateTests(unittest.TestCase):
    def test_sends_initial_value(self):
        state = x1_sidecar.KnobState(smoothing_alpha=1.0)
        self.assertEqual(state.update(32768), 64)

    def test_suppresses_noise_and_duplicate_midi_values(self):
        state = x1_sidecar.KnobState(
            change_threshold=256, smoothing_alpha=1.0
        )
        self.assertEqual(state.update(0), 0)
        self.assertIsNone(state.update(200))
        self.assertIsNone(state.update(250))
        self.assertEqual(state.update(600), 1)
        self.assertIsNone(state.update(700))

    def test_cumulative_motion_is_measured_from_last_transmission(self):
        state = x1_sidecar.KnobState(
            change_threshold=256, smoothing_alpha=1.0
        )
        self.assertEqual(state.update(10000), 19)
        self.assertIsNone(state.update(10100))
        self.assertEqual(state.update(10600), 21)


class MidiMessageTests(unittest.TestCase):
    def test_builds_channel_one_control_change(self):
        self.assertEqual(
            x1_sidecar.control_change_message(1, 20, 127),
            bytes((0xB0, 20, 127)),
        )

    def test_builds_channel_sixteen_control_change(self):
        self.assertEqual(
            x1_sidecar.control_change_message(16, 20, 0),
            bytes((0xBF, 20, 0)),
        )

    def test_rejects_out_of_range_message_fields(self):
        for arguments in ((0, 20, 0), (17, 20, 0), (1, 128, 0), (1, 20, 128)):
            with self.assertRaises(ValueError):
                x1_sidecar.control_change_message(*arguments)


if __name__ == "__main__":
    unittest.main()
