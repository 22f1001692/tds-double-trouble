import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# 1. Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],  # <--- Changed this from ["POST"] to ["*"]
    allow_headers=["*"],
)

# 2. Define the expected request body
class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/")
@app.post("")
async def get_metrics(payload: QueryPayload):
    # Locate the bundled telemetry file (checks root and api/ folders)
    base_dir = os.path.dirname(os.path.dirname(__file__))
    search_paths = [
        os.path.join(base_dir, "telemetry.csv"),
        os.path.join(base_dir, "telemetry.json"),
        os.path.join(os.path.dirname(__file__), "telemetry.csv"),
        os.path.join(os.path.dirname(__file__), "telemetry.json")
    ]
    
    df = None
    for path in search_paths:
        if os.path.exists(path):
            if path.endswith('.csv'):
                df = pd.read_csv(path)
            else:
                df = pd.read_json(path)
            break
            
    if df is None:
        return {"error": "Telemetry file not found on server."}

    # Standardize column names to lowercase to avoid matching errors
    df.columns = [c.lower() for c in df.columns]
    
    results = []
    
    # 3. Calculate metrics per region
    for region in payload.regions:
        # Filter data for the specific region
        region_df = df[df['region'].str.lower() == region.lower()]
        
        if len(region_df) == 0:
            continue
            
        avg_latency = float(region_df['latency'].mean())
        p95_latency = float(region_df['latency'].quantile(0.95))
        avg_uptime = float(region_df['uptime'].mean())
        breaches = int((region_df['latency'] > payload.threshold_ms).sum())
        
        results.append({
            "region": region,
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        })
        
    return results
