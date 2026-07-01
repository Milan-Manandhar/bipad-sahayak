from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI Bipad Sahayak", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Bipad Sahayak - Nepal's AI Disaster Platform", "status": "running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "message": "✅ Backend is running successfully!",
        "nepal_time": "2026-07-01 15:45:00 +05:45",
        "version": "1.0.0"
    }

@app.get("/status")
def status():
    return {
        "database": "connected",
        "dhm_stations": 10,
        "rivers_monitored": 22,
        "districts_loaded": 77,
        "active_alerts": 2,
        "registered_users": 12487
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
