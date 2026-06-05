import json
import statistics
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Define the expected input schema
class AnalyticsRequest(BaseModel):
    regions: List[str]
    threshold_ms: float

# Helper to load telemetry data once
def load_data():
    with open('telemetry.json', 'r') as f:
        return json.load(f)

@app.post("/analytics")
async def get_analytics(req: AnalyticsRequest):
    data = load_data()
    results = {}
    
    for region in req.regions:
        # Filter records for the specific region
        region_data = [item for item in data if item.get('region') == region]
        
        if not region_data:
            continue
            
        latencies = [d['latency'] for d in region_data]
        uptimes = [d['uptime'] for d in region_data]
        
        # Calculate stats
        avg_latency = statistics.mean(latencies)
        avg_uptime = statistics.mean(uptimes)
        
        # P95 calculation (Sort data, find index at 95%)
        sorted_latencies = sorted(latencies)
        p95_idx = int(len(sorted_latencies) * 0.95)
        p95_latency = sorted_latencies[p95_idx]
        
        # Count breaches
        breaches = sum(1 for l in latencies if l > req.threshold_ms)
        
        results[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }
        
    return results
