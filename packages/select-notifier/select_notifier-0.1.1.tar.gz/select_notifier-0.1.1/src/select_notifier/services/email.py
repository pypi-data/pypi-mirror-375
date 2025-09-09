from __future__ import annotations

import logging
import re
import smtplib
import ssl
import time
import unicodedata
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from smtplib import SMTPAuthenticationError
from typing import Callable, ContextManager, Protocol

from select_notifier.base import (
    Message,
    SendResult,
    Notifier,
    normalize_message,
    TransientNotifierError,
    PermanentNotifierError,
)

# ---------------------------------
# Logging
# ---------------------------------
logger = logging.getLogger("select_notifier.email")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


# ---------------------------------
# Config
# ---------------------------------
@dataclass(frozen=True)
class SMTPConfig:
    server: str
    port: int
    sender: str
    password: str
    use_tls: bool = True   # STARTTLS (587)
    use_ssl: bool = False  # SMTPS (465)
    timeout: float = 30.0


# ---------------------------------
# SMTP factory protocol (DIP)
# ---------------------------------
class SMTPContextFactory(Protocol):
    def __call__(self, server: str, port: int, timeout: float) -> ContextManager[smtplib.SMTP]: ...


def _default_smtp_factory(
    server: str, port: int, timeout: float, *, use_ssl: bool
) -> ContextManager[smtplib.SMTP]:
    if use_ssl:
        return smtplib.SMTP_SSL(server, port, timeout=timeout)  # type: ignore[return-value]
    return smtplib.SMTP(server, port, timeout=timeout)  # type: ignore[return-value]


# ---------------------------------
# EmailNotifier (implements Notifier)
# ---------------------------------
class EmailNotifier(Notifier):
    provider_name = "email"
    _EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(
        self,
        config: SMTPConfig,
        *,
        retries: int = 2,
        backoff: float = 1.5,
        smtp_factory: Callable[[str, int, float], ContextManager[smtplib.SMTP]] | None = None,
    ) -> None:
        norm_pwd = self._normalize_secret(config.password)
        object.__setattr__(config, "password", norm_pwd)

        self._cfg = config
        self._retries = retries
        self._backoff = backoff
        self._smtp_factory = smtp_factory or (
            lambda host, port, timeout: _default_smtp_factory(
                host, port, timeout, use_ssl=config.use_ssl
            )
        )

    # -------- Public: Notifier API --------
    def send(self, message: Message) -> SendResult:
        if not message.to:
            raise PermanentNotifierError("'to' is required for EmailNotifier")
        self._validate_email(self._cfg.sender, "sender")
        for addr in message.to:
            self._validate_email(addr, "recipient")

        msg = self._build_text_message(
            sender=self._cfg.sender,
            to=", ".join(message.to),
            subject=message.subject,
            body_text=message.body,
        )

        attempt = 0
        last_err: Exception | None = None

        while attempt <= self._retries:
            attempt += 1
            try:
                logger.info("Email send (attempt %d/%d) to %s", attempt, self._retries + 1, message.to)

                context = ssl.create_default_context()
                with self._smtp_factory(self._cfg.server, self._cfg.port, self._cfg.timeout) as smtp:
                    smtp.ehlo()
                    if self._cfg.use_tls and not self._cfg.use_ssl:
                        smtp.starttls(context=context)
                        smtp.ehlo()
                    smtp.login(self._cfg.sender, self._cfg.password)
                    smtp.send_message(msg)

                logger.info("Email sent successfully to %s", message.to)
                return SendResult.success(provider=self.provider_name)

            except SMTPAuthenticationError as e:
                last_err = e
                logger.warning("SMTP auth failed (attempt %d): %s", attempt, e)
                if attempt > self._retries:
                    raise PermanentNotifierError(str(e)) from e
                time.sleep(self._backoff**attempt)

            except (smtplib.SMTPException, OSError) as e:
                last_err = e
                logger.warning("SMTP send failed (attempt %d): %r", attempt, e)
                if attempt > self._retries:
                    raise TransientNotifierError(str(e)) from e
                time.sleep(self._backoff**attempt)

        raise TransientNotifierError(
            f"Failed to send email to {message.to!r} via {self._cfg.server}:{self._cfg.port} "
            f"after {attempt} attempts."
        ) from last_err

    # -------- Convenience wrapper --------
    def send_text(
        self,
        *,
        subject: str,
        body: str,
        to: list[str] | tuple[str, ...],
    ) -> SendResult:
        msg = normalize_message(subject=subject, body=body, to=to)
        return self.send(msg)

    # -------- Private helpers --------
    @staticmethod
    def _validate_email(addr: str, label: str) -> None:
        if not addr or not EmailNotifier._EMAIL_RE.match(addr):
            raise PermanentNotifierError(f"Invalid {label} email address: {addr!r}")

    @staticmethod
    def _normalize_secret(secret: str) -> str:
        s = "".join(ch for ch in secret if not ch.isspace())
        s = "".join(str(unicodedata.digit(ch)) if ch.isdigit() and not ch.isascii() else ch for ch in s)
        return s

    @staticmethod
    def _build_text_message(*, sender: str, to: str, subject: str, body_text: str) -> EmailMessage:
        if not subject.strip():
            raise PermanentNotifierError("subject is required")
        if not body_text.strip():
            raise PermanentNotifierError("body is required")

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = to
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        msg.set_content(body_text)
        return msg

    # -------- Factory method --------
    @classmethod
    def create(
        cls,
        *,
        sender: str,
        password: str,
        server: str,
        port: int,
        use_tls: bool = True,
        use_ssl: bool = False,
        timeout: float = 30.0,
        retries: int = 2,
        backoff: float = 1.5,
    ) -> EmailNotifier:
        cfg = SMTPConfig(
            server=server,
            port=port,
            sender=sender,
            password=password,
            use_tls=use_tls,
            use_ssl=use_ssl,
            timeout=timeout,
        )
        return cls(cfg, retries=retries, backoff=backoff)
