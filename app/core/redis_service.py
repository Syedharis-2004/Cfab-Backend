import logging
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisService:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisService, cls).__new__(cls)
        return cls._instance

    async def get_client(self):
        if self._client is None:
            try:
                self._client = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                )
                # Test connection
                await self._client.ping()
                logger.info("✅ Redis connected successfully.")
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {str(e)}")
                self._client = None
        return self._client

    async def is_available(self):
        client = await self.get_client()
        if client is None:
            return False
        try:
            await client.ping()
            return True
        except:
            return False

redis_service = RedisService()
