"""LLM client dung chung — profile/prompt-only, retry/backoff/timeout, structured output.

Nguyen tac: LLM proposes. Engine validates. Human approves. Executor executes.
- Loi provider co kieu (llm_errors): chi retry RateLimit/Timeout/Server.
- Output validate bang Pydantic schema truoc khi dung (complete_model).
- LLM KHONG bao gio nhan raw rows — chi profile JSON / schema / mo ta NL.
"""

import json
import logging
import os
import re
import time

from typing import Any, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

from src.core.llm_errors import ProviderException, classify

logger = logging.getLogger(__name__)

TIMEOUT_S = float(os.environ.get("LLM_TIMEOUT_S", "30"))
MAX_RETRIES = int(os.environ.get("LLM_MAX_RETRIES", "3"))
BACKOFF_S = float(os.environ.get("LLM_BACKOFF_S", "1.0"))

T = TypeVar("T", bound=BaseModel)


def _build_llm(api_key: str, provider: str):
    provider = (provider or "openai").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return (
            ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                api_key=api_key,
                request_timeout=TIMEOUT_S,
                max_retries=0,  # tu retry o day de fallback nhat quan
            ),
            "gpt-4o-mini",
        )
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return (
            ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.3,
                google_api_key=api_key,
            ),
            "gemini-2.0-flash",
        )
    raise ValueError(f"Unknown provider {provider!r} (chon 'openai'|'gemini')")


def _to_lc_messages(messages: List[Dict[str, str]]):
    from langchain_core.messages import HumanMessage, SystemMessage

    out = []
    for m in messages:
        role, content = m.get("role", "user"), m.get("content", "")
        out.append(SystemMessage(content=content) if role == "system" else HumanMessage(content=content))
    return out


def complete_text(api_key: str, provider: str, messages: List[Dict[str, str]]) -> tuple[str, str]:
    """Tra ve (text, model). Raise ProviderException (typed)."""
    llm, model = _build_llm(api_key, provider)
    lc_messages = _to_lc_messages(messages)
    last_exc: Optional[ProviderException] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = llm.invoke(lc_messages)
            return (resp.content or "").strip(), model
        except Exception as exc:
            typed = classify(exc, provider=provider, model=model) if not isinstance(exc, ProviderException) else exc
            last_exc = typed
            if attempt >= MAX_RETRIES or not typed.retryable:
                raise typed from exc
            wait = BACKOFF_S * (2 ** (attempt - 1))
            logger.warning(
                "LLM %s failed (attempt %d/%d, provider=%s): %s — retry sau %.1fs",
                type(typed).__name__,
                attempt,
                MAX_RETRIES,
                provider,
                typed,
                wait,
            )
            time.sleep(wait)
    raise last_exc  # type: ignore[misc]


def extract_json(text: str) -> Dict[str, Any]:
    """Tach JSON ke ca khi LLM boc trong markdown ```json fence."""
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
    """Tra ve (dict, model). Raise ProviderException (parse fail = InvalidRequestError)."""
    from src.core.llm_errors import InvalidRequestError

    text, model = complete_text(api_key, provider, messages)
    try:
        return extract_json(text), model
    except Exception as exc:
        raise InvalidRequestError(
            f"LLM tra ve khong phai JSON: {exc}; text={text[:300]}", provider=provider, model=model
        )


def complete_model(api_key: str, provider: str, messages: List[Dict[str, str]], schema: Type[T]) -> tuple[T, str]:
    """LLM -> JSON -> Pydantic schema validation. Raise ProviderException neu sai schema."""
    from src.core.llm_errors import InvalidRequestError

    data, model = complete_json(api_key, provider, messages)
    try:
        return schema(**data), model
    except Exception as exc:
        raise InvalidRequestError(
            f"LLM output khong dat schema {schema.__name__}: {exc}", provider=provider, model=model
        )
