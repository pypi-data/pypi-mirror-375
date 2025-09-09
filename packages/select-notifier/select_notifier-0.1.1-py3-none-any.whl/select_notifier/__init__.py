from __future__ import annotations

from typing import TYPE_CHECKING

from .__version__ import __version__
from .base import (
    Message,
    SendResult,
    Notifier,
    AsyncNotifier,
    NotifierError,
    TransientNotifierError,
    PermanentNotifierError,
    normalize_message,
)

__all__ = [
    # core
    "Message",
    "SendResult",
    "Notifier",
    "AsyncNotifier",
    "NotifierError",
    "TransientNotifierError",
    "PermanentNotifierError",
    "normalize_message",
    "__version__",
    # services (lazy)
    "EmailNotifier",
    "RocketNotifier",
    "SMTPConfig",
    "RocketConfig",
]

if TYPE_CHECKING:
    from .services.email import EmailNotifier, SMTPConfig
    from .services.rocket import RocketNotifier, RocketConfig


def __getattr__(name: str):
    if name in ("EmailNotifier", "SMTPConfig"):
        from .services.email import EmailNotifier, SMTPConfig
        return {"EmailNotifier": EmailNotifier, "SMTPConfig": SMTPConfig}[name]
    if name in ("RocketNotifier", "RocketConfig"):
        from .services.rocket import RocketNotifier, RocketConfig
        return {"RocketNotifier": RocketNotifier, "RocketConfig": RocketConfig}[name]
    raise AttributeError(name)


def __dir__():
    return sorted(set(globals().keys()) | {"EmailNotifier", "SMTPConfig", "RocketNotifier", "RocketConfig"})
