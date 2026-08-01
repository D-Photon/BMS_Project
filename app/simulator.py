import math
from typing import List
from app.schemas import SimulationRequest, SimulationResponse, HourlyTelemetry

class BMSSimulator:
    """
    Domestic Solar Battery Management System Engine.
    Simulates hourly PV solar generation, battery charging/discharging,
    inverter conversion efficiency, depth-of-discharge (DoD) reserve limits,
    and accurate load energy delivery accounting.
    """

    @staticmethod
    def _solar_irradiance_factor(hour: int) -> float:
        """
        Diurnal solar curve peaking at solar noon (12:00 / Hour 12 of a 24h cycle).
        Returns a normalized factor between 0.0 and 1.0.
        """
        hour_of_day = (hour - 1) % 24  # 0 to 23
        # Solar generation active between 6:00 AM (Hour 6) and 18:00 PM (Hour 18)
        if 6 <= hour_of_day <= 18:
            # Sine wave model peaking at 12:00
            angle = (hour_of_day - 6) * math.pi / 12.0
            return max(0.0, math.sin(angle))
        return 0.0

    @classmethod
    def run(cls, data: SimulationRequest) -> SimulationResponse:
        max_capacity_wh = data.capacity_ah * data.voltage
        max_capacity_kwh = max_capacity_wh / 1000.0
        
        # Max usable depth of discharge (e.g. 80% DoD means 20% min reserve)
        max_dod = data.max_dod_percent / 100.0
        min_reserve_soc = max(0.0, 100.0 - (max_dod * 100.0))
        usable_capacity_kwh = max_capacity_kwh * max_dod

        inverter_eff = data.inverter_efficiency / 100.0

        current_soc = 100.0  # Start fully charged
        current_energy_wh = max_capacity_wh
        
        timeline: List[HourlyTelemetry] = []
        cumulative_delivered_wh = 0.0
        total_solar_gen_wh = 0.0
        total_requested_load_wh = 0.0

        autonomy_steps = 0
        cutoff_reached = False

        for hour in range(1, data.usage_hours + 1):
            hour_of_day = (hour - 1) % 24
            time_label = f"{hour_of_day:02d}:00"

            # Solar PV generation in Wh for this hour
            if data.enable_solar:
                solar_factor = cls._solar_irradiance_factor(hour)
                hourly_solar_wh = data.solar_peak_kw * 1000.0 * solar_factor
            else:
                hourly_solar_wh = 0.0
            total_solar_gen_wh += hourly_solar_wh

            # Hourly load requirement in Wh (accounting for inverter losses)
            hourly_load_gross_wh = (data.load_watts * 1.0) / inverter_eff
            total_requested_load_wh += data.load_watts * 1.0

            # Net energy balance for the hour
            # Net > 0: Excess solar energy available for charging
            # Net < 0: Load exceeds solar; battery must discharge to cover deficit
            net_wh = hourly_solar_wh - hourly_load_gross_wh

            delivered_load_wh = 0.0
            status = "Active"
            status_code = "discharging"

            if net_wh >= 0:
                # Solar covers 100% of load + excess charges battery
                delivered_load_wh = data.load_watts * 1.0
                charge_energy = net_wh * 0.95  # 95% charging efficiency
                current_energy_wh = min(max_capacity_wh, current_energy_wh + charge_energy)
                current_soc = (current_energy_wh / max_capacity_wh) * 100.0
                
                if current_soc >= 99.9:
                    status = "Full (Solar Float)"
                    status_code = "charging"
                else:
                    status = f"Charging (+{round(charge_energy/1000.0, 2)} kW solar)"
                    status_code = "charging"
                
                if not cutoff_reached:
                    autonomy_steps += 1

            else:
                # Deficit must come from battery
                deficit_wh = abs(net_wh)
                
                # Solar portion directly delivered to load
                solar_to_load_wh = hourly_solar_wh * inverter_eff
                
                # Available battery energy above safety DoD reserve limit
                min_reserve_wh = max_capacity_wh * (min_reserve_soc / 100.0)
                available_battery_wh = max(0.0, current_energy_wh - min_reserve_wh)

                if available_battery_wh >= deficit_wh:
                    # Battery has sufficient energy to cover full deficit
                    current_energy_wh -= deficit_wh
                    current_soc = (current_energy_wh / max_capacity_wh) * 100.0
                    delivered_load_wh = data.load_watts * 1.0
                    
                    if current_soc <= min_reserve_soc + 5.0:
                        status = "Warning: Low SoC Reserve!"
                        status_code = "warning"
                    else:
                        status = "Active Discharging"
                        status_code = "discharging"
                        
                    if not cutoff_reached:
                        autonomy_steps += 1
                else:
                    # Battery is partially or fully depleted!
                    cutoff_reached = True
                    battery_supplied_wh = available_battery_wh
                    current_energy_wh = min_reserve_wh
                    current_soc = min_reserve_soc
                    
                    # Total delivered load = solar direct + whatever remaining battery could supply
                    delivered_load_wh = solar_to_load_wh + (battery_supplied_wh * inverter_eff)
                    
                    if delivered_load_wh > 0.1:
                        status = f"Partial Power ({round(delivered_load_wh, 0)}W delivered)"
                        status_code = "warning"
                    else:
                        status = "Inactive: Battery Cutoff!"
                        status_code = "cutoff"

            cumulative_delivered_wh += delivered_load_wh
            remaining_kwh = (current_soc / 100.0) * max_capacity_kwh
            net_power_kw = (hourly_solar_wh - (data.load_watts * 1.0)) / 1000.0

            timeline.append(
                HourlyTelemetry(
                    hour=hour,
                    time_label=time_label,
                    soc_percent=round(current_soc, 1),
                    solar_gen_kwh=round(hourly_solar_wh / 1000.0, 3),
                    load_kwh=round(data.load_watts / 1000.0, 3),
                    net_power_kw=round(net_power_kw, 3),
                    energy_used_kwh=round(cumulative_delivered_wh / 1000.0, 3),
                    remaining_kwh=round(remaining_kwh, 3),
                    status=status,
                    status_code=status_code
                )
            )

        total_load_delivered_kwh = cumulative_delivered_wh / 1000.0
        total_requested_kwh = total_requested_load_wh / 1000.0
        unmet_demand_kwh = max(0.0, total_requested_kwh - total_load_delivered_kwh)
        
        solar_gen_kwh = total_solar_gen_wh / 1000.0
        solar_sufficiency = (min(solar_gen_kwh, total_load_delivered_kwh) / max(0.001, total_load_delivered_kwh)) * 100.0
        solar_sufficiency = min(100.0, solar_sufficiency)

        return SimulationResponse(
            system_voltage=data.voltage,
            total_capacity_kwh=round(max_capacity_kwh, 2),
            usable_capacity_kwh=round(usable_capacity_kwh, 2),
            autonomy_hours=autonomy_steps,
            solar_self_sufficiency_percent=round(solar_sufficiency, 1),
            total_solar_gen_kwh=round(solar_gen_kwh, 2),
            total_load_delivered_kwh=round(total_load_delivered_kwh, 2),
            unmet_demand_kwh=round(unmet_demand_kwh, 2),
            timeline=timeline
        )
