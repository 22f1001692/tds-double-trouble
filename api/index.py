# api/index.py
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics

app = FastAPI()

# Allow any origin, but only need POST. Simpler to allow all methods for small test.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST","OPTIONS","GET"],
    allow_headers=["*"],
)

class Query(BaseModel):
    regions: list[str]
    threshold_ms: float

# Helper to compute p95
def percentile_95(values):
    if not values:
        return None
    sorted_v = sorted(values)
    k = 0.95 * (len(sorted_v) - 1)
    f = int(k)
    c = f + 1
    if c >= len(sorted_v):
        return sorted_v[-1]
    d0 = sorted_v[f] * (c - k)
    d1 = sorted_v[c] * (k - f)
    return d0 + d1

@app.post("/analytics")
async def analytics(query: Query, request: Request):
    body = await request.json()  # not strictly needed because query parsed, but safer if extra fields
    # Expect telemetry bundle in a file you downloaded (q-vercel-latency.json) to be used on server,
    # but here we assume a telemetry variable is included when deployed (we'll load sample on start if present).
    # For the assignment we will read telemetry from a local file bundled in repo.
    import json
    telemetry_path = os.path.join(os.path.dirname(__file__), "..", "q-vercel-latency.json")
    try:
        with open(telemetry_path) as f:
            telemetry = json.load(f)
    except Exception:
        # If file missing, return helpful error
        return {"error": "Telemetry file not found on server. Add q-vercel-latency.json to repo root."}

    result = {}
    for region in query.regions:
        # filter records for region
        recs = [r for r in telemetry if r.get("region") == region]
        latencies = [r.get("latency_ms", 0) for r in recs if "latency_ms" in r]
        uptimes = [r.get("uptime_percent", 0) for r in recs if "uptime_percent" in r]

        avg_latency = statistics.mean(latencies) if latencies else None
        p95_latency = percentile_95(latencies) if latencies else None
        avg_uptime = statistics.mean(uptimes) if uptimes else None
        breaches = sum(1 for v in latencies if v > query.threshold_ms)

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return result
