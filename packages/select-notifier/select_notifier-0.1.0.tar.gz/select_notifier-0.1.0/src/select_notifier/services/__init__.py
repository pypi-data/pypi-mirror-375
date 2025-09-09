from __future__ import annotations

__all__ = ["EmailNotifier", "SMTPConfig", "RocketNotifier", "RocketConfig"]

def __getattr__(name: str):
    if name in ("EmailNotifier", "SMTPConfig"):
        from .email import EmailNotifier, SMTPConfig
        return {"EmailNotifier": EmailNotifier, "SMTPConfig": SMTPConfig}[name]
    if name in ("RocketNotifier", "RocketConfig"):
        from .rocket import RocketNotifier, RocketConfig
        return {"RocketNotifier": RocketNotifier, "RocketConfig": RocketConfig}[name]
    raise AttributeError(name)
