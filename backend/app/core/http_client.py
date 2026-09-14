"""Global HTTP Client for Connection Pooling."""

import httpx


class HTTPClient:
    """Manages a global httpx.AsyncClient instance for connection pooling."""
    client: httpx.AsyncClient | None = None

    @classmethod
    def get_client(cls, timeout: float = 30.0) -> httpx.AsyncClient:
        if cls.client is None:
            cls.client = httpx.AsyncClient(
                timeout=timeout,
                limits=httpx.Limits(max_keepalive_connections=50, max_connections=100),
                verify=False
            )
        return cls.client

    @classmethod
    async def close_client(cls) -> None:
        if cls.client is not None:
            await cls.client.aclose()
            cls.client = None
