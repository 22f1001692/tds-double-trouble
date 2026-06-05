import json
import statistics
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load data into memory once when the function starts
with open('q-vercel-latency.json', 'r') as f:
    telemetry_data = json.load(f)

class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

@app.post("/analytics")
async def get_analytics(req: AnalyticsRequest):
    results = {}
    
    for region in req.regions:
        # Filter data for the requested region
        region_data = [item for item in telemetry_data if item['region'] == region]
        
        if not region_data:
            results[region] = "No data found"
            continue
            
        latencies = [d['latency_ms'] for d in region_data]
        uptimes = [d['uptime_pct'] for d in region_data]
        
        # Calculations
        avg_latency = statistics.mean(latencies)
        avg_uptime = statistics.mean(uptimes)
        
        # P95 Calculation
        sorted_latencies = sorted(latencies)
        p95_idx = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[p95_idx]
        
        # Count breaches
        breaches = sum(1 for l in latencies if l > req.threshold_ms)
        
        results[region] = {
            "avg_latency": round(avg_latency, 2),
            "p95_latency": round(p95_latency, 2),
            "avg_uptime": round(avg_uptime, 2),
            "breaches": breaches
        }
        
    return results
