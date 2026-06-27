"""
test_tamper_detection_validation.py — Validation suite for SecureDAL tamper detection.

Covers the 9 scenarios defined in the validation plan, one test per scenario:
  1. Valid object (baseline case)
  2. Object without anchor
  3. Object content tampering
  4. Multiple tampered objects (read_all)
  5. Deleted object
  6. Anchor deletion (IPFS-level, mapping untouched)
  7. Pinned-anchor recovery (Pinata)
  8. Anchor injection attack
  9. Rollback attack

Conventions used throughout:

  - Backend: "fs" for all tests.
  - "Attacker" / unmanaged-party actions are performed via
    `tamper_op._operator` (the raw underlying OpenDAL operator that
    TamperOperator wraps). This bypasses every integrity mechanism the
    SDK provides, which is exactly what it's wanted: to simulate an external
    party tampering with the backend directly.
  - Anchor-level attacks (6, 7, 8) act directly on IPFS via
    `tamper_op._eis._client` (the raw ipfshttpclient instance).
  - The local key->CID mapping is never touched in any scenario. 
    It is considered a trusted component, and the SDK's integrity 
    checks always consult it to find the anchor for a given key. 
    The mapping is never modified by any of the attack scenarios, 
    so it always points at the original anchor (or nothing, if the 
    object was never written through the SDK).
"""

import os

import pytest

from securedal import TamperOperator
from securedal.exceptions import (
    TamperDetectedException,
    MissingAnchorException,
    MissingDataException,
    UntrackedObjectException,
    OrphanMappingException,
    BulkTamperException,
)

from dotenv import load_dotenv
load_dotenv()


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def storage_dir(tmp_path):
    """Fresh fs storage directory for each test."""
    path = tmp_path / "storage"
    path.mkdir()
    return str(path)


@pytest.fixture
def mapping_path(tmp_path):
    """Fresh mapping DB path for each test."""
    return str(tmp_path / "mapping" / "tamper_mapping.db")


@pytest.fixture
def tamper_op(storage_dir, mapping_path):
    """A TamperOperator instance backed by a fresh fs root and mapping DB."""
    op = TamperOperator(
        scheme="fs",
        root=storage_dir,
        mapping_path=mapping_path,
    )
    yield op
    op.close()


# ── 1. Valid object (baseline case) ──────────────────────────────────────────

def test_valid_object_round_trip_succeeds(tamper_op):
    """Untampered write + read through the prototype succeeds (no false positive)."""
    tamper_op.write("patient/record.json", b"original clinical data")

    result = tamper_op.read("patient/record.json")

    assert result == b"original clinical data"


# ── 2. Object without anchor ─────────────────────────────────────────────────

def test_object_without_anchor_is_rejected(tamper_op):
    """
    An object written directly to the backend (bypassing TamperOperator.write,
    and therefore never anchored) must be rejected on read.
    """
    tamper_op._operator.write("external/unmanaged.txt", b"not managed by the SDK")

    with pytest.raises(UntrackedObjectException):
        tamper_op.read("external/unmanaged.txt")


# ── 3. Object content tampering ──────────────────────────────────────────────

def test_object_content_tampering_is_detected(tamper_op):
    """
    Data modified directly at the storage layer (bypassing the SDK) must be 
    detected on next read.
    """
    tamper_op.write("patient/blood_test.json", b'{"hemoglobin": 14.2}')

    # Attacker modifies the stored bytes directly through the raw operator,
    # bypassing the SDK's write path entirely.
    tamper_op._operator.write("patient/blood_test.json", b'{"hemoglobin": 99.9}')

    with pytest.raises(TamperDetectedException):
        tamper_op.read("patient/blood_test.json")


# ── 4. Multiple tampered objects (read_all) ──────────────────────────────────

def test_multiple_tampered_objects_detected_by_read_all(tamper_op):
    """
    read_all() must detect and report tampered objects in a batch,
    regardless of which specific object(s) were modified.
    """
    tamper_op.write("d1.txt", b"data one")
    tamper_op.write("d2.txt", b"data two")
    tamper_op.write("d3.txt", b"data three")

    # Attacker tampers with one of several records directly via the backend.
    tamper_op._operator.write("d2.txt", b"TAMPERED")

    with pytest.raises(BulkTamperException) as exc_info:
        tamper_op.read_all("/")

    violations = exc_info.value.violations
    assert "d2.txt" in violations
    assert "d1.txt" not in violations
    assert "d3.txt" not in violations


# ── 5. Deleted object ─────────────────────────────────────────────────────────

