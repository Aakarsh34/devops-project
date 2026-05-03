from flask import Flask, Response, jsonify, render_template_string
import datetime
import os
import socket
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest


app = Flask(__name__)
REQUEST_COUNT = Counter("app_requests_total", "Total number of HTTP requests")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DevOps Demo App</title>
    <style>
        body {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
            background-image: radial-gradient(circle at top right, #1e293b, #0f172a);
        }
        .container {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 600px;
            width: 90%;
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        h1 {
            background: linear-gradient(to right, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: 0;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .status-badge {
            display: inline-flex;
            align-items: center;
            background: rgba(5, 150, 105, 0.2);
            color: #34d399;
            padding: 0.5rem 1.2rem;
            border-radius: 9999px;
            font-weight: 600;
            font-size: 0.875rem;
            margin-bottom: 2.5rem;
            border: 1px solid rgba(5, 150, 105, 0.3);
        }
        .pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: #10b981;
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 8px #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        .info-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 1.2rem;
            text-align: left;
        }
        .info-card {
            background: rgba(15, 23, 42, 0.6);
            padding: 1.2rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            transition: transform 0.2s;
        }
        .info-card:hover {
            transform: translateY(-2px);
            background: rgba(15, 23, 42, 0.8);
        }
        .info-label {
            color: #94a3b8;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.4rem;
        }
        .info-value {
            font-size: 1.25rem;
            font-weight: 500;
            font-family: 'Courier New', Courier, monospace;
            color: #f8fafc;
        }
        .highlight {
            color: #fbbf24;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>DevOps Pipeline</h1>
        <div class="status-badge">
            <span class="pulse"></span> SYSTEM ONLINE
        </div>
        
        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">Application Name</div>
                <div class="info-value">{{ application }}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Serving Pod Hostname</div>
                <div class="info-value highlight">{{ hostname }}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Deployment Environment</div>
                <div class="info-value">{{ environment }} ({{ version }})</div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    REQUEST_COUNT.inc()
    return render_template_string(
        HTML_TEMPLATE,
        application=os.getenv("APP_NAME", "generic-app"),
        hostname=socket.gethostname(),
        environment=os.getenv("APP_ENV", "production"),
        version=os.getenv("APP_VERSION", "latest")
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
