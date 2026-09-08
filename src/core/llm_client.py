"""LLM client dung chung — profile/prompt-only, retry/backoff/timeout, JSON parse an toan.

Dung cho: brief (briefer), pipeline generate (etl_author), dashboard generate (dashboard_author).
LLM KHONG bao gio nhan raw rows — chi profile JSON / schema / mo ta NL.
Het retry -> raise, caller tu fallback rule-based.
"""

import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

TIMEOUT_S = float(os.environ.get("LLM_TIMEOUT_S", "30"))
MAX_RETRIES = int(os.environ.get("LLM_MAX_RETRIES", "3"))
BACKOFF_S = float(os.environ.get("LLM_BACKOFF_S", "1.0"))
_RETRYABLE = ("timeout", "timed out", "rate limit", "429", "503", "502", "500", "connection", "temporarily")


def _retryable(exc: Exception) -> bool:
    msg = f"{type(exc).__name__}: {exc}".lower()
    return any(s in msg for s in _RETRYABLE)


def _build_llm(api_key: str, provider: str):
    provider = (provider or "openai").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return (
            ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=api_key, request_timeout=TIMEOUT_S, max_retries=0),
            "gpt-4o-mini",
        )
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return (
            ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3, google_api_key=api_key),
            "gemini-2.0-flash",
        )
    raise ValueError(f"Unknown provider {provider!r} (chose 'openai'|'gemini')")


def _to_lc_messages(messages: List[Dict[str, str]]):
    from langchain_core.messages import HumanMessage, SystemMessage

    out = []
    for m in messages:
        role, content = m.get("role", "user"), m.get("content", "")
        out.append(SystemMessage(content=content) if role == "system" else HumanMessage(content=content))
    return out


def complete_text(api_key: str, provider: str, messages: List[Dict[str, str]]) -> tuple[str, str]:
    """Tra ve (text, model). Raise neu het retry / provider la."""
    llm, model = _build_llm(api_key, provider)
    lc_messages = _to_lc_messages(messages)
    last_exc: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = llm.invoke(lc_messages)
            return (resp.content or "").strip(), model
        except Exception as exc:
            last_exc = exc
            if attempt >= MAX_RETRIES or not _retryable(exc):
                raise
            wait = BACKOFF_S * (2 ** (attempt - 1))
            logger.warning(
                "LLM text failed attempt %d/%d (%s): %s — retry %.1fs", attempt, MAX_RETRIES, provider, exc, wait
            )
            time.sleep(wait)
    raise last_exc  # type: ignore[misc]


def extract_json(text: str) -> Dict[str, Any]:
    """Parse JSON ke ca khi LLM boc trong markdown ```json fence."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        text = m.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            text = text[start : end + 1]
    return json.loads(text)


def complete_json(api_key: str, provider: str, messages: List[Dict[str, str]]) -> tuple[Dict[str, Any], str]:
    """Tra ve (dict, model). Raise neu het retry / khong parse duoc JSON."""
    text, model = complete_text(api_key, provider, messages)
    try:
        return extract_json(text), model
    except Exception as exc:
        raise ValueError(f"LLM tra ve khong phai JSON: {exc}; text={text[:300]}")
