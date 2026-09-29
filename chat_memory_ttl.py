from redis_client import get_redis_client

redis_client = get_redis_client()
CHAT_TTL_SECONDS = 20


def add_message(user_id: str, message: str) -> None:
    key = f"chat:{user_id}"
    ## add message to chat history
    redis_client.lpush(key, message)
    redis_client.expire(key, CHAT_TTL_SECONDS)


def get_recent_messages(user_id: str, limit: int = 5):
    key = f"chat:{user_id}"
    return redis_client.lrange(key, 0, limit - 1)