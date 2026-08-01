import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.schemas import SimulationRequest
from app.simulator import BMSSimulator

def test_simulation():
    req = SimulationRequest(
        voltage=48.0,
        capacity_ah=200.0,
        load_watts=600.0,
        solar_peak_kw=1.5,
        max_dod_percent=80.0,
        inverter_efficiency=92.0,
        usage_hours=24
    )
    res = BMSSimulator.run(req)
    print("=== Simulation Results ===")
    print(f"Total Capacity: {res.total_capacity_kwh} kWh")
    print(f"Usable Capacity: {res.usable_capacity_kwh} kWh")
    print(f"Autonomy Hours: {res.autonomy_hours} hrs")
    print(f"Solar Self-Sufficiency: {res.solar_self_sufficiency_percent}%")
    print(f"Total Solar Gen: {res.total_solar_gen_kwh} kWh")
    print(f"Total Delivered Load: {res.total_load_delivered_kwh} kWh")
    print(f"Unmet Demand: {res.unmet_demand_kwh} kWh")
    print(f"Timeline Steps: {len(res.timeline)}")
    print("Step 1 (00:00):", res.timeline[0])
    print("Step 12 (11:00 Peak Solar):", res.timeline[11])
    print("Step 24 (23:00):", res.timeline[-1])

if __name__ == "__main__":
    test_simulation()
