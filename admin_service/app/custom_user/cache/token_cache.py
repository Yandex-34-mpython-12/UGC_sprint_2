from django.core.cache import cache


def cache_token(user_id, token, ttl=3600):
    """
    Caches a token in Redis with a specific time to live (TTL).
    :param user_id: The ID of the user to whom the token belongs.
    :param token: The token string.
    :param ttl: Time to live for the token in seconds.
    """
    cache_key = f"user:{user_id}:token"
    cache.set(cache_key, token, timeout=ttl)


def get_cached_token(user_id):
    """
    Retrieves a token from the cache if it exists.
    :param user_id: The ID of the user to whom the token belongs.
    :return: The token string if found, else None.
    """
    cache_key = f"user:{user_id}:token"
    return cache.get(cache_key)
