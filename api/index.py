# api/index.py
import json
import numpy as np
import pandas as pd
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

# Load telemetry — must be at root of repo, same level as vercel.json
with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

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

    return {"regions": regions_result}   # ← wrap in "regions" key
