# app.py
from flask import Flask, request, jsonify
import logging
import time
import random
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pythonjsonlogger import jsonlogger

app = Flask(__name__)

# JSON structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger("observability-app")
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

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
    latency = time.time() - getattr(request, "start_time", time.time())
    # ensure labels are strings
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    REQUEST_COUNT.labels(request.method, request.path, str(response.status_code)).inc()

    log_data = {
        "method": request.method,
        "path": request.path,
        "status": response.status_code,
        "latency_s": round(latency, 3),
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

# ⚠️ NEW ENDPOINT for readiness check
@app.route("/readiness")
def readiness():
    if readiness_status == "ok":
        return jsonify(status="ok"), 200
    else:
        return jsonify(status="not ready"), 503 # 503 is the standard status code for service unavailable

# ⚠️ NEW ENDPOINT to toggle readiness status
@app.route("/toggle-readiness")
def toggle_readiness():
    global readiness_status
    if readiness_status == "ok":
        readiness_status = "not ready"
        return jsonify(message="Readiness status set to 'not ready'"), 200
    else:
        readiness_status = "ok"
        return jsonify(message="Readiness status set to 'ok'"), 200

@app.route("/badrequest")
def badrequest():
    # simulate a 400
    return jsonify(error="Bad request simulated"), 400

@app.route("/error")
def error():
    # simulate intermittent 5xx errors
    if random.random() < 0.5:
        logger.error({"event": "Simulated failure", "path": "/error"})
        return jsonify(error="Simulated failure"), 500
    return jsonify(message="No error this time")

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
