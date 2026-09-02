from __future__ import annotations

import redis
from fastapi import HTTPException, status

from app.config import get_settings


def enforce_rate_limit(scope: str, key: str, limit: int) -> None:
    """Apply a fixed-window Redis limit; local dependency outages fail open for availability."""
    settings = get_settings()
    redis_key = f"dwco:rate:{scope}:{key}"
    try:
        client = redis.from_url(  # type: ignore[no-untyped-call]
            settings.redis_url, socket_connect_timeout=1
        )
        count = int(client.incr(redis_key))
        if count == 1:
            client.expire(redis_key, settings.rate_limit_window_seconds)
    except redis.RedisError:
        return
    if count > limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="rate limit exceeded"
        )
