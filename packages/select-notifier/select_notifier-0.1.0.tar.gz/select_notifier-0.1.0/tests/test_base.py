import pytest
from dataclasses import FrozenInstanceError

from select_notifier.base import (
    Message,
    SendResult,
    Notifier,
    AsyncNotifier,
    normalize_message,
    PermanentNotifierError,
)


# ---------------------------
# Message.ensure_tuple / create
# ---------------------------
def test_ensure_tuple_none_and_list_and_tuple():
    assert Message.ensure_tuple(None) == tuple()
    assert Message.ensure_tuple([]) == tuple()
    assert Message.ensure_tuple(["a", "b"]) == ("a", "b")
    t = ("x", "y")
    assert Message.ensure_tuple(t) == t


def test_message_create_converts_and_copies_meta():
    meta = {"k": "v"}
    m = Message.create(subject="s", body="b", to=["a@b.com"], meta=meta)
    assert isinstance(m.to, tuple)
    assert m.to == ("a@b.com",)
    assert isinstance(m.meta, dict)
    assert m.meta == {"k": "v"}

    meta["k"] = "changed"
    assert m.meta["k"] == "v"


def test_message_is_frozen():
    m = Message.create(subject="s", body="b")
    with pytest.raises(FrozenInstanceError):
        m.subject = "other"


# ---------------------------
# normalize_message
# ---------------------------
@pytest.mark.parametrize("bad_subject", ["", "   ", "\n\t"])
def test_normalize_message_requires_subject(bad_subject):
    with pytest.raises(PermanentNotifierError, match="subject is required"):
        normalize_message(subject=bad_subject, body="body")


@pytest.mark.parametrize("bad_body", ["", "   ", "\n\t"])
def test_normalize_message_requires_body(bad_body):
    with pytest.raises(PermanentNotifierError, match="body is required"):
        normalize_message(subject="subj", body=bad_body)


def test_normalize_message_ok():
    msg = normalize_message(subject=" OK ", body=" body ", to=["x@y.com"], meta={"a": 1})
    assert isinstance(msg, Message)
    assert msg.subject == " OK "
    assert msg.to == ("x@y.com",)
    assert msg.meta == {"a": 1}


# ---------------------------
# SendResult helpers
# ---------------------------
def test_sendresult_success():
    r = SendResult.success(provider="email", message_id="123", raw={"detail": "ok"})
    assert r.ok is True
    assert r.provider == "email"
    assert r.message_id == "123"
    assert r.raw == {"detail": "ok"}
    assert r.error is None
    assert r.retryable is False


def test_sendresult_failure_retryable_and_nonretryable():
    r1 = SendResult.failure(provider="rocket", error="rate limited", retryable=True)
    assert r1.ok is False
    assert r1.retryable is True
    assert r1.error == "rate limited"

    r2 = SendResult.failure(provider="rocket", error="bad request", retryable=False, raw={"code": 400})
    assert r2.ok is False
    assert r2.retryable is False
    assert r2.raw == {"code": 400}


# ---------------------------
# Protocol smoke checks (type-only API surface)
# ---------------------------
def test_notifier_protocol_signature():
    assert hasattr(Notifier, "send")
    assert hasattr(AsyncNotifier, "send_async")
