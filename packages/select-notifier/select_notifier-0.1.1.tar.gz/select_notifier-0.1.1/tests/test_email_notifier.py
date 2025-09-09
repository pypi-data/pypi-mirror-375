import smtplib
from smtplib import SMTPAuthenticationError
import ssl
import types
import pytest

from select_notifier.base import Message, PermanentNotifierError, TransientNotifierError
from select_notifier.services.email import EmailNotifier, SMTPConfig


# ---------- Helpers: Dummy SMTP contexts ----------
def make_dummy_smtp(success_after=0, auth_error=False, record=None, use_starttls=True):
    attempts = {"count": 0}
    record = record if record is not None else {}

    class DummySMTP:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False

        def ehlo(self): record["ehlo"] = record.get("ehlo", 0) + 1

        def starttls(self, context=None):
            assert isinstance(context, ssl.SSLContext)
            record["starttls"] = record.get("starttls", 0) + 1

        def login(self, user, pwd):
            record["login"] = (user, pwd)
            if auth_error:
                raise SMTPAuthenticationError(535, b"5.7.8 Authentication failed")

        def send_message(self, msg):
            attempts["count"] += 1
            record["last_msg"] = msg
            if attempts["count"] <= success_after:
                raise smtplib.SMTPException("transient failure")

    def factory(host, port, timeout):
        record["factory_args"] = (host, port, timeout)
        return DummySMTP()

    return factory


# ---------- Fixtures ----------
@pytest.fixture
def cfg_valid():
    return SMTPConfig(
        server="smtp.test.local",
        port=587,
        sender="from@example.com",
        password=" ap۱۲۳ 4 ",   # -> "ap1234"
        use_tls=True,
        use_ssl=False,
        timeout=5.0,
    )


# ---------- Tests ----------
def test_send_success(cfg_valid, monkeypatch):
    rec = {}
    smtp_factory = make_dummy_smtp(success_after=0, record=rec)
    notifier = EmailNotifier(cfg_valid, retries=0, backoff=1.0, smtp_factory=smtp_factory)

    res = notifier.send_text(subject="OK", body="hello", to=["rcpt@example.com"])
    assert res.ok is True
    assert res.provider == "email"
    assert rec["last_msg"]["From"] == cfg_valid.sender
    assert rec["last_msg"]["To"] == "rcpt@example.com"
    assert rec["last_msg"]["Subject"] == "OK"


def test_missing_to_raises(cfg_valid):
    notifier = EmailNotifier(cfg_valid, smtp_factory=make_dummy_smtp())
    msg = Message.create(subject="s", body="b", to=[])
    with pytest.raises(PermanentNotifierError, match="'to' is required"):
        notifier.send(msg)


@pytest.mark.parametrize("bad_sender", ["", "foo", "foo@", "foo@bar", "a@b", "no-at-symbol.com"])
def test_invalid_sender_raises(bad_sender, cfg_valid):
    bad_cfg = SMTPConfig(
        server=cfg_valid.server,
        port=cfg_valid.port,
        sender=bad_sender,
        password=cfg_valid.password,
        use_tls=True,
        use_ssl=False,
        timeout=cfg_valid.timeout,
    )
    notifier = EmailNotifier(bad_cfg, smtp_factory=make_dummy_smtp())
    with pytest.raises(PermanentNotifierError, match="Invalid sender"):
        notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])


@pytest.mark.parametrize("bad_rcpt", ["", "x@", "x@z", "no-at"])
def test_invalid_recipient_raises(bad_rcpt, cfg_valid):
    notifier = EmailNotifier(cfg_valid, smtp_factory=make_dummy_smtp())
    with pytest.raises(PermanentNotifierError, match="Invalid recipient"):
        notifier.send_text(subject="s", body="b", to=[bad_rcpt])


def test_auth_error_eventually_permanent(monkeypatch, cfg_valid):
    monkeypatch.setattr("time.sleep", lambda s: None)
    smtp_factory = make_dummy_smtp(auth_error=True)
    notifier = EmailNotifier(cfg_valid, retries=1, backoff=1.1, smtp_factory=smtp_factory)
    with pytest.raises(PermanentNotifierError, match="Authentication"):
        notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])


def test_transient_failure_then_success(monkeypatch, cfg_valid):
    monkeypatch.setattr("time.sleep", lambda s: None)
    rec = {}
    smtp_factory = make_dummy_smtp(success_after=1, record=rec)
    notifier = EmailNotifier(cfg_valid, retries=2, backoff=1.1, smtp_factory=smtp_factory)
    res = notifier.send_text(subject="retry", body="will pass on 2nd", to=["rcpt@example.com"])
    assert res.ok is True
    assert rec.get("starttls", 0) >= 1


def test_transient_failure_exhausts_retries(monkeypatch, cfg_valid):
    monkeypatch.setattr("time.sleep", lambda s: None)
    smtp_factory = make_dummy_smtp(success_after=99)
    notifier = EmailNotifier(cfg_valid, retries=1, backoff=1.1, smtp_factory=smtp_factory)
    with pytest.raises(TransientNotifierError):
        notifier.send_text(subject="retry", body="never", to=["rcpt@example.com"])


def test_password_normalization_applied(cfg_valid):
    n = EmailNotifier(cfg_valid, smtp_factory=make_dummy_smtp())
    assert n._cfg.password == "ap1234"


def test_starttls_used_when_tls_true(cfg_valid):
    rec = {}
    smtp_factory = make_dummy_smtp(record=rec)
    notifier = EmailNotifier(cfg_valid, smtp_factory=smtp_factory)
    notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])
    assert rec.get("starttls", 0) >= 1


def test_no_starttls_when_tls_false():
    cfg = SMTPConfig(
        server="smtp.test.local",
        port=587,
        sender="from@example.com",
        password="x",
        use_tls=False,
        use_ssl=False,
        timeout=5.0,
    )
    rec = {}
    smtp_factory = make_dummy_smtp(record=rec)
    notifier = EmailNotifier(cfg, smtp_factory=smtp_factory)
    notifier.send_text(subject="s", body="b", to=["rcpt@example.com"])
    assert rec.get("starttls", 0) == 0
