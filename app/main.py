from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.schemas import SimulationRequest, SimulationResponse
from app.simulator import BMSSimulator

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Domestic Solar BMS Engine",
    description="Optimized deterministic battery management & solar state-of-charge simulation engine.",
    version="2.0.0"
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard(request: Request):
    """Serves the main web dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/v1/simulate", response_model=SimulationResponse)
async def run_simulation(data: SimulationRequest):
    """Calculates battery state-of-charge, solar PV contribution, and energy telemetry."""
    return BMSSimulator.run(data)
