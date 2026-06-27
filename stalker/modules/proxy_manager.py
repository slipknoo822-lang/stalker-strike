"""HTTP client factory — stealth headers injection.

Replaces raw httpx.AsyncClient across all Stalker modules.
"""

from __future__ import annotations
import httpx


def prepare_client(**kwargs) -> httpx.AsyncClient:
    """Create httpx.AsyncClient with stealth header injection.

    Uses STEALTH_RANDOM_UA config from environment.
    All stalker modules should use this instead of httpx.AsyncClient directly.

    Usage:
        from .proxy_manager import prepare_client
        async with prepare_client(timeout=10) as client:
            resp = await client.get(url)
    """
    from ..config import Config

    user_headers = kwargs.pop("headers", None) or {}

    headers = None
    if Config.STEALTH_RANDOM_UA:
        try:
            from . import stealth_profile
            headers = stealth_profile.random_headers(user_headers)
        except ImportError:
            if user_headers:
                headers = user_headers
    elif user_headers:
        headers = user_headers

    return httpx.AsyncClient(headers=headers, **kwargs)
