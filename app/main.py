from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import SimulationRequest, SimulationResponse
from app.simulator import BMSSimulator

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Domestic Solar BMS Engine",
    description="Optimized deterministic battery management & solar state-of-charge simulation engine.",
    version="2.0.0"
)

# Enable CORS for cross-origin deployment (Cloudflare Pages + Render API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use public directory for web assets (Unified layout for Render & Cloudflare Pages)
PUBLIC_DIR = BASE_DIR / "public"
if not PUBLIC_DIR.exists():
    PUBLIC_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(PUBLIC_DIR))

@app.get("/healthz")
async def health_check():
    """Health check endpoint for Render service monitoring."""
    return {"status": "ok", "service": "bms-engine"}

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the main web dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/simulate", response_model=SimulationResponse)
async def run_simulation(data: SimulationRequest):
    """Calculates battery state-of-charge, solar PV contribution, and energy telemetry."""
    return BMSSimulator.run(data)
