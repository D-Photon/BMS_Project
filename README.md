# Domestic Solar & Battery Management System (BMS) Simulation Engine

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Mobile](https://img.shields.io/badge/mobile-optimized-brightgreen.svg)

A high-fidelity domestic Battery Management System (BMS) predictive simulation engine and real-time telemetry dashboard. Developed for **Photon Power and Engineering LTD**, this application models battery Depth-of-Discharge (DoD) degradation safeguards, diurnal Solar PV generation curves, inverter conversion losses, and battery backup autonomy for domestic and off-grid renewable installations.

---

## 🌟 Key Features

- **Battery Chemistry & DoD Safeguards**:
  - Chemistry-specific safety profiles: **LiFePO4** (80% default DoD), **Lithium-Ion NMC** (85% DoD), and **Lead-Acid AGM/Gel** (50% DoD).
  - Over-discharge cutoff protection: Prevents deep-discharge cell degradation by enforcing minimum State of Charge ($SoC$) safety thresholds.
  - Inverter conversion efficiency derating ($\eta \approx 90\text{--}95\%$).

- **Selective Solar PV Effect (Night DoD vs. 24h Solar Cycle)**:
  - Toggle switch (`☀️ Solar PV Charging Effect`) to enable or disable daytime solar array generation.
  - When disabled, runs in **Pure Battery DoD Mode** to evaluate nighttime domestic backup duration and autonomy hours.
  - When enabled, models diurnal solar irradiance (sine-wave model peaking at solar noon) with excess solar energy automatically diverted to battery charging.

- **Dual-Engine Architecture (Instant & 100% Offline-Ready)**:
  - **Instant Client-Side Engine**: Built-in JavaScript simulation engine matches backend physics, rendering graphs and telemetry in **0ms** even when offline or opening directly via `file:///`.
  - **FastAPI Cloud Sync**: Non-blocking asynchronous REST API (`/api/v1/simulate`) with automatic fallback handling.
  - Visual engine indicator pill (`⚡ Local Engine Active` / `☁️ Cloud API Synced`).

- **Interactive Dual-Axis Telemetry Chart**:
  - Built with Chart.js with dual-CDN failover (`jsdelivr` + `cdnjs`).
  - Left Y-Axis: Battery State of Charge ($SoC\,\%$) area curve.
  - Right Y-Axis: Energy ($kWh$) for Load Demand and Solar PV Generation.
  - Auto-adapting mobile ticks (`maxTicksLimit: 6`) preventing text overlap on small screens.

- **Mobile-First Responsive Experience**:
  - Full touch-friendly design adhering to Apple HIG & WCAG accessibility guidelines.
  - Safe-area insets (`viewport-fit=cover`) and notch support.
  - iOS auto-zoom prevention (`16px` form control inputs).
  - Swipeable preset carousel (`🌙 Night DoD Mode`, `🔋 5kWh LiFePO4`, `🏡 3.5kWh Cabin`).
  - Horizontal swipe indicator for the telemetry breakdown table.
  - One-click **CSV Telemetry Export**.

---

## 📐 Mathematical & Physics Model

The simulation operates on discrete hourly timesteps ($t = 1, \dots, N$):

1. **System Capacity & Usable Storage**:
   $$\text{Capacity}_{\text{gross}} = \frac{C_{\text{Ah}} \times V}{1000} \quad (\text{kWh})$$
   $$\text{Capacity}_{\text{usable}} = \text{Capacity}_{\text{gross}} \times \text{DoD}_{\text{max}}$$
   $$\text{SoC}_{\text{reserve}} = 100\% - (\text{DoD}_{\text{max}} \times 100\%)$$

2. **Load Demand Accounting for Inverter Losses**:
   $$P_{\text{gross}} = \frac{P_{\text{load}}}{\eta_{\text{inverter}}}$$

3. **Diurnal Solar Irradiance Curve**:
   $$\text{Factor}(t) = \begin{cases} \max\left(0, \sin\left(\frac{(t_{\text{day}} - 6)\pi}{12}\right)\right), & \text{if } 6 \le t_{\text{day}} \le 18 \\ 0, & \text{otherwise} \end{cases}$$
   $$P_{\text{solar}}(t) = P_{\text{peak}} \times \text{Factor}(t) \quad (\text{if Solar PV Enabled})$$

4. **Net Energy Balance & DoD Protection**:
   $$\Delta E = P_{\text{solar}}(t) - P_{\text{gross}}(t)$$
   - **Surplus ($\Delta E \ge 0$)**: Solar supplies 100% of the load; excess energy charges the battery at 95% Coulombic charge efficiency up to 100% $SoC$.
   - **Deficit ($\Delta E < 0$)**: Battery supplies energy down to the minimum safety limit ($SoC_{\text{reserve}}$). If the reserve limit is reached, power delivery is safely truncated to prevent over-discharge, tracking unfulfilled load in $\text{Unmet Demand } (\text{kWh})$.

---

## 📁 Project Directory Structure

```text
bms_engine/
├── app/
│   ├── __init__.py           # Python package marker
│   ├── main.py               # FastAPI application with CORS & /healthz
│   ├── schemas.py            # Pydantic V2 models for requests & telemetry
│   └── simulator.py          # Deterministic BMS physics simulation engine
├── public/                   # Unified Web Assets (Cloudflare Pages build target)
│   ├── index.html            # Mobile-responsive web dashboard with dual engine
│   └── _redirects            # Cloudflare Pages edge proxy rule to Render
├── templates/
│   └── index.html            # Jinja2 template fallback for FastAPI full-stack
├── test_bms.py               # Unit verification test suite
├── test_cutoff.py            # Low-voltage cutoff & DoD safety validation
├── test_pure_dod.py          # Pure nighttime battery discharge test
├── Procfile                  # Render start command
├── render.yaml               # Render Infrastructure-as-Code Blueprint
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.10+ installed
- Web browser (Chrome, Safari, Edge, Firefox)

### 2. Installation
Clone or navigate to the project directory:
```bash
cd bms_engine
pip install -r requirements.txt
```

### 3. Run Locally with Uvicorn
```bash
uvicorn app.main:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

> [!TIP]
> You can also double-click `public/index.html` to run the dashboard directly in your browser without starting Python. The built-in client engine will run the simulation instantly.

### 4. Run Automated Verification Tests
```bash
python test_bms.py
python test_cutoff.py
python test_pure_dod.py
```

---

## 🌐 Production Deployment

### Option A: Render Full-Stack (Easiest)
Deploy both the FastAPI backend and web dashboard as a single service on Render:

1. Push your repository to GitHub or GitLab.
2. Go to [Render Dashboard](https://dashboard.render.com) &rarr; **New +** &rarr; **Web Service**.
3. Connect your repository and configure:
   - **Name**: `domestic-solar-battery-simulator`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/healthz`
4. Click **Create Web Service**.

---

### Option B: Split Architecture (Render API + Cloudflare Pages CDN)
Serve dynamic API endpoints via Render while hosting the frontend across Cloudflare's global edge network:

#### Step 1: Deploy Backend on Render
1. Deploy the service on Render as detailed in Option A.
2. Copy your live Render URL (e.g., `https://domestic-solar-battery-simulator.onrender.com`).

#### Step 2: Configure Cloudflare Pages
1. Open `public/_redirects` and verify the proxy rule:
   ```text
   /api/*  https://domestic-solar-battery-simulator.onrender.com/api/:splat  200!
   ```
2. In the **Cloudflare Dashboard** &rarr; **Workers & Pages** &rarr; **Create application** &rarr; **Pages**.
3. Connect your GitHub repository.
4. Set Build Settings:
   - **Framework preset**: `None`
   - **Build output directory**: `public`
5. Click **Save and Deploy**.

Cloudflare Pages will serve your UI at edge speeds while proxying `/api/*` requests to your Render backend with zero CORS issues.

---

## 📡 REST API Reference

### 1. Health Check
`GET /healthz`
```json
{
  "status": "ok",
  "service": "bms-engine"
}
```

### 2. Run Simulation
`POST /api/v1/simulate`

#### Request Body
```json
{
  "voltage": 48.0,
  "capacity_ah": 200.0,
  "load_watts": 600.0,
  "solar_peak_kw": 1.5,
  "enable_solar": false,
  "battery_type": "lifepo4",
  "max_dod_percent": 80.0,
  "inverter_efficiency": 92.0,
  "usage_hours": 24
}
```

#### Response (200 OK)
```json
{
  "system_voltage": 48.0,
  "total_capacity_kwh": 9.6,
  "usable_capacity_kwh": 7.68,
  "autonomy_hours": 11.0,
  "solar_self_sufficiency_percent": 0.0,
  "total_solar_gen_kwh": 0.0,
  "total_load_delivered_kwh": 7.07,
  "unmet_demand_kwh": 7.33,
  "timeline": [
    {
      "hour": 1,
      "time_label": "00:00",
      "soc_percent": 93.2,
      "solar_gen_kwh": 0.0,
      "load_kwh": 0.6,
      "net_power_kw": -0.6,
      "energy_used_kwh": 0.6,
      "remaining_kwh": 8.948,
      "status": "Active Discharging",
      "status_code": "discharging"
    }
  ]
}
```

---

## 🏢 Organization & Support

Developed by **Photon Power and Engineering LTD**  
Specialists in domestic and commercial solar power systems, battery energy storage systems (BESS), and renewable power engineering.

- **Inquiries & Technical Support**: 📞 08137304139  
- **License**: MIT
