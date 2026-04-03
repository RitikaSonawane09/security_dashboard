import os

try:
    import redis

    r = redis.Redis(
        host=os.environ.get("REDIS_HOST", "localhost"),
        port=int(os.environ.get("REDIS_PORT", 6379)),
        password=os.environ.get("REDIS_PASSWORD"),
        decode_responses=True
    )

    r.ping()  # test connection
    print("✅ Connected to Redis")

except Exception as e:
    print("⚠️ Redis not available, using in-memory storage")

    class FakeRedis:
        def __init__(self):
            self.store = {}

        def lpush(self, key, value):
            self.store.setdefault(key, []).insert(0, value)

        def ltrim(self, key, start, end):
            if key in self.store:
                self.store[key] = self.store[key][start:end+1]

        def lrange(self, key, start, end):
            return self.store.get(key, [])[start:end+1]

        def llen(self, key):
            return len(self.store.get(key, []))

    r = FakeRedis()