import json
import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.options("/")
@app.options("/api/latency")
async def preflight():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/")
@app.post("/api/latency")
async def analyze(payload: QueryPayload):
    out = {}
    for region in payload.regions:
        r = df[df["region"].str.lower() == region.lower()]
        if r.empty:
            continue
        out[region.lower()] = {
            "avg_latency": round(float(r["latency_ms"].mean()), 4),
            "p95_latency": round(float(np.percentile(r["latency_ms"], 95)), 4),
            "avg_uptime":  round(float(r["uptime_pct"].mean()), 4),
            "breaches":    int((r["latency_ms"] > payload.threshold_ms).sum()),
        }
    return {"regions": out}
