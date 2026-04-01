"""
Dynamic Asymmetric Sharding Strategy (DASS) Scheduler
"""

import numpy as np
from typing import Dict, List, Tuple

class DASSScheduler:
    def __init__(self, 
                 throughput_A: float = 1e12,   # effective ops/s for GPU
                 throughput_B: float = 5e11,   # effective ops/s for NPU
                 thermal_inertia_tau: float = 3.6,   # seconds
                 throttle_threshold_temp: float = 85.0):
        self.throughput_A = throughput_A
        self.throughput_B = throughput_B
        self.thermal_inertia_tau = thermal_inertia_tau
        self.throttle_threshold = throttle_threshold_temp
        self.weights = {"A": 0.5, "B": 0.5}  # initial S_A, S_B

    def compute_optimal_weights(self, 
                                total_work: float, 
                                current_temp_A: float,
                                current_temp_B: float) -> Tuple[float, float]:
        """
        Compute optimal sharding weights S_A and S_B to minimize total latency.
        Includes thermal throttling: if temperature exceeds threshold, reduce weight.
        """
        # Thermal penalty: if temp > threshold, reduce effective throughput
        eff_A = self.throughput_A * (1 - max(0, current_temp_A - self.throttle_threshold) / 20.0)
        eff_B = self.throughput_B * (1 - max(0, current_temp_B - self.throttle_threshold) / 20.0)

        # Solve for weights minimizing max(work*S_A/eff_A, work*S_B/eff_B)
        # The optimal balance is proportional to throughput.
        total_eff = eff_A + eff_B
        S_A = eff_A / total_eff if total_eff > 0 else 0.5
        S_B = 1 - S_A

        self.weights = {"A": S_A, "B": S_B}
        return S_A, S_B

    def update_temperature(self, 
                           power_A: float, 
                           power_B: float,
                           ambient_temp: float = 65.0,
                           cooling_rate: float = 0.2) -> Tuple[float, float]:
        """
        Simple thermal model with first-order RC dynamics.
        Returns new temperatures for nodes A and B.
        """
        # Temperature change based on power and cooling
        dT_A = (power_A - cooling_rate * (self.weights["A"] - 0.5)) / self.thermal_inertia_tau
        dT_B = (power_B - cooling_rate * (self.weights["B"] - 0.5)) / self.thermal_inertia_tau
        new_temp_A = ambient_temp + dT_A
        new_temp_B = ambient_temp + dT_B
        return new_temp_A, new_temp_B

    def schedule_step(self, 
                      total_work: float,
                      current_temp_A: float,
                      current_temp_B: float) -> Dict:
        """
        Perform one scheduling step: compute weights, simulate latency.
        Returns metrics dict.
        """
        S_A, S_B = self.compute_optimal_weights(total_work, current_temp_A, current_temp_B)
        latency_A = total_work * S_A / self.throughput_A if S_A > 0 else 0
        latency_B = total_work * S_B / self.throughput_B if S_B > 0 else 0
        total_latency = max(latency_A, latency_B)

        return {
            "S_A": S_A,
            "S_B": S_B,
            "latency_A": latency_A,
            "latency_B": latency_B,
            "total_latency": total_latency,
            "temp_A": current_temp_A,
            "temp_B": current_temp_B
        }