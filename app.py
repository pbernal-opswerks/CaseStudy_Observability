from flask import Flask, request, jsonify
import logging
import time
import random
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger(__name__)

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP Requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds", "Request latency",
    ["endpoint"]
)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    latency = time.time() - request.start_time
    REQUEST_LATENCY.labels(request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, response.status_code).inc()

    log_data = {
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "latency": round(latency, 3),
        "ip": request.remote_addr,
    }
    logger.info(log_data)
    return response

@app.route("/")
def home():
    return jsonify(message="Hello from Flask Observability App")

@app.route("/health")
def health():
    return jsonify(status="ok")

@app.route("/error")
def error():
    if random.choice([True, False]):
        logger.error({"event": "Simulated failure", "path": "/error"})
        return jsonify(error="Simulated failure"), 500
    return jsonify(message="No error this time")

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
