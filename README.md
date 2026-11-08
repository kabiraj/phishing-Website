# phishing-Website

Session 10 Group 4 — COS30049 Assignment 3. React front end, FastAPI back end.

```text
frontend/   React app
backend/    FastAPI, model, predict.py
```
# Backend Contribution and Defence

The backend of this project was developed using **FastAPI** and integrates a trained **Extra Trees machine learning model** to detect potentially malicious URLs. Its main purpose is to receive URLs from the frontend, extract relevant URL features, and classify them into different categories, including benign, phishing, malware, and defacement.

## Backend Structure

The backend is organised into three main folders:

- **app/** – Contains the FastAPI application, API endpoints, and model integrity verification.
- **models/** – Stores the trained Extra Trees machine learning model used for URL classification.
- **src/** – Contains the machine learning scripts for feature extraction, preprocessing, training, evaluation, clustering, and prediction.

## Implementation and Security

Several security and reliability measures were implemented in the backend:

1. **URL validation:** Only HTTP and HTTPS URLs are accepted. Invalid URLs and URLs containing embedded usernames or passwords are rejected.
2. **Model integrity verification:** The SHA-256 hash of the trained model is checked before it is loaded to help detect unauthorised changes.
3. **Request size limit:** Incoming requests are restricted to a maximum size of 10 KB.
4. **Concurrency control:** The API limits simultaneous prediction requests to prevent excessive resource usage.
5. **CORS configuration:** Cross-origin requests are restricted to the local frontend development origin.
6. **Error handling:** Invalid requests and unexpected errors are handled through appropriate API responses.

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Checks whether the backend is running and the model is loaded. |
| `/predict` | POST | Accepts a URL and returns its predicted category, probability scores, and trust score. |
| `/docs` | GET | Provides interactive API documentation through Swagger UI. |

## Testing and Validation

The backend was tested locally to verify that the application starts successfully, the trained model loads correctly, and the API endpoints respond as expected.

The health endpoint returned a healthy status with the model loaded. The prediction endpoint was also tested using sample URLs and successfully returned classification results and probability scores. Invalid URL inputs were tested and rejected by the API.

## Defence and Justification

FastAPI was selected because it provides a lightweight and efficient framework for building REST APIs and supports request validation through Pydantic. The trained Extra Trees model was integrated so that predictions can be made using the features extracted from submitted URLs.

Security measures such as URL validation, model integrity checking, request size restrictions, concurrency control, and restricted CORS were included to improve the reliability and security of the application.

The backend separates API functionality from machine learning functionality, making the project easier to maintain, test, and extend. Although the model provides automated predictions, its results are not guaranteed to be correct and should be treated as an indication of potential risk rather than definitive proof that a URL is malicious.
