"""Typed LLM provider exceptions (thay string-matching retry).

LLMProvider
    ↓
ProviderException
    ├── RateLimitError      -> retry (backoff)
    ├── TimeoutError        -> retry (backoff)
    ├── ServerError         -> retry (backoff)
    ├── AuthenticationError -> NO retry, fallback ngay
    └── InvalidRequestError -> NO retry, fallback ngay
"""

from typing import Optional


class ProviderException(Exception):
    """Base cho moi loi tu LLM provider."""

    retryable: bool = False

    def __init__(self, message: str, *, provider: str = "", model: str = "", status: Optional[int] = None):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.status = status


class RateLimitError(ProviderException):
    retryable = True


class TimeoutError(ProviderException):  # noqa: A001 - co y trung ten builtin de map ro
    retryable = True


class ServerError(ProviderException):
    retryable = True


class AuthenticationError(ProviderException):
    retryable = False


class InvalidRequestError(ProviderException):
    retryable = False


def classify(exc: Exception, *, provider: str = "", model: str = "") -> ProviderException:
    """Map exception cua langchain/SDK -> typed ProviderException."""
    if isinstance(exc, ProviderException):
        return exc
    name = type(exc).__name__
    mod = type(exc).__module__ or ""
    text = f"{name}: {exc}"
    status = getattr(exc, "status_code", None) or getattr(exc, "status", None)

    # OpenAI SDK typed errors (langchain_openai dung openai package)
    if "openai" in mod:
        if name in ("RateLimitError",):
            return RateLimitError(text, provider=provider, model=model, status=429)
        if name in ("APITimeoutError", "Timeout"):
            return TimeoutError(text, provider=provider, model=model)
        if name in ("AuthenticationError", "PermissionDeniedError"):
            return AuthenticationError(text, provider=provider, model=model, status=401)
        if name in ("BadRequestError", "NotFoundError", "UnprocessableEntityError"):
            return InvalidRequestError(text, provider=provider, model=model, status=status)
        if name in ("APIConnectionError", "APIResponseValidationError", "InternalServerError"):
            return ServerError(text, provider=provider, model=model, status=status or 500)
    # Google GenAI SDK
    if "google" in mod:
        if status == 429 or "RESOURCE_EXHAUSTED" in text or "quota" in text.lower():
            return RateLimitError(text, provider=provider, model=model, status=429)
        if status in (500, 502, 503, 504) or "UNAVAILABLE" in text:
            return ServerError(text, provider=provider, model=model, status=status)
        if status in (401, 403) or "UNAUTHENTICATED" in text or "API key" in text:
            return AuthenticationError(text, provider=provider, model=model, status=status)
        if status == 400 or "INVALID_ARGUMENT" in text:
            return InvalidRequestError(text, provider=provider, model=model, status=400)
    # Langchain wrappers
    if "langchain" in mod:
        if "output" in text.lower() and "pars" in text.lower():
            return InvalidRequestError(f"LLM output parse failed: {exc}", provider=provider, model=model)

    # Fallback theo status / noi dung (van giu, nhung chi la cuoi cung)
    if status == 400:
        return InvalidRequestError(text, provider=provider, model=model, status=status)
    if status == 429:
        return RateLimitError(text, provider=provider, model=model, status=status)
    if status in (500, 502, 503, 504):
        return ServerError(text, provider=provider, model=model, status=status)
    if status in (401, 403):
        return AuthenticationError(text, provider=provider, model=model, status=status)
    lowered = text.lower()
    if "timed out" in lowered or "timeout" in lowered:
        return TimeoutError(text, provider=provider, model=model)
    if "rate limit" in lowered or "too many requests" in lowered:
        return RateLimitError(text, provider=provider, model=model)
    return ServerError(text, provider=provider, model=model, status=status)
