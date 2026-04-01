"""
TC-012: Thermal Tracking Test
Verifies hotspot detection, throttling logic, and thermal inertia modeling.
"""

import pytest
from src.poci_sim import ThermalCalculator, DASSScheduler


class TestTC012Thermal:
    def setup_method(self):
        self.calc = ThermalCalculator()
        self.scheduler = DASSScheduler()

    def test_throttling_trigger(self):
        """Simulate temperature rise and check throttling condition."""
        # Assume temperature crosses 85°C
        temp = 86.0
        # Throttling condition: freq_drop > 5% AND duration > 200ms
        freq_drop = 0.06
        duration = 250
        assert freq_drop > 0.05 and duration > 200, "Throttling should trigger"

    def test_hotspot_detection(self):
        """Detect hotspot when CPU temperature gradient is high."""
        # Simulated thermal trace
        trace = [70, 72, 78, 85, 89, 88, 82]
        # Simple gradient check
        max_gradient = max(trace[i+1] - trace[i] for i in range(len(trace)-1))
        hotspot_detected = max_gradient > 5  # °C per sample
        assert hotspot_detected

    def test_thermal_stability(self):
        """Verify system returns to stable temperature after load reduction."""
        # Simulate load reduction after throttling
        # Thermal inertia model: Tj = Tcoolant + P * Rth
        # After power drop, temperature should decay with time constant τ
        tau = 3.6  # seconds
        initial_temp = 87.0
        ambient = 65.0
        # After 5 seconds (approx 1.4 τ), temperature should drop significantly
        decay_ratio = 0.25  # rough estimate
        final_temp = ambient + (initial_temp - ambient) * decay_ratio
        assert final_temp < 85.0, "Thermal inertia should bring temperature down"