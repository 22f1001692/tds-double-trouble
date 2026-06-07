import os
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Force global CORS middleware across all incoming routes/methods
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryPayload(BaseModel):
    regions: List[str]
    threshold_ms: float

# A simple GET endpoint to verify the server is running without crashing
@app.get("/")
def health_check():
    return {"status": "healthy", "message": "The server is running perfectly!"}

@app.post("/")
@app.post("")
async def get_metrics(payload: QueryPayload):
    try:
        # We import pandas INSIDE the function to catch compilation/import crashes
        import pandas as pd
        
        # Look for telemetry data file
        base_dir = os.path.dirname(os.path.dirname(__file__))
        search_paths = [
            os.path.join(base_dir, "telemetry.csv"),
            os.path.join(base_dir, "telemetry.json"),
            os.path.join(os.path.dirname(__file__), "telemetry.csv"),
            os.path.join(os.path.dirname(__file__), "telemetry.json")
        ]
        
        path_to_load = None
        for path in search_paths:
            if os.path.exists(path):
                path_to_load = path
                break
                
        if path_to_load is None:
            return {
                "error": "File Not Found", 
                "checked_paths": search_paths,
                "current_directory_contents": os.listdir(base_dir)
            }

        # Read file safely
        if path_to_load.endswith('.csv'):
            df = pd.read_csv(path_to_load)
        else:
            df = pd.read_json(path_to_load)

        # Standardize columns
        df.columns = [c.lower() for c in df.columns]
        
        results = []
        for region in payload.regions:
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

    except Exception as e:
        # If ANY error happens, catch it and send it as a successful JSON response 
        # so it preserves CORS headers and shows you exactly what broke.
        return {
            "error": "Runtime Crash",
            "details": str(e),
            "traceback": traceback.format_exc()
        }
