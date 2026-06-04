"""
请求频率限制模块

基于内存字典的简单速率限制器，用于防止暴力破解和滥用。
每分钟最多允许 max_requests 次请求。
"""

import time
from collections import defaultdict
from fastapi import Request, HTTPException, status


class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._store: dict[str, list[float]] = defaultdict(list)
        self._hits = 0

    def _clean(self, key: str, now: float) -> None:
        cutoff = now - self.window_seconds
        self._store[key] = [t for t in self._store[key] if t > cutoff]

    def _full_clean(self, now: float) -> None:
        cutoff = now - self.window_seconds
        expired = [k for k, v in self._store.items() if not any(t > cutoff for t in v)]
        for k in expired:
            del self._store[k]

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._clean(key, now)
        self._hits += 1
        if self._hits % 1000 == 0:
            self._full_clean(now)
        if len(self._store[key]) >= self.max_requests:
            return False
        self._store[key].append(now)
        return True


_auth_limiter = RateLimiter(max_requests=10, window_seconds=60)


def rate_limit_auth(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    key = f"auth:{client_ip}"
    if not _auth_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试",
        )
