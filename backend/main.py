from fastapi import FastAPI
from pydantic import BaseModel
from predict import predict

app = FastAPI()


class UrlIn(BaseModel):
    url: str


@app.post("/predict")
def check_url(body: UrlIn):
    return predict(body.url)
