"""
请求频率限制模块

基于内存字典的简单速率限制器，用于防止暴力破解和滥用。
每分钟最多允许 max_requests 次请求，字典最多保留 max_store_size 个 key。

注意：此限流器基于进程内存，多 worker 部署（uvicorn --workers N）时各进程独立计数，
限流粒度变为"每 worker N 次"。生产环境应改用 Redis 等共享存储实现分布式限流。
"""

import time
import threading
from fastapi import Request, HTTPException, status


class RateLimiter:
    def __init__(self, max_requests: int = 5, window_seconds: int = 60, max_store_size: int = 10000):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_store_size = max_store_size
        self._store: dict[str, list[float]] = {}
        self._hits = 0
        self._lock = threading.Lock()

    def _clean(self, key: str, now: float) -> None:
        if key not in self._store:
            return
        cutoff = now - self.window_seconds
        self._store[key] = [t for t in self._store[key] if t > cutoff]
        if not self._store[key]:
            del self._store[key]

    def _full_clean(self, now: float) -> None:
        cutoff = now - self.window_seconds
        expired = [k for k, v in self._store.items() if not any(t > cutoff for t in v)]
        for k in expired:
            del self._store[k]

    def is_allowed(self, key: str) -> bool:
        with self._lock:
            now = time.time()
            self._hits += 1
            if self._hits % 1000 == 0:
                self._full_clean(now)

        is_new = key not in self._store
        if is_new:
            if len(self._store) >= self.max_store_size:
                self._full_clean(now)
            if len(self._store) >= self.max_store_size:
                oldest = min(self._store.keys(), key=lambda k: self._store[k][-1] if self._store[k] else 0)
                del self._store[oldest]
                self._store[key] = []

            self._clean(key, now)
            if not self._store.get(key):
                self._store[key] = []
            if len(self._store[key]) >= self.max_requests:
                return False
            self._store[key].append(now)
            return True


_auth_limiter = RateLimiter(max_requests=10, window_seconds=60)


def rate_limit_auth(request: Request):
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    key = f"auth:{client_ip}"
    if not _auth_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="请求过于频繁，请稍后再试",
        )
