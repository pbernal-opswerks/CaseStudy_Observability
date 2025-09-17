# Flask Observability App

A simple Python Flask app for observability case study.

## Features
- `/` → Returns hello message
- `/health` → Health check
- `/error` → Random error endpoint to simulate failures
- `/metrics` → Prometheus metrics endpoint

## Run locally
```bash
pip install -r requirements.txt
python app.py
```

## Build Docker
```bash
docker build -t <your-dockerhub-username>/flask-observability-app:latest .
docker run -p 3000:3000 <your-dockerhub-username>/flask-observability-app:latest
```
