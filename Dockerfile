FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install poppler for pdf2image
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY main.py .
COPY prompt.txt .

RUN chgrp -R 0 /app && \
    chmod -R g=u /app
USER 1000
