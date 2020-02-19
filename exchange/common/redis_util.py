import json

import django_redis


def get_redis_connection():
    return django_redis.get_redis_connection()


def save_to_redis(redis_key, value: str, timeout):
    redis = get_redis_connection()
    redis.set(redis_key, value, timeout)


def get_from_redis_as_json(redis_key) -> dict:
    redis = get_redis_connection()
    value = redis.get(redis_key)
    return json.loads(value) if value else None


def get_from_redis(redis_key):
    redis = get_redis_connection()
    return redis.get(redis_key)


def delete_from_redis(redis_key):
    redis = get_redis_connection()
    redis.delete(redis_key)
