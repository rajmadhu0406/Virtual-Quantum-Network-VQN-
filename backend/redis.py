import aioredis
import logging
import asyncio

logger = logging.getLogger(__name__)


# Redis connection settings
REDIS_HOST = 'redis://localhost'
REDIS_PORT = 6379
REDIS_HASHMAP_KEY_NAME = 'user_requests'
REDIS_URL = 'redis://redis:6379'

REDIS_TOPIC = "user_responses_topic"


class RedisClient:
    def __init__(self):
        self.redis = None
        self.REDIS_HOST = REDIS_HOST
        self.REDIS_PORT = 6379
        self.REDIS_HASHMAP_KEY_NAME = REDIS_HASHMAP_KEY_NAME
        self.REDIS_URL = REDIS_URL
        self.REDIS_TOPIC = REDIS_TOPIC
    
    def __init__(self, REDIS_HOST, REDIS_PORT, REDIS_URL, REDIS_HASHMAP_KEY_NAME="", REDIS_TOPIC=""):
        self.redis = None
        self.REDIS_HOST = REDIS_HOST
        self.REDIS_PORT = REDIS_PORT    
        self.REDIS_HASHMAP_KEY_NAME = REDIS_HASHMAP_KEY_NAME
        self.REDIS_URL = REDIS_URL
        self.REDIS_TOPIC = REDIS_TOPIC
    
    async def get_redis(self):
        # Create and return a Redis connection pool
        if not self.redis:
            #returns a redis connection pool object that manages a pool of connections
            self.redis = await aioredis.from_url(self.REDIS_URL, decode_responses=True)
        return self.redis

    async def add(self, request_id, request_data):
        redis = await self.get_redis()
        await redis.hset(self.REDIS_HASHMAP_KEY_NAME, request_id, request_data)
        print(f"Request {request_id} added to Redis with data : {request_data}")
    
    async def get(self, request_id):
        redis = await self.get_redis()
        request_data = await redis.hget(self.REDIS_HASHMAP_KEY_NAME, request_id)
        return request_data
    
    async def get_first(self):
        redis = await self.get_redis()
        request_data = await redis.hget(self.REDIS_HASHMAP_KEY_NAME, 0)
        return request_data
    
    async def delete(self, request_id):
        redis = await self.get_redis()
        await redis.hdel(self.REDIS_HASHMAP_KEY_NAME, request_id)
        print(f"Request {request_id} deleted from Redis")
    
    async def get_all(self):
        redis = await self.get_redis()
        requests_data = await redis.hgetall(self.REDIS_HASHMAP_KEY_NAME)
        return requests_data    
    
    async def get_length(self):
        redis = await self.get_redis()
        len = await redis.hlen(self.REDIS_HASHMAP_KEY_NAME)
        return len
    
    async def publish(self, message):
        redis = await self.get_redis()
        await redis.publish(self.REDIS_TOPIC, message)
        logger.info(f"Message published to topic : {self.REDIS_TOPIC}") 
    
    












