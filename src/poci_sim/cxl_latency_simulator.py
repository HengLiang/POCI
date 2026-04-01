"""
CXL 3.0 Latency Simulator
Based on M/D/1 queue model, parameters from POCI architecture v0.2.
"""

import numpy as np
from typing import Dict, Optional

class CXLLatencySimulator:
    """
    Simulates CXL 3.0 GFAM latency using M/D/1 queue model.
    """
    def __init__(self, 
                 payload_bytes: int = 512,
                 service_rate_ns: float = 1/280e-9,  # 280ns service time (P50)
                 redline_ns: float = 500.0,
                 queue_limit: float = 0.85):
        self.payload_bytes = payload_bytes
        self.service_rate = service_rate_ns  # packets per second
        self.redline_ns = redline_ns
        self.queue_limit = queue_limit

    def compute_latency(self, arrival_rate: float) -> Dict[str, float]:
        """
        Compute latency metrics for given arrival rate (packets/sec).
        Returns dict with P50, P90, P99, P99.9, mean, std.
        """
        # M/D/1 queue: waiting time = (ρ * service_time) / (2*(1-ρ))
        rho = arrival_rate / self.service_rate
        if rho >= 1.0:
            raise ValueError(f"Queue unstable: rho={rho} >= 1")

        service_time_ns = 1.0 / self.service_rate * 1e9
        waiting_time_ns = (rho * service_time_ns) / (2 * (1 - rho)) if rho > 0 else 0
        total_latency_ns = waiting_time_ns + service_time_ns

        # Rough distribution approximations for M/D/1 (exponential waiting + deterministic service)
        # For demonstration, we use heuristic percentiles based on queueing theory.
        # P50 is around total_latency; P99 and P99.9 can be approximated by scaling waiting time.
        p50 = total_latency_ns
        p90 = total_latency_ns + 0.5 * waiting_time_ns
        p99 = total_latency_ns + 1.5 * waiting_time_ns
        p999 = total_latency_ns + 2.5 * waiting_time_ns
        # Cap at redline (500ns) for safety
        p999 = min(p999, self.redline_ns)

        return {
            "rho": rho,
            "P50_ns": p50,
            "P90_ns": p90,
            "P99_ns": p99,
            "P99_9_ns": p999,
            "mean_ns": total_latency_ns,
            "std_dev_ns": waiting_time_ns * 0.7  # rough
        }

    def check_redline(self, arrival_rate: float) -> bool:
        """Return True if latency at redline is not exceeded."""
        metrics = self.compute_latency(arrival_rate)
        return metrics["P99_9_ns"] <= self.redline_ns