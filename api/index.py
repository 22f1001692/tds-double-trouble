from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import statistics

app = FastAPI()

# ✅ Step 1: Enable CORS for POST from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

# ✅ Step 2: Paste your JSON data here as a Python list
# Open q-vercel-latency.json and replace the [...] below with its full contents
LATENCY_DATA = [
    # PASTE THE CONTENTS OF q-vercel-latency.json HERE
    # It should look like:
    # {"region": "apac", "latency_ms": 123, "uptime": 0.99},
    # {"region": "emea", "latency_ms": 145, "uptime": 0.98},
    # ... etc
]

# ✅ Step 3: Define what the incoming request looks like
class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: float

# ✅ Step 4: The POST endpoint
@app.post("/analytics")
def get_analytics(req: AnalyticsRequest):
    result = {}

    for region in req.regions:
        # Filter records that belong to this region
        records = [r for r in LATENCY_DATA if r["region"] == region]

        if not records:
            result[region] = {"error": "no data found"}
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes   = [r["uptime"] for r in records]

        # Sort for percentile calculation
        latencies_sorted = sorted(latencies)
        n = len(latencies_sorted)
        p95_index = int(0.95 * n)  # 95th percentile position
        if p95_index >= n:
            p95_index = n - 1

        result[region] = {
            "avg_latency": round(statistics.mean(latencies), 2),
            "p95_latency": round(latencies_sorted[p95_index], 2),
            "avg_uptime":  round(statistics.mean(uptimes), 4),
            "breaches":    sum(1 for l in latencies if l > req.threshold_ms),
        }

    return result
