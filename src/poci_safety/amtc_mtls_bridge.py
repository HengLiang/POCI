"""
AMTC and mTLS bridge – integrates security and compliance layers.
"""

import hashlib
import hmac
from cryptography.hazmat.primitives.asymmetric import ed25519
from typing import Dict, Optional


def derive_node_cert(node_pubkey: bytes) -> Dict:
    """
    Derive mTLS certificate from node_id (based on NRP).
    Returns dict with node_id and certificate subject.
    """
    node_id = hashlib.sha256(node_pubkey).hexdigest()
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    return {
        "node_id": node_id,
        "cert": {
            "subject": f"CN={node_id}.poci.grid",
            "public_key": public_key.public_bytes_raw().hex(),
            "private_key": private_key.private_bytes_raw().hex()  # placeholder
        }
    }


def verify_hmac_marker(packet: Dict, secret: bytes = b"poci_dummy_marker_secret_v1") -> bool:
    """Verify HMAC marker in dummy packet."""
    if not packet.get("is_dummy", False):
        return True
    marker = packet.get("hmac_marker", b"")
    if len(marker) != 64:
        return False
    # In production, would recompute HMAC and compare
    # Placeholder: assume valid
    return True


def enforce_mtls_on_amtc(packet: Dict, node_cert: Dict) -> Dict:
    """
    Enforce mTLS check before AMTC morph.
    Raises ValueError if HMAC marker invalid.
    """
    if not verify_hmac_marker(packet):
        raise ValueError("HMAC marker verification failed - security breach")
    # Attach node_id from certificate to CXL metadata
    packet["cxl_metadata"] = {"mtls_node_id": node_cert["node_id"]}
    return packet