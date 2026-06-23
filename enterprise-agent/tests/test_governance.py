import pytest

from app.governance import (
    AccessDeniedError,
    AuditLog,
    IdempotencyGuard,
    Permission,
    Principal,
    RBACPolicy,
    mask_pii,
)


def test_authorize_operator_can_write() -> None:
    policy = RBACPolicy()
    operator = Principal(user_id="u1", roles=frozenset({"operator"}))
    policy.authorize(operator, Permission.WRITE)


def test_authorize_viewer_cannot_write() -> None:
    policy = RBACPolicy()
    viewer = Principal(user_id="u2", roles=frozenset({"viewer"}))
    with pytest.raises(AccessDeniedError):
        policy.authorize(viewer, Permission.WRITE)


def test_mask_pii_hides_email_and_phone() -> None:
    masked = mask_pii("contact a@b.com au 06 12 34 56 78")
    assert "a@b.com" not in masked
    assert "06 12 34 56 78" not in masked
    assert "[email]" in masked
    assert "[phone]" in masked


def test_idempotency_guard_blocks_replay() -> None:
    guard = IdempotencyGuard()
    assert guard.is_new("k1") is True
    assert guard.is_new("k1") is False


def test_audit_log_records_entry() -> None:
    log = AuditLog()
    principal = Principal(user_id="u3", roles=frozenset({"viewer"}))
    log.record(principal, action="read", resource="doc", allowed=True)
    assert len(log.entries) == 1
    assert log.entries[0].user_id == "u3"
    assert log.entries[0].allowed is True
