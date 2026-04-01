"""
Thermal model and PCE calculator for POCI.
"""

import numpy as np
from typing import Dict, Optional

class ThermalCalculator:
    def __init__(self,
                 node_type: str = "NPU",
                 tdp_w: float = 200.0,
                 chip_area_mm2: float = 600.0,
                 thermal_resistance: float = 0.11,   # °C/W
                 coolant_temp_c: float = 65.0,
                 pump_power_w: float = 40.0,
                 microchannel_htc: float = 60000.0,
                 eta_heat: float = 0.75,
                 network_overhead_factor: float = 1.0):
        self.node_type = node_type
        self.tdp = tdp_w
        self.area_mm2 = chip_area_mm2
        self.rth = thermal_resistance
        self.coolant_temp = coolant_temp_c
        self.pump_power = pump_power_w
        self.htc = microchannel_htc
        self.eta_heat = eta_heat
        self.network_factor = network_overhead_factor

    def compute_junction_temp(self, power: Optional[float] = None) -> float:
        """Compute junction temperature based on power and cooling."""
        if power is None:
            power = self.tdp
        # Thermal resistance model: Tj = Tc + P * Rth
        Tj = self.coolant_temp + power * self.rth
        return Tj

    def compute_heat_flux(self, power: Optional[float] = None) -> float:
        """Heat flux in W/m²."""
        if power is None:
            power = self.tdp
        area_m2 = self.area_mm2 / 1e6
        return power / area_m2

    def compute_pce(self,
                    effective_ops: float,
                    total_power: float,
                    recovered_heat: float = 0.0) -> float:
        """
        PCE = effective_ops / (total_power - eta_heat * recovered_heat)
        """
        net_power = total_power - self.eta_heat * recovered_heat
        if net_power <= 0:
            return float('inf')
        return effective_ops / net_power

    def evaluate(self, dummy_packet_rate: float = 0) -> Dict[str, float]:
        """Full evaluation with network overhead."""
        # Adjust power based on dummy packet rate (simplified)
        extra_power = dummy_packet_rate * 0.5  # watts per packet per second
        total_power = self.tdp + self.pump_power + extra_power
        Tj = self.compute_junction_temp(total_power)
        heat_flux = self.compute_heat_flux(total_power)
        # Assume recovered heat is proportional to total power
        recovered = 0.95 * total_power  # 95% of power becomes heat
        pce = self.compute_pce(1e9, total_power, recovered)  # placeholder ops

        return {
            "node_type": self.node_type,
            "Tj_celsius": Tj,
            "heat_flux_kW_m2": heat_flux / 1000,
            "total_power_w": total_power,
            "pump_power_w": self.pump_power,
            "pce_placeholder": pce,
            "thermal_safety_margin": max(0, 85 - Tj)
        }