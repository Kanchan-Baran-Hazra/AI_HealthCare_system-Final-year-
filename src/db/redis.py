import redis.asyncio as aioredis
from src.config import Config  # Adjust to your config import


# Initialize async Redis client
redis_client = aioredis.from_url(
    Config.REDIS_URL, # e.g., "redis://localhost:6379/0"
    encoding="utf-8", 
    decode_responses=True
)



async def add_jti_to_blocklist(jti: str, expiry_seconds: int) -> None:
    """
    Stores the token's JTI in Redis with an expiration equal to the remaining TTL.
    After expiry_seconds, Redis automatically deletes key to save memory.
    """
    await redis_client.set(name=f"blocklist:{jti}", value="revoked", ex=expiry_seconds)


async def is_jti_blocklisted(jti: str) -> bool:
    """Checks whether the token's JTI exists in the Redis blocklist."""
    token_in_redis = await redis_client.get(f"blocklist:{jti}")
    return token_in_redis is not None





