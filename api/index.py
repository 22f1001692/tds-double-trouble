import json
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.options("/")
@app.options("/api/latency")
async def preflight():
    return {}

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
