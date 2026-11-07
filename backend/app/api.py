
import asyncio
import math
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

import joblib
from app.model_integrity import verify_model_integrity
import pandas as pd
from fastapi import FastAPI, Body, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.concurrency import run_in_threadpool
from starlette.exceptions import HTTPException as StarletteHTTPException


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "extra_trees.joblib"

MAX_REQUEST_SIZE = 10 * 1024
MAX_PREDICTIONS = 2


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(min_length=1, max_length=2048)

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("URL cannot be empty")

        try:
            parsed = urlsplit(value)

            if parsed.scheme.lower() not in ("http", "https"):
                raise ValueError("Only HTTP and HTTPS URLs are accepted")

            if not parsed.hostname:
                raise ValueError("URL must contain a hostname")

            if parsed.username or parsed.password:
                raise ValueError("URLs containing credentials are not accepted")

            if parsed.port is not None and not (
                1 <= parsed.port <= 65535
            ):
                raise ValueError("Invalid port number")

        except ValueError as exc:
            raise ValueError(str(exc)) from exc

        return value


class PredictionResponse(BaseModel):
    url: str
    prediction: str
    probabilities: dict[str, float]
    trust_score: float
    decision_source: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")

    verify_model_integrity(MODEL_PATH)
    artifact = joblib.load(MODEL_PATH)

    if not isinstance(artifact, dict):
        raise RuntimeError("Invalid model artifact format")

    if "model" not in artifact or "features" not in artifact:
        raise RuntimeError("Model artifact is missing required keys")

    model = artifact["model"]
    feature_columns = artifact["features"]

    if not hasattr(model, "predict_proba"):
        raise RuntimeError("Model does not support predict_proba")

    if not feature_columns:
        raise RuntimeError("Model feature list is empty")

    app.state.model = model
    app.state.feature_columns = feature_columns
    app.state.active_predictions = 0
    app.state.max_predictions = MAX_PREDICTIONS
    app.state.prediction_lock = asyncio.Lock()

    print("Model loaded successfully.")
    print(f"Model features: {len(feature_columns)}")

    yield


app = FastAPI(
    title="Phishing URL Detection API",
    description=(
        "Predicts URL categories using the trained machine-learning "
        "model. All URLs are classified by the model without "
        "hostname-specific prediction overrides."
    ),
    version="1.3.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class RequestSizeLimitMiddleware:
    def __init__(self, app, max_size: int):
        self.app = app
        self.max_size = max_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_length = None

        for name, value in scope.get("headers", []):
            if name.lower() == b"content-length":
                try:
                    content_length = int(value)
                except ValueError:
                    response = JSONResponse(
                        status_code=400,
                        content={
                            "detail": {
                                "code": "INVALID_CONTENT_LENGTH",
                                "message": "Invalid Content-Length header.",
                            }
                        },
                    )
                    await response(scope, receive, send)
                    return

        if content_length is not None and content_length > self.max_size:
            response = JSONResponse(
                status_code=413,
                content={
                    "detail": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": "Request body exceeds 10 KB.",
                    }
                },
            )
            await response(scope, receive, send)
            return

        body = bytearray()
        more_body = True

        while more_body:
            message = await receive()

            if message["type"] == "http.disconnect":
                return

            body.extend(message.get("body", b""))

            if len(body) > self.max_size:
                response = JSONResponse(
                    status_code=413,
                    content={
                        "detail": {
                            "code": "REQUEST_TOO_LARGE",
                            "message": "Request body exceeds 10 KB.",
                        }
                    },
                )
                await response(scope, receive, send)
                return

            more_body = message.get("more_body", False)

        received = False

        async def receive_body():
            nonlocal received

            if not received:
                received = True
                return {
                    "type": "http.request",
                    "body": bytes(body),
                    "more_body": False,
                }

            return {"type": "http.disconnect"}

        await self.app(scope, receive_body, send)


app.add_middleware(
    RequestSizeLimitMiddleware,
    max_size=MAX_REQUEST_SIZE,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": {
                "code": "INVALID_REQUEST",
                "message": "The request contains invalid input.",
            }
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail),
            }
        },
        headers=exc.headers,
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    print(f"Prediction API error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "code": "INTERNAL_ERROR",
                "message": "An internal prediction error occurred.",
            }
        },
    )


@app.get("/health")
async def health(request: Request):
    return {
        "status": "healthy",
        "model_loaded": hasattr(request.app.state, "model"),
    }


def make_prediction(url: str, model, feature_columns):
    from src.features import extract_features

    features = extract_features(url)

    input_data = pd.DataFrame(
        [features],
        columns=feature_columns,
    )

    values = model.predict_proba(input_data)[0]
    labels = model.classes_

    probabilities = {
        str(label): float(probability)
        for label, probability in zip(labels, values)
    }

    if not all(
        math.isfinite(probability)
        and 0.0 <= probability <= 1.0
        for probability in probabilities.values()
    ):
        raise ValueError("Model returned invalid probabilities")

    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-5):
        raise ValueError("Model probabilities do not sum to 1")

    prediction = str(labels[int(values.argmax())])

    # This is the model's benign-class probability, not a guarantee
    # that the website is safe.
    trust_score = round(
        probabilities.get("benign", 0.0) * 100,
        2,
    )

    return {
        "url": url,
        "prediction": prediction,
        "probabilities": probabilities,
        "trust_score": trust_score,
        "decision_source": "machine_learning",
    }


@app.post(
    "/predict",
    response_model=PredictionResponse,
    responses={
        400: {"description": "Invalid request size header."},
        413: {"description": "Request body exceeds 10 KB."},
        422: {"description": "Invalid URL input."},
        500: {"description": "Internal prediction error."},
        503: {"description": "Prediction capacity is full."},
    },
)
async def predict(
    request: Request,
    payload: PredictionRequest = Body(...),
):
    async with request.app.state.prediction_lock:
        if (
            request.app.state.active_predictions
            >= request.app.state.max_predictions
        ):
            return JSONResponse(
                status_code=503,
                content={
                    "detail": {
                        "code": "CAPACITY_FULL",
                        "message": "Prediction capacity is full. Try again shortly.",
                    }
                },
            )

        request.app.state.active_predictions += 1

    try:
        result = await run_in_threadpool(
            make_prediction,
            payload.url,
            request.app.state.model,
            request.app.state.feature_columns,
        )

        return result

    finally:
        async with request.app.state.prediction_lock:
            request.app.state.active_predictions -= 1