def test_deleted_object_is_detected(tamper_op):
    """Unauthorized deletion at the storage layer must not be silently accepted."""
    tamper_op.write("important/contract.pdf", b"binding agreement text")

    # Attacker deletes the record directly from storage, bypassing the
    # SDK's delete path (which would also clean up the anchor).
    tamper_op._operator.delete("important/contract.pdf")

    with pytest.raises(MissingDataException):
        tamper_op.read("important/contract.pdf")


# ── 6. Anchor deletion ─────────────────────────────────────────────────────────

def test_anchor_deletion_from_ipfs_is_detected(tamper_op):
    """
    The attack unpins the anchor's CID from the local IPFS node and runs
    garbage collection, making the anchor content unreachable even though
    the mapping still (correctly, from its own point of view) points at it.
    """
    tamper_op.write("secure/data.bin", b"sensitive payload")

    full_key = tamper_op._eis._full_key("secure/data.bin")
    cid = tamper_op._eis._mapping.get(full_key)

    # Unpin and garbage-collect directly on the raw IPFS client.
    # The mapping entry for "secure/data.bin" is never modified.
    tamper_op._eis._client.pin.rm(cid)
    tamper_op._eis._client.repo.gc()

    with pytest.raises(MissingAnchorException):
        tamper_op.read("secure/data.bin")


# ── 7. Pinned-anchor recovery (Pinata) ───────────────────────────────────────

PINATA_JWT = os.environ.get("JWT")

@pytest.mark.skipif(
    not PINATA_JWT,
    reason="JWT not set — skipping live Pinata recovery test",
)
def test_pinned_anchor_recovery_after_local_loss(storage_dir, mapping_path):
    """
    Verifies resilience when the anchor is lost locally (unpinned + GC'd
    from the local IPFS node, mapping untouched) but was also pinned
    remotely via Pinata. The prototype should still be able to fetch the
    anchor content through the network and verify successfully.
    """
    import time

    op = TamperOperator(
        scheme="fs",
        root=storage_dir,
        mapping_path=mapping_path,
        pinata_token=PINATA_JWT,
    )

    try:
        op.write("backup/record.json", b"important record")

        # Allow the async Pinata pin to complete.
        time.sleep(3)

        full_key = op._eis._full_key("backup/record.json")
        cid = op._eis._mapping.get(full_key)

        # Same attack as scenario 6: remove the anchor from the LOCAL node only.
        # Mapping is untouched. Content remains available via Pinata.
        op._eis._client.pin.rm(cid)
        op._eis._client.repo.gc()

        result = op.read("backup/record.json")
        assert result == b"important record"
    finally:
        op.close()


# ── 8. Anchor injection attack ───────────────────────────────────────────────

def test_anchor_injection_attack_is_rejected(tamper_op):
    """
    An attacker writes data directly to the backend, then attempts to
    forge legitimacy by inserting a matching anchor directly into IPFS
    (bypassing the EIS layer's store_hash, which would be normal SDK
    behaviour, not an attack). The local key->CID mapping has no entry 
    for the forged key, so the SDK should reject the read. In other words, 
    the attacker's injected anchor is simply never consulted.
    """
    forged_key = "external/forged_record.json"
    forged_content = b'{"balance": 1000000}'

    # Attacker writes content directly via the raw operator.
    tamper_op._operator.write(forged_key, forged_content)

    # Attacker inserts a "matching" anchor directly into IPFS, without
    # going through the EIS layer / mapping at all.
    forged_hash = tamper_op._compute_hash(forged_content)
    tamper_op._eis._client.add_bytes(forged_hash)

    # No mapping entry exists for forged_key (the mapping was never
    # touched), so verification fails for lack of an anchor, i.e.,
    # the injected IPFS object is orphaned and irrelevant.
    with pytest.raises(UntrackedObjectException):
        tamper_op.read(forged_key)


# ── 9. Rollback attack ────────────────────────────────────────────────────────

def test_rollback_attack_is_detected(tamper_op):
    """
    Reverting a record to a previous, once-legitimate state via direct
    storage access must still be detected, since the anchor only matches
    the most recently written state.
    """
    version_a = b"version A: initial balance 100"
    version_b = b"version B: updated balance 50"

    tamper_op.write("account/balance.txt", version_a)
    tamper_op.write("account/balance.txt", version_b)

    # Attacker restores version A directly via the raw operator, bypassing
    # the SDK. The mapping still holds the anchor for version B.
    tamper_op._operator.write("account/balance.txt", version_a)

    with pytest.raises(TamperDetectedException):
        tamper_op.read("account/balance.txt")