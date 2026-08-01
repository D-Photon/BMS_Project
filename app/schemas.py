from typing import List, Optional
from pydantic import BaseModel, Field

class SimulationRequest(BaseModel):
    voltage: float = Field(default=48.0, gt=0, description="System Voltage in Volts", example=48.0)
    capacity_ah: float = Field(default=200.0, gt=0, description="Battery Capacity in Ah", example=200.0)
    load_watts: float = Field(default=600.0, ge=0, description="Average Load Demand in Watts", example=600.0)
    solar_peak_kw: float = Field(default=1.5, ge=0, description="Peak Solar PV Capacity in kW", example=1.5)
    enable_solar: bool = Field(default=False, description="Enable or disable Solar PV generation charging")
    battery_type: str = Field(default="lifepo4", description="Battery chemistry type (lifepo4, li_ion, lead_acid)")
    inverter_efficiency: float = Field(default=92.0, ge=50.0, le=100.0, description="Inverter efficiency %")
    max_dod_percent: float = Field(default=80.0, ge=10.0, le=100.0, description="Maximum Depth of Discharge %")
    usage_hours: int = Field(default=24, gt=0, le=72, description="Simulation Duration in Hours", example=24)

class HourlyTelemetry(BaseModel):
    hour: int
    time_label: str
    soc_percent: float
    solar_gen_kwh: float
    load_kwh: float
    net_power_kw: float
    energy_used_kwh: float
    remaining_kwh: float
    status: str
    status_code: str  # "charging", "discharging", "warning", "cutoff"

class SimulationResponse(BaseModel):
    system_voltage: float
    total_capacity_kwh: float
    usable_capacity_kwh: float
    autonomy_hours: float
    solar_self_sufficiency_percent: float
    total_solar_gen_kwh: float
    total_load_delivered_kwh: float
    unmet_demand_kwh: float
    timeline: List[HourlyTelemetry]
