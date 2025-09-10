from __future__ import annotations

from dataclasses import dataclass

import redis


@dataclass(frozen=True)
class RedisConfig:
    """Configuration for creating Redis client instances.

    Avoid logging sensitive fields like password in your application code.
    """

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    username: str | None = None
    ssl: bool = False
    decode_responses: bool = True
    socket_timeout: float | None = None
    health_check_interval: int = 0


def get_redis(config: RedisConfig | None = None) -> redis.Redis:
    """Create a synchronous Redis client using the provided configuration.

    Parameters
    ----------
    config: RedisConfig | None
        Configuration. If None, defaults will be used.

    Returns
    -------
    redis.Redis
        A configured Redis client.
    """
    cfg = config or RedisConfig()
    return redis.Redis(
        host=cfg.host,
        port=cfg.port,
        db=cfg.db,
        password=cfg.password,
        username=cfg.username,
        ssl=cfg.ssl,
        decode_responses=cfg.decode_responses,
        socket_timeout=cfg.socket_timeout,
        health_check_interval=cfg.health_check_interval,
    )