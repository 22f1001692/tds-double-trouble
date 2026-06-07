import os
import json
import pandas as pd
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS explicitly for all origins and methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

# Load the telemetry data once at startup
with open("q-vercel-latency.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

@app.api_route("/", methods=["POST", "OPTIONS"])
async def handle_request(request: Request, payload: QueryPayload = None):
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return Response(status_code=200)
    
    # Process POST request
    try:
        results = []
        for region in payload.regions:
            region_df = df[df['region'] == region]
            if region_df.empty:
                continue
            
            results.append({
                "region": region,
                "avg_latency": float(region_df['latency_ms'].mean()),
                "p95_latency": float(region_df['latency_ms'].quantile(0.95)),
                "avg_uptime": float(region_df['uptime_pct'].mean()),
                "breaches": int((region_df['latency_ms'] > payload.threshold_ms).sum())
            })
        return results
    except Exception as e:
        return {"error": str(e)}
