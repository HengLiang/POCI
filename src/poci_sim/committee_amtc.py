"""
Adaptive Morphing Traffic Camouflage (AMTC) for committee communication.
Based on AMTC v0.4.1 specification.
"""

import numpy as np
import hmac
import hashlib
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

MAX_DUMMY_RATE_PER_SEC = 50

class CommitteeAMTC:
    def __init__(self,
                 target_ratio: float = 2.05,
                 max_overhead: float = 1.2,
                 dummy_entropy_target: float = 7.95):
        self.target_ratio = target_ratio
        self.max_overhead = max_overhead
        self.dummy_entropy_target = dummy_entropy_target

        # Mixed dummy size sampler (40% small, 40% medium, 20% large)
        self.dummy_size_samplers = [
            lambda: int(np.random.uniform(100, 250)),                         # 40%
            lambda: int(np.clip(np.random.lognormal(6.5, 0.6), 600, 1200)),  # 40%
            lambda: int(np.random.uniform(1200, 1400))                        # 20%
        ]
        self.sampler_weights = [0.4, 0.4, 0.2]
        self.dummy_iat_sampler = lambda: np.random.exponential(15)  # ms

    def sample_dummy_size(self) -> int:
        idx = np.random.choice([0, 1, 2], p=self.sampler_weights)
        return self.dummy_size_samplers[idx]()

    def _generate_hmac_marker(self,
                              leaf_id: str = "",
                              epoch: int = 0,
                              seq_id: int = 0,
                              node_private_key: Optional[bytes] = None) -> bytes:
        message = f"DUMMY_MARKER_v1|{leaf_id}|{epoch}|{seq_id}".encode()
        h = hmac.new(b"poci_dummy_marker_secret_v1", message, hashlib.sha256).digest()

        if node_private_key is not None:
            # In production, use real Ed25519 signature (placeholder)
            sig = b'\x00' * 32  # would be real signature in production
        else:
            # Simulation: derive pseudo-random signature
            sig = hmac.new(b"poci_dummy_marker_secret_v1", h + b"SIG_STUB", hashlib.sha256).digest()
        return h + sig  # 64B total

    def morph_committee_flow(self,
                             real_packets: List[Dict],
                             leaf_id: str = "",
                             epoch: int = 0,
                             node_private_key: Optional[bytes] = None) -> Tuple[List[Dict], Dict]:
        """
        Apply AMTC to committee traffic.
        Returns (morphed_packets, metrics)
        """
        if not real_packets:
            return [], {}

        up_bytes = sum(p['size'] for p in real_packets if p['direction'] == 'up')
        down_bytes = sum(p['size'] for p in real_packets if p['direction'] == 'down')
        current_ratio = down_bytes / up_bytes if up_bytes > 0 else 0.0

        needed_down = up_bytes * self.target_ratio
        extra_needed = max(0, needed_down - down_bytes)
        max_extra = (down_bytes + up_bytes) * self.max_overhead
        extra_needed = min(extra_needed, max_extra)

        dummy_packets = []
        remaining = extra_needed
        last_ts = max(p['iat'] for p in real_packets) if real_packets else 0
        seq_id = 0
        while remaining > 100:
            sz = self.sample_dummy_size()
            sz = min(sz, remaining)
            iat_delta = self.dummy_iat_sampler()
            last_ts += iat_delta

            marker = self._generate_hmac_marker(leaf_id, epoch, seq_id, node_private_key)
            payload = marker + np.random.bytes(sz - len(marker))

            dummy_packets.append({
                "id": f"dummy_{seq_id}",
                "phase": "dummy_down",
                "size": len(payload),
                "iat": last_ts,
                "direction": "down",
                "is_dummy": True,
                "entropy": self.dummy_entropy_target
            })
            remaining -= sz
            seq_id += 1

        # Aggregate packet padding (unidirectional)
        aggregate_sizes = set()
        for p in real_packets:
            if p['phase'] == 'aggregate':
                pad_len = np.random.randint(0, 121)   # 0–120B
                p['size'] = 936 + pad_len
                p['pad_len'] = pad_len
                aggregate_sizes.add(p['size'])

        all_packets = real_packets + dummy_packets
        all_packets.sort(key=lambda p: p['iat'])

        # Padding to MTU and entropy setting
        for p in all_packets:
            orig_size = p['size']
            if orig_size < 1400:
                pad_len = np.random.randint(900, 1401) - orig_size
                pad_len = max(0, pad_len)
                pad = np.random.bytes(pad_len)
                p['padded_size'] = orig_size + pad_len
                p['entropy'] = self.dummy_entropy_target if p.get('is_dummy', False) else 7.9
            else:
                p['padded_size'] = orig_size
                p['entropy'] = 7.9

        # Rate limiting
        duration_sec = last_ts / 1000.0 if last_ts > 0 else 1.0
        current_rate = len(dummy_packets) / duration_sec
        if current_rate > MAX_DUMMY_RATE_PER_SEC:
            max_allowed = int(MAX_DUMMY_RATE_PER_SEC * duration_sec)
            dummy_packets = dummy_packets[:max_allowed]
            logger.warning(f"Dummy rate limited: {current_rate:.2f}/s -> {MAX_DUMMY_RATE_PER_SEC}/s")

        metrics = {
            "aggregate_identifiable": len(aggregate_sizes) > 0,
            "dummy_packet_count": len(dummy_packets),
            "dummy_to_real_byte_ratio": sum(p['padded_size'] for p in dummy_packets) / sum(p['padded_size'] for p in real_packets) if real_packets else 0,
            "bandwidth_overhead": (sum(p['padded_size'] for p in all_packets) - sum(p['padded_size'] for p in real_packets)) / sum(p['padded_size'] for p in real_packets) if real_packets else 0
        }
        return all_packets, metrics