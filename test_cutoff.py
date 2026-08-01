import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.schemas import SimulationRequest
from app.simulator import BMSSimulator

def test_cutoff_scenario():
    # Small 2.4kWh battery with heavy 1500W load and NO solar
    req = SimulationRequest(
        voltage=24.0,
        capacity_ah=100.0, # 2.4 kWh total, 1.92 kWh usable (80% DoD)
        load_watts=1500.0, # Heavy load
        solar_peak_kw=0.0, # No solar
        max_dod_percent=80.0,
        inverter_efficiency=90.0,
        usage_hours=10
    )
    res = BMSSimulator.run(req)
    print("=== Cutoff Scenario Results ===")
    print(f"Total Capacity: {res.total_capacity_kwh} kWh")
    print(f"Usable Capacity: {res.usable_capacity_kwh} kWh")
    print(f"Autonomy Hours: {res.autonomy_hours} hrs")
    print(f"Total Delivered Load: {res.total_load_delivered_kwh} kWh")
    print(f"Unmet Demand: {res.unmet_demand_kwh} kWh")
    for step in res.timeline:
        print(f"Hour {step.hour:2d} ({step.time_label}): SoC={step.soc_percent:5.1f}%, Delivered={step.energy_used_kwh:5.2f} kWh, Status={step.status}")

if __name__ == "__main__":
    test_cutoff_scenario()
