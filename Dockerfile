# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py /app/

# non-root user
RUN useradd -ms /bin/bash appuser
USER appuser

EXPOSE 3000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]
