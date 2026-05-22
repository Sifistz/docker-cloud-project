from flask import Flask, jsonify
import time
import redis
import os

app = Flask(__name__)
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
cache = redis.from_url(redis_url, decode_responses=True)

@app.route("/")
def home():
    return jsonify({
        "message": "Docker Demo App",
        "status": "running"
    })

@app.route("/method1")
def method1():
    start = time.time()

    time.sleep(1)

    end = time.time()

    return jsonify({
        "method": "without cache",
        "response_time": round(end - start, 3)
    })
    
@app.route("/method2")
def method2():
    start = time.time()

    cached_result = cache.get("demo_result")

    if cached_result:
        end = time.time()
        return jsonify({
            "method": "with redis cache",
            "cache": "hit",
            "response_time": round(end - start, 3)
        })

    time.sleep(1)
    cache.set("demo_result", "result saved in redis")

    end = time.time()
    return jsonify({
        "method": "with redis cache",
        "cache": "miss",
        "response_time": round(end - start, 3)
    })
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)