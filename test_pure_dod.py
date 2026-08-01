import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.schemas import SimulationRequest
from app.simulator import BMSSimulator

def test_pure_dod():
    req = SimulationRequest(
        voltage=48.0,
        capacity_ah=200.0, # 9.6 kWh total, 7.68 kWh usable (80% DoD)
        load_watts=600.0,
        solar_peak_kw=1.5,
        enable_solar=False, # PV DISABLED
        max_dod_percent=80.0,
        inverter_efficiency=92.0,
        usage_hours=24
    )
    res = BMSSimulator.run(req)
    print("=== Pure Battery DoD Simulation (Solar Disabled) ===")
    print(f"Total Capacity: {res.total_capacity_kwh} kWh")
    print(f"Usable Capacity: {res.usable_capacity_kwh} kWh")
    print(f"Autonomy Hours: {res.autonomy_hours} hrs")
    print(f"Total Solar Gen: {res.total_solar_gen_kwh} kWh")
    print(f"Total Delivered Load: {res.total_load_delivered_kwh} kWh")
    print(f"Unmet Demand: {res.unmet_demand_kwh} kWh")
    for step in res.timeline[:14]:
        print(f"Hour {step.hour:2d} ({step.time_label}): SoC={step.soc_percent:5.1f}%, Remaining={step.remaining_kwh:5.2f} kWh, Status={step.status}")

if __name__ == "__main__":
    test_pure_dod()
