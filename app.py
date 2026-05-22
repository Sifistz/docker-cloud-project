from flask import Flask, jsonify
import time
import redis
import os
import csv
import json

app = Flask(__name__)

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
cache = redis.from_url(redis_url, decode_responses=True)


def process_dataset():
    total = 0
    survived = 0
    total_age = 0
    age_count = 0
    total_fare = 0

    with open("data.csv", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            total += 1
            survived += int(row["Survived"])

            if row["Age"]:
                total_age += float(row["Age"])
                age_count += 1

            if row["Fare"]:
                total_fare += float(row["Fare"])

    return {
        "total_passengers": total,
        "survived_passengers": survived,
        "average_age": round(total_age / age_count, 2),
        "average_fare": round(total_fare / total, 2)
    }


@app.route("/")
def home():
    return jsonify({
        "message": "Docker Demo App with Titanic Dataset",
        "status": "running"
    })


@app.route("/method1")
def method1():
    start = time.time()

    result = process_dataset()

    end = time.time()

    return jsonify({
        "method": "without cache",
        "dataset": "Titanic",
        "data": result,
        "response_time": round(end - start, 3)
    })


@app.route("/method2")
def method2():
    start = time.time()

    cached_result = cache.get("titanic_result")

    if cached_result:
        end = time.time()
        return jsonify({
            "method": "with redis cache",
            "dataset": "Titanic",
            "cache": "hit",
            "data": json.loads(cached_result),
            "response_time": round(end - start, 3)
        })

    result = process_dataset()
    cache.set("titanic_result", json.dumps(result))

    end = time.time()

    return jsonify({
        "method": "with redis cache",
        "dataset": "Titanic",
        "cache": "miss",
        "data": result,
        "response_time": round(end - start, 3)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)