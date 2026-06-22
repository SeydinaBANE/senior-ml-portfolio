import uuid

import pytest

from app.security.auth import create_access_token, decode_token


def test_create_and_decode_token_roundtrip() -> None:
    tenant_id = uuid.uuid4()
    token = create_access_token("user-1", tenant_id)
    payload = decode_token(token)

    assert payload.sub == "user-1"
    assert payload.tenant_id == str(tenant_id)


def test_decode_invalid_token_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_token("not.a.valid.token")


def test_decode_tampered_signature_raises() -> None:
    tenant_id = uuid.uuid4()
    token = create_access_token("user-1", tenant_id)
    tampered = token[:-8] + "XXXXXXXX"
    with pytest.raises(ValueError):
        decode_token(tampered)


def test_different_tenants_produce_different_tokens() -> None:
    t1, t2 = uuid.uuid4(), uuid.uuid4()
    assert create_access_token("u", t1) != create_access_token("u", t2)
