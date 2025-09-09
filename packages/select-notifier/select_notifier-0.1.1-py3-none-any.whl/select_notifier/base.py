from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Mapping, Any, Iterable, Optional


# -----------------------------
# Message Model
# -----------------------------
@dataclass(frozen=True)
class Message:
    """
    Unified message model all notifiers accept.
    """
    subject: str
    body: str
    to: tuple[str, ...] = field(default_factory=tuple)
    meta: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def ensure_tuple(values: Optional[Iterable[str]]) -> tuple[str, ...]:
        if not values:
            return tuple()
        return tuple(values)

    @classmethod
    def create(
        cls,
        *,
        subject: str,
        body: str,
        to: Optional[Iterable[str]] = None,
        meta: Optional[Mapping[str, Any]] = None,
    ) -> "Message":
        """Helper constructor that accepts list/dict inputs."""
        return cls(
            subject=subject,
            body=body,
            to=cls.ensure_tuple(to),
            meta=dict(meta or {}),
        )


# -----------------------------
# Results & Exceptions
# -----------------------------
@dataclass(frozen=True)
class SendResult:
    ok: bool
    provider: str
    message_id: Optional[str] = None
    raw: Optional[Mapping[str, Any]] = None
    error: Optional[str] = None
    retryable: bool = False

    @classmethod
    def success(
        cls,
        provider: str,
        message_id: Optional[str] = None,
        raw: Optional[Mapping[str, Any]] = None,
    ) -> "SendResult":
        return cls(ok=True, provider=provider, message_id=message_id, raw=raw)

    @classmethod
    def failure(
        cls,
        provider: str,
        error: str,
        *,
        retryable: bool = False,
        raw: Optional[Mapping[str, Any]] = None,
    ) -> "SendResult":
        return cls(ok=False, provider=provider, error=error, retryable=retryable, raw=raw)


class NotifierError(Exception):
    """Base error for notifier implementations."""


class TransientNotifierError(NotifierError):
    """
    Indicates the send may succeed if retried
    (network hiccup, 5xx, rate-limit).
    """


class PermanentNotifierError(NotifierError):
    """
    Indicates a non-retryable failure (invalid config, bad request).
    """


# -----------------------------
# Interfaces
# -----------------------------
class Notifier(Protocol):
    """Synchronous notifier interface."""
    provider_name: str

    def send(self, message: Message) -> SendResult: ...


class AsyncNotifier(Protocol):
    """Asynchronous notifier interface."""
    provider_name: str

    async def send_async(self, message: Message) -> SendResult: ...


# -----------------------------
# Helper
# -----------------------------
def normalize_message(
    subject: str,
    body: str,
    *,
    to: Optional[Iterable[str]] = None,
    meta: Optional[Mapping[str, Any]] = None,
) -> Message:
    """Convenience helper for clients to build a valid Message."""
    msg = Message.create(subject=subject, body=body, to=to, meta=meta)
    if not msg.subject.strip():
        raise PermanentNotifierError("subject is required")
    if not msg.body.strip():
        raise PermanentNotifierError("body is required")
    return msg
