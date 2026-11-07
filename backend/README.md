# Backend - Phishing URL Detection

## Setup
Run: python -m pip install -r requirements.txt

## Start API
python -m uvicorn app.api:app --host 127.0.0.1 --port 8000

## Endpoints
- GET /health
- POST /predict
- GET /docs

## Security
SHA-256 model verification, URL validation, request size limit, concurrency limit and restricted CORS.
