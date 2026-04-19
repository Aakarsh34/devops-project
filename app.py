from flask import Flask, Response, jsonify
import datetime
import os
import socket
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


app = Flask(__name__)
REQUEST_COUNT = Counter("app_requests_total", "Total number of HTTP requests")


@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return jsonify(
        {
            "application": os.getenv("APP_NAME", "generic-app"),
            "status": "ok",
            "hostname": socket.gethostname(),
            "environment": os.getenv("APP_ENV", "production"),
            "version": os.getenv("APP_VERSION", "1.0.0"),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }
    )


@app.route("/healthz")
def healthz():
    REQUEST_COUNT.inc()
    return jsonify({"status": "healthy"}), 200


@app.route("/readyz")
def readyz():
    REQUEST_COUNT.inc()
    return jsonify({"status": "ready"}), 200


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
