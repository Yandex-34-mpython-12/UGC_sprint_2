from redis import Redis
from backoff import backoff


# Define a function to attempt connecting to redis
def connect_to_redis():
    redis = Redis(host='redis', port=6379)
    if redis.ping():
        print('Connected to redis successfully!')
        return redis
    else:
        print('Failed to connect to redis.')
        raise ConnectionError('redis ping failed.')


# Use backoff to handle retries
@backoff
def main():
    redis = connect_to_redis()
    return redis


if __name__ == '__main__':
    redis = main()
