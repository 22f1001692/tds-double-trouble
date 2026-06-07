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
    {
    "region": "apac",
    "service": "analytics",
    "latency_ms": 133.81,
    "uptime_pct": 99.029,
    "timestamp": 20250301
  },
  {
    "region": "apac",
    "service": "catalog",
    "latency_ms": 130.95,
    "uptime_pct": 97.339,
    "timestamp": 20250302
  },
  {
    "region": "apac",
    "service": "recommendations",
    "latency_ms": 222,
    "uptime_pct": 97.398,
    "timestamp": 20250303
  },
  {
    "region": "apac",
    "service": "analytics",
    "latency_ms": 111.8,
    "uptime_pct": 98.805,
    "timestamp": 20250304
  },
  {
    "region": "apac",
    "service": "catalog",
    "latency_ms": 173.13,
    "uptime_pct": 97.515,
    "timestamp": 20250305
  },
  {
    "region": "apac",
    "service": "support",
    "latency_ms": 112.27,
    "uptime_pct": 97.165,
    "timestamp": 20250306
  },
  {
    "region": "apac",
    "service": "support",
    "latency_ms": 218.79,
    "uptime_pct": 97.242,
    "timestamp": 20250307
  },
  {
    "region": "apac",
    "service": "recommendations",
    "latency_ms": 184.86,
    "uptime_pct": 99.341,
    "timestamp": 20250308
  },
  {
    "region": "apac",
    "service": "analytics",
    "latency_ms": 225.27,
    "uptime_pct": 98.305,
    "timestamp": 20250309
  },
  {
    "region": "apac",
    "service": "support",
    "latency_ms": 159.78,
    "uptime_pct": 98.065,
    "timestamp": 20250310
  },
  {
    "region": "apac",
    "service": "catalog",
    "latency_ms": 148.3,
    "uptime_pct": 98.746,
    "timestamp": 20250311
  },
  {
    "region": "apac",
    "service": "recommendations",
    "latency_ms": 168.48,
    "uptime_pct": 97.5,
    "timestamp": 20250312
  },
  {
    "region": "emea",
    "service": "analytics",
    "latency_ms": 156.04,
    "uptime_pct": 98.49,
    "timestamp": 20250301
  },
  {
    "region": "emea",
    "service": "catalog",
    "latency_ms": 172.34,
    "uptime_pct": 97.95,
    "timestamp": 20250302
  },
  {
    "region": "emea",
    "service": "support",
    "latency_ms": 149.97,
    "uptime_pct": 97.623,
    "timestamp": 20250303
  },
  {
    "region": "emea",
    "service": "checkout",
    "latency_ms": 231.5,
    "uptime_pct": 98.234,
    "timestamp": 20250304
  },
  {
    "region": "emea",
    "service": "checkout",
    "latency_ms": 125.02,
    "uptime_pct": 98.889,
    "timestamp": 20250305
  },
  {
    "region": "emea",
    "service": "support",
    "latency_ms": 168.24,
    "uptime_pct": 98.947,
    "timestamp": 20250306
  },
  {
    "region": "emea",
    "service": "catalog",
    "latency_ms": 134.54,
    "uptime_pct": 97.654,
    "timestamp": 20250307
  },
  {
    "region": "emea",
    "service": "support",
    "latency_ms": 119.42,
    "uptime_pct": 99.473,
    "timestamp": 20250308
  },
  {
    "region": "emea",
    "service": "recommendations",
    "latency_ms": 104.4,
    "uptime_pct": 99.327,
    "timestamp": 20250309
  },
  {
    "region": "emea",
    "service": "recommendations",
    "latency_ms": 170.91,
    "uptime_pct": 99.032,
    "timestamp": 20250310
  },
  {
    "region": "emea",
    "service": "recommendations",
    "latency_ms": 195.08,
    "uptime_pct": 99.404,
    "timestamp": 20250311
  },
  {
    "region": "emea",
    "service": "checkout",
    "latency_ms": 204.61,
    "uptime_pct": 97.691,
    "timestamp": 20250312
  },
  {
    "region": "amer",
    "service": "support",
    "latency_ms": 124.14,
    "uptime_pct": 98.917,
    "timestamp": 20250301
  },
  {
    "region": "amer",
    "service": "catalog",
    "latency_ms": 175.04,
    "uptime_pct": 99.446,
    "timestamp": 20250302
  },
  {
    "region": "amer",
    "service": "analytics",
    "latency_ms": 227.56,
    "uptime_pct": 99.214,
    "timestamp": 20250303
  },
  {
    "region": "amer",
    "service": "analytics",
    "latency_ms": 157.32,
    "uptime_pct": 97.515,
    "timestamp": 20250304
  },
  {
    "region": "amer",
    "service": "catalog",
    "latency_ms": 168.25,
    "uptime_pct": 97.682,
    "timestamp": 20250305
  },
  {
    "region": "amer",
    "service": "support",
    "latency_ms": 171.84,
    "uptime_pct": 98.08,
    "timestamp": 20250306
  },
  {
    "region": "amer",
    "service": "catalog",
    "latency_ms": 129.32,
    "uptime_pct": 98.963,
    "timestamp": 20250307
  },
  {
    "region": "amer",
    "service": "payments",
    "latency_ms": 133.06,
    "uptime_pct": 97.561,
    "timestamp": 20250308
  },
  {
    "region": "amer",
    "service": "catalog",
    "latency_ms": 196.24,
    "uptime_pct": 99.254,
    "timestamp": 20250309
  },
  {
    "region": "amer",
    "service": "support",
    "latency_ms": 169.94,
    "uptime_pct": 99.377,
    "timestamp": 20250310
  },
  {
    "region": "amer",
    "service": "checkout",
    "latency_ms": 179.83,
    "uptime_pct": 98.232,
    "timestamp": 20250311
  },
  {
    "region": "amer",
    "service": "analytics",
    "latency_ms": 211.46,
    "uptime_pct": 98.216,
    "timestamp": 20250312
  }
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
