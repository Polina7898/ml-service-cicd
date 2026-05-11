import os
import joblib
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

VERSION = os.getenv("APP_VERSION", "v1.1.0")
model = joblib.load("model.joblib")


class PredictRequest(BaseModel):
    x: list[float]


app = FastAPI(title="ml-service", version=VERSION)


@app.get("/health")
def health():
    return {"status": "ok", "version": VERSION}


@app.post("/predict")
def predict(req: PredictRequest):
    pred = int(model.predict(np.array(req.x).reshape(1, -1))[0])
    return {"prediction": pred, "version": VERSION}
