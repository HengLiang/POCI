"""
Merkle Tree Simulator for data provenance and batch validation.
Based on POCI Merkle specification v0.3.
"""

import hashlib
from typing import List, Dict, Optional, Tuple

class MerkleSimulator:
    def __init__(self, batch_threshold: float = 0.4):
        """
        batch_threshold: AI_ASSISTED proportion that triggers alert (>40%)
        """
        self.batch_threshold = batch_threshold
        self.leaf_db = {}  # placeholder for leaf storage

    @staticmethod
    def compute_leaf_id(node_id: str, epoch: int, counter: int, content_hash: str) -> str:
        """leaf_id = sha256(node_id || epoch || local_counter || content_hash)"""
        data = f"{node_id}{epoch}{counter}{content_hash}".encode()
        return hashlib.sha256(data).hexdigest()

    def validate_leaf(self, leaf: Dict) -> Tuple[bool, str]:
        """
        Validate a single leaf according to provenance rules.
        Returns (accept, reason)
        """
        origin = leaf.get("origin_type")
        if origin == "AI_GENERATED":
            return False, "direct_ai_generation"
        # Check ancestors (simplified: we assume parent list contains hashes)
        ancestors = leaf.get("parent_leaf_ids", [])
        for pid in ancestors:
            parent = self.leaf_db.get(pid)
            if parent and parent.get("origin_type") == "AI_GENERATED":
                return False, f"ai_ancestor_detected: {pid}"
        # ZK proof placeholder (would be real verification in production)
        if not leaf.get("zk_proof_valid", True):
            return False, "invalid_zk_proof"
        return True, "ACCEPT"

    def batch_validate(self, leaves: List[Dict]) -> Dict:
        """
        Batch validate leaves, compute aggregate metrics.
        Returns dict with pass_rate, alerts, etc.
        """
        results = []
        ai_assisted_count = 0
        total = len(leaves)

        for leaf in leaves:
            accept, reason = self.validate_leaf(leaf)
            results.append((accept, reason))
            if leaf.get("origin_type") == "AI_ASSISTED":
                ai_assisted_count += 1

        pass_rate = sum(1 for acc, _ in results if acc) / total if total else 1.0
        ai_ratio = ai_assisted_count / total if total else 0.0
        alert_triggered = ai_ratio > self.batch_threshold

        return {
            "pass_rate": pass_rate,
            "ai_assisted_ratio": ai_ratio,
            "batch_alert_triggered": alert_triggered,
            "alert_type": "BATCH_RATIO_EXCEEDED" if alert_triggered else None,
            "results": results
        }

    def estimate_storage(self, leaf_count: int) -> Dict:
        """Estimate storage per leaf and total size."""
        per_leaf_bytes = 1850  # ~1.85KB from Phase 2
        total_bytes = leaf_count * per_leaf_bytes
        return {
            "per_leaf_kb": per_leaf_bytes / 1024,
            "total_kb": total_bytes / 1024,
            "total_mb": total_bytes / (1024*1024)
        }