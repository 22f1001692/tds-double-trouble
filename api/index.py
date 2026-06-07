# api/index.py
import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization",
}

class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

@app.options("/")
@app.options("/api/latency")
async def preflight():
    return JSONResponse(content={}, headers=CORS_HEADERS)

@app.post("/")
@app.post("/api/latency")
async def analyze(payload: QueryPayload):
    regions_result = {}
    for region in payload.regions:
        rdf = df[df["region"].str.lower() == region.lower()]
        if rdf.empty:
            continue
        regions_result[region.lower()] = {
            "avg_latency": round(float(rdf["latency_ms"].mean()), 4),
            "p95_latency": round(float(np.percentile(rdf["latency_ms"], 95)), 4),
            "avg_uptime":  round(float(rdf["uptime_pct"].mean()), 4),
            "breaches":    int((rdf["latency_ms"] > payload.threshold_ms).sum()),
        }
    return JSONResponse(content={"regions": regions_result}, headers=CORS_HEADERS)
