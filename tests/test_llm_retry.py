"""Unit tests muc 14: retry/backoff LLM + fallback rule-based."""

import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

from src.core import ai_service as mod
from src.core.ai_service import AIService


def _df():
    return pd.DataFrame({"score": [5.0, 6.0, 7.0], "grp": ["A", "B", "A"]})


def test_retry_then_success(monkeypatch):
    """Lan 1 timeout, lan 2 ok -> dung ket qua LLM."""
    monkeypatch.setattr(mod, "LLM_BACKOFF_S", 0)
    svc = AIService(api_key="sk-x", provider="openai")
    fake = MagicMock()
    resp = MagicMock()
    resp.content = '{"summary": "ok", "insights": [], "recommendations": ["r1"]}'
    fake.invoke.side_effect = [TimeoutError("timed out"), resp]
    svc._llm = fake
    svc._initialized = True
    report = svc.generate_report(_df())
    assert report.summary == "ok"
    assert report.model_used == "openai"
    assert fake.invoke.call_count == 2


def test_classify_typed_errors():
    """Muc production-grade: loi co kieu, retry dung loai."""
    from src.core.llm_errors import (
        AuthenticationError,
        InvalidRequestError,
        ProviderException,
        RateLimitError,
        ServerError,
        TimeoutError,
        classify,
    )

    assert isinstance(classify(TimeoutError("timed out")), TimeoutError)
    assert isinstance(classify(RateLimitError("429")), RateLimitError)
    assert isinstance(classify(AuthenticationError("401")), AuthenticationError)
    err400 = ValueError("bad request")
    err400.status_code = 400  # type: ignore[attr-defined]
    assert isinstance(classify(err400), InvalidRequestError)
    assert isinstance(classify(ValueError("boom")), ServerError)
    assert isinstance(classify(ValueError("x")), ProviderException)


def test_non_retryable_no_retry():
    """Loi khong retryable -> raise ngay, fallback rule-based."""
    svc = AIService(api_key="sk-x", provider="openai")
    fake = MagicMock()
    err = ValueError("bad request: invalid prompt")
    err.status_code = 400  # type: ignore[attr-defined]
    fake.invoke.side_effect = err
    svc._llm = fake
    svc._initialized = True
    report = svc.generate_report(_df())
    assert report.model_used == "rule-based"
    assert fake.invoke.call_count == 1


def test_all_retries_fail_fallback(monkeypatch):
    """Het retry -> fallback rule-based, khong crash."""
    monkeypatch.setattr(mod, "LLM_BACKOFF_S", 0)
    svc = AIService(api_key="sk-x", provider="openai")
    fake = MagicMock()
    fake.invoke.side_effect = TimeoutError("connection timed out")
    svc._llm = fake
    svc._initialized = True
    report = svc.generate_report(_df())
    assert report.model_used == "rule-based"
    assert fake.invoke.call_count == mod.LLM_MAX_RETRIES


def test_singleton_keyed_by_key():
    """2 key khac nhau -> 2 service (chong cross-user leak)."""
    mod.reset_ai_service()
    a = mod.get_ai_service(api_key="sk-aaa", provider="openai")
    b = mod.get_ai_service(api_key="sk-bbb", provider="openai")
    c = mod.get_ai_service(api_key="sk-aaa", provider="openai")
    assert a is not b
    assert a is c
    mod.reset_ai_service()
