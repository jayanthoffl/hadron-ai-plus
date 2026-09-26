<div align="center">

# ⚛️ HADRON AI++
### ServiceNow-Native Commercial Pricing Intelligence & Quantum Decision Cockpit

<p>
  <strong>From opportunity context → deterministic economics → Qiskit QAOA quantum optimization → multi-tier offer strategies → Gemini executive decision synthesis → automated ServiceNow roundtrip writeback.</strong>
</p>

<br/>

<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" /></a>
<a href="https://qiskit.org/"><img src="https://img.shields.io/badge/Quantum-Qiskit%20QAOA-6929C4?style=for-the-badge&logo=qiskit&logoColor=white" /></a>
<a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/API-Flask%20REST-000000?style=for-the-badge&logo=flask&logoColor=white" /></a>
<a href="https://www.servicenow.com/"><img src="https://img.shields.io/badge/Platform-ServiceNow%20PDI-81B5A1?style=for-the-badge&logo=servicenow&logoColor=white" /></a>
<a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/GenAI-Gemini%20Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" /></a>
<a href="https://github.com/"><img src="https://img.shields.io/badge/Deployment-Docker%20%7C%20Render%20%7C%20Railway-2496ED?style=for-the-badge&logo=docker&logoColor=white" /></a>

<br/><br/>

### 🚀 Transforming commercial complexity into mathematically grounded, auditable enterprise decisions.

<br/>

[Executive Summary](#-executive-summary) •
[System Architecture](#-system-architecture) •
[ServiceNow Native Engine](#-servicenow-native-architecture) •
[6-Pillar Intelligence Model](#-the-6-pillar-intelligence-model) •
[PDI Audit & Codebase Reconciliation](#-servicenow-pdi-audit--reconciliation-matrix) •
[Real-World Case Studies](#-live-data--real-deal-telemetry) •
[Live Deployment Guide](#-live-deployment-guide) •
[Local Setup](#-local-setup-instructions) •
[API Reference](#-api-specification) •
[Judge Value Proposition](#-why-hadron-wins)

</div>

---

# 📋 Executive Summary

**HADRON AI++** is an enterprise-grade commercial pricing intelligence system operating in a continuous, bi-directional loop with **ServiceNow**. 

Enterprise pricing for complex transformation contracts typically takes **3 to 4 weeks**, buried across disconnected spreadsheets, sales emails, risk memos, and delivery pod estimates. When generative AI is applied blindly to pricing, it hallucinates numbers, breaches margin floors, and creates unacceptable balance-sheet risk.

HADRON solves this through an unyielding architectural law:

> **Generative AI should interpret commercial intelligence — never manufacture financial truth.**

HADRON separates **deterministic mathematical truth** (GDC rate cards, delivery FTE capacity, Black-Scholes barrier option math, Qiskit QAOA quantum combinatorial state exploration, and competitor dispersion) from **generative synthesis** (Google Gemini multi-model pool for executive narrative synthesis and explainability).

### Core Capabilities:
- **Two-Way ServiceNow Handshake**: Integrated with ServiceNow Flow Designer (`HADRON Commercial Intelligence Orchestration`) and custom Table API endpoints.
- **Quantum Combinatorial Optimization**: Uses Qiskit QAOA quantum circuits parameterized by market volatility, deal urgency, and target margin to explore non-linear price acceptance landscapes.
- **Multi-Key Failover Pool**: Automatic zero-downtime key rotation for Google Gemini (`gemini-3.8-flash` with deterministic algorithmic fallback).
- **Executive 3D Control Tower**: Interactive canvas featuring real-time opportunity orbs, sub-3ms client caching, dual donut telemetry, and audit trail write-back.

---

# 🏛️ System Architecture

HADRON operates as a closed-loop distributed architecture between the **ServiceNow Instance (PDI)** and the **HADRON Computational Engine & Control Tower**.

### End-to-End Orchestration Flow

```mermaid
sequenceDiagram
    autonumber
    actor Exec as 👔 Executive / Sales Rep
    participant CT as 🎛️ HADRON Control Tower (Port 5050)
    participant SN_Table as 🔵 ServiceNow Table (x_..._pricing_request)
    participant SN_Flow as ⚡ ServiceNow Flow Designer
    participant Hadron_API as 🌐 HADRON Intelligence API (Port 5000)
    participant Quantum as ⚛️ Qiskit QAOA Engine
    participant Gemini as ✨ Gemini Agentic Pool

    Note over Exec,SN_Table: Inbound Deal Ingestion
    Exec->>CT: Submit New Deal / Request Analysis
    CT->>SN_Table: POST /api/now/table/x_..._pricing_request (as hadron.integration)
    SN_Table-->>SN_Flow: Trigger: Record Created (CRUD_TRIGGER)

    Note over SN_Flow,Hadron_API: Two-Sided Orchestration Loop
    rect rgb(20, 32, 54)
        SN_Flow->>Hadron_API: Action 1: Run Quantum Pricing (/run_quantum_pricing)
        Hadron_API->>Quantum: Parameterize QAOA Circuit (volatility, urgency, margin)
        Quantum-->>Hadron_API: Optimal Quantum State & Price Multiplier
        Hadron_API-->>SN_Flow: Return quantum_price, classical_price, margins, drivers

        SN_Flow->>Hadron_API: Action 2: Run HADRON Intelligence (/hadron/analyze)
        Hadron_API->>Hadron_API: Execute 6-Pillar Intelligence Pipeline
        Hadron_API->>Gemini: Synthesize Executive Memo & Explainability
        Gemini-->>Hadron_API: Audited Executive Decision Narrative
        Hadron_API-->>SN_Flow: Return Full Intelligence Package (offer_set, risks, evidence)
    end

    Note over SN_Flow,SN_Table: Automated ServiceNow Write-Back
    SN_Flow->>SN_Table: Update Record with Intelligence, Prices & Recommendations
    SN_Table-->>CT: Synchronized Real-Time Event via ServiceNow Table API
    CT->>Exec: Instant 3D Cockpit Telemetry, Dual Donut Gauges & Approval Gate
```

### Architectural Component Diagram

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SERVICENOW PDI PLATFORM                                │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Table: x_2216687_optimu_0_pricing_request (36 Custom Enterprise Fields)        │   │
│   │ • customer_name       • service_product_name    • commercial_objective         │   │
│   │ • recommended_price   • quantum_price           • classical_price              │   │
│   │ • expected_margin     • confidence              • intelligence_status (0-6)    │   │
│   │ • offer_set (JSON)    • risks (JSON)            • executive_summary (Text)     │   │
│   └───────────────────────────────────┬────────────────────────────────────────────┘   │
│                                       │ CRUD Trigger (Record Created)                  │
│                                       ▼                                                │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │ Flow: HADRON Commercial Intelligence Orchestration                             │   │
│   │                                                                                │   │
│   │  ⚡ Action 1: Run Quantum Pricing       ⚡ Action 2: Run HADRON Intelligence   │   │
│   │     (run_quantum_pricing)                   (run_hadron_intelligence)          │   │
│   └───────────────────┬───────────────────────────────────────┬────────────────────┘   │
└───────────────────────┼───────────────────────────────────────┼────────────────────────┘
                        │ HTTPS REST Call                       │ HTTPS REST Call
                        ▼                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                           HADRON COMPUTATIONAL ENGINE (Port 5000)                      │
│                                                                                        │
│   ┌────────────────────────────────────────┐ ┌─────────────────────────────────────┐   │
│   │ POST /run_quantum_pricing              │ │ POST /hadron/analyze                │   │
│   │ • Ingests Financial & Urgency Params   │ │ • Ingests Customer & Service Scope  │   │
│   │ • Random Forest Feature Importance     │ │ • Orchestrates 6-Pillar Agents      │   │
│   │ • Qiskit Aer 3-Qubit Quantum Circuit   │ │ • GDC Blended Rate Cost Engine      │   │
│   │ • Multi-State QAOA State Measurement   │ │ • Multi-Tier Scenario Generation    │   │
│   │ • Gemini AI Explainability Log Stamp   │ │ • Deterministic Fallback Logic      │   │
│   └────────────────────────────────────────┘ └─────────────────────────────────────┘   │
│                         │                                        │                     │
│                         ▼                                        ▼                     │
│             ┌────────────────────────┐              ┌────────────────────────┐         │
│             │ Qiskit QAOA Simulator  │              │ Gemini Multi-Key Pool  │         │
│             │ Quantum State Space    │              │ Failover Model Client  │         │
│             └────────────────────────┘              └────────────────────────┘         │
└───────────────────────────────────┬────────────────────────────────────────────────────┘
                                    │ Live Telemetry & Bi-Directional Sync
                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          HADRON CONTROL TOWER (Port 5050)                              │
│                                                                                        │
│  ✨ 3D Radial Node Graph    🎯 Opportunity Pipeline Orb    📊 Dual Donut Gauges        │
│  🛡️ Verifiable Governance   ⚡ Sub-3ms TTL Caching         📂 Live ServiceNow Writeback │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 🔵 ServiceNow Native Architecture

HADRON is not a loose plugin; it is deeply embedded into ServiceNow’s metadata architecture.

### 1. Integration Machine Identity
- **User Account**: `hadron.integration`
- **sys_id**: `8726ef7483ef8f101fdfc829feaad303`
- **Identity Type**: `machine` (Web Service Access Only — cannot log in to ServiceNow UI)
- **Role**: Purpose-built integration account authenticating via ServiceNow Basic Auth to create and update records.

### 2. Custom Table Specification: `x_2216687_optimu_0_pricing_request`
The table contains **36 specialized fields** capturing the full lifecycle of a pricing deal:

| Field Label | Field Name | Type | Purpose |
| :--- | :--- | :--- | :--- |
| **Number** | `number` | String | Unique auto-generated request ticket (e.g. `PRI0001031`) |
| **Customer Name** | `customer_name` | String | Enterprise client name (e.g. *DHL Courier*, *Google*, *Infosys*) |
| **Service / Product** | `service_product_name` | String | Commercial offering from internal catalog |
| **Commercial Objective** | `commercial_objective` | String | Client's strategic intent (e.g. *Fleet Carrier Quantum Routing*) |
| **Additional Context** | `additional_context` | String | Technical constraints (TPU, ISO 26262, GDC location) |
| **Intelligence Status** | `intelligence_status` | Choice | `0=Draft`, `1=Analyzing`, `2=Ready`, `3=Review`, `4=Negotiation`, `5=Approved`, `6=Failed` |
| **Recommended Price** | `recommended_price` | Currency | Primary AI-recommended commercial offer price |
| **Quantum Price** | `quantum_price` | Currency | Price output from Qiskit QAOA quantum optimizer |
| **Classical Price** | `classical_price` | Currency | Baseline heuristic/cost-plus price |
| **Expected Margin** | `expected_margin` | Decimal | Gross margin % computed by quantum simulation |
| **Acceptance Probability**| `acceptance_probability` | Decimal | Statistical win probability (calibrated against 72 historical deals) |
| **Confidence** | `confidence` | Decimal | Score (0.0 to 1.0) reflecting data completeness and catalog match |
| **AI Value Drivers** | `ai_value_drivers` | String | Top algorithmic drivers selected by Random Forest regressor |
| **Executive Summary** | `executive_summary` | String (Large) | Audited narrative synthesis prepared for C-suite decision makers |
| **Offer Set** | `offer_set` | JSON Blob | 4-Tier structured offers (Entry, Balanced, Strategic, Premium) |
| **Risks** | `risks` | JSON Blob | Array of deterministic risk signals with severity and mitigation |
| **Customer Intelligence**| `customer_intelligence` | JSON Blob | Financials, tier, budget, and capacity pressure |
| **Service Intelligence** | `service_intelligence` | JSON Blob | FTE pod requirements, duration, and complexity index |
| **Market Intelligence** | `market_intelligence` | JSON Blob | Competitor pricing signals and volatility indicators |

### 3. Flow Designer Orchestration
- **Flow**: `HADRON Commercial Intelligence Orchestration`
- **Trigger**: `CRUD_TRIGGER` on Record Created in `x_2216687_optimu_0_pricing_request`.
- **Action 1 (`run_quantum_pricing`)**: Passes 12 economic telemetry parameters to HADRON's quantum solver.
- **Action 2 (`run_hadron_intelligence`)**: Passes context to the multi-agent pipeline and writes back the complete package.
- **UI Policy (`Lock Quantum Telemetry`)**: Protects calculated quantum outputs from unauthorized manual tampering.

---

# 🧠 The 6-Pillar Intelligence Model

```text
               📥 INCOMING REQUEST (Customer, Service, Objective, Context)
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  👤 PILLAR 1:                     🧩 PILLAR 2:                     🌎 PILLAR 3:
CUSTOMER INTELLIGENCE            SERVICE INTELLIGENCE             MARKET INTELLIGENCE
• CRM revenue & FTE match        • Catalog complexity index       • Competitor pricing signals
• Tier 1-3 classification        • FTE pod resource mix           • Market price dispersion
• Capacity pressure score        • Delivery duration months       • Market volatility index
        │                                │                                │
        └────────────────────────────────┼────────────────────────────────┘
                                         ▼
                                  💰 PILLAR 4:
                            INTERNAL ECONOMICS ENGINE
                   • GDC Pune / Blended labor rate cards ($/hr)
                   • Base operating delivery cost calculation
                   • 30.0% Non-negotiable floor margin constraint
                   • 72 Historical deal benchmark calibration
                                         │
                                         ▼
                                  ⚛️ PILLAR 5:
                           QUANTUM QAOA & SCENARIO ENGINE
                   • Classical cost-plus baseline calibration
                   • 3-Qubit quantum state space simulation
                   • 4-Tier Offer Generation:
                     - Entry Offer     (Minimum viable price / 30% margin)
                     - Balanced Offer  (QAOA-calibrated optimal win probability)
                     - Strategic Offer (Value-expanded multi-year transformation)
                     - Premium Offer   (Maximum SLA & high-margin capture)
                                         │
                                         ▼
                                  🛡️ PILLAR 6:
                           DETERMINISTIC RISK ENGINE
                   • Market disconnect ratio (Floor vs. Competitor avg)
                   • Delivery complexity & staffing feasibility
                   • Parametric data-sparse severity penalties
                                         │
                                         ▼
                                  ✨ EXECUTIVE AGENT
                         (Gemini 3.8 Flash + Deterministic Fallback)
                   • Audited Executive Summary with UTC Log Stamp
                   • Evidence Chain & Verifiable Confidence Score
                   • Automated ServiceNow Record Write-Back
```

---

# 📊 ServiceNow PDI Audit & Reconciliation Matrix

A comprehensive audit of our live ServiceNow instance was conducted by a ServiceNow platform agent. Below is the transparent reconciliation between the ServiceNow PDI findings and the local codebase implementation:

| # | PDI Analysis Finding | Severity | Codebase Status & Resolution |
| :--- | :--- | :---: | :--- |
| **1** | **Flow is ACTIVE and working** (10+ successful executions in 48h) | ✅ Good | **Verified 100% Operational**. All recent CRUD triggers executed in 1.0s to 29.6s without errors. |
| **2** | **External integration is live** (`hadron.integration` machine user active) | ✅ Good | **Integrated**. The client supports both `admin` and `hadron.integration` credentials for automated flow triggers. |
| **3** | **AI intelligence populated** (Rich multi-dimensional data on records) | ✅ Good | **Populated**. Full JSON blobs (`offer_set`, `customer_intelligence`, `risks`) stored in ServiceNow table. |
| **4** | **Flow shows status: 'draft' in metadata** (even though active) | ℹ️ Info | **Normal ServiceNow Behavior**. In PDIs, activated flows operate off snapshot runtime versions even if the draft record is open. |
| **5** | **No app menu/modules in ServiceNow left navigation** | 🟡 Gap | **Solved via HADRON Control Tower**. Rather than generic ServiceNow form views, HADRON provides a dedicated C-suite cockpit on port 5050. |
| **6** | **No mandatory fields in table definition** | 🟡 Gap | **Enforced in Code**. Both `app.py` and `control_tower_app.py` validate required commercial inputs before submission. |
| **7** | **`intelligence_status` was NULL in initial records** | 🟡 Resolved | **Fixed in Code**. Added formal state machine (`0=DRAFT`, `1=ANALYZING`, `2=READY`, `3=REVIEW`, `4=NEGOTIATION`, `5=APPROVED`, `6=FAILED`). Control Tower and `app.py` now explicitly persist status `2` (READY) and update on approval. |
| **8** | **`hadron_core_company_read` role orphaned** | 🟡 Info | **Handled Locally**. Customer lookup is performed against enterprise CRM records (`data/customer.json`), eliminating cross-scope dependency issues. |
| **9** | **Fluent workspace empty** (`src/fluent/index.now.ts`) | ℹ️ Info | **By Design**. ServiceNow schema was built via App Engine Studio/Flow Designer; computational intelligence lives in Python. |
| **10**| **`quantum_price` / `classical_price` unmapped in early flows** | 🟡 Resolved | **Fixed in Write-Back**. In `control_tower_app.py`, explicit writeback updates `quantum_price`, `classical_price`, `expected_margin`, `acceptance_probability`, and `ai_value_drivers`. |

---

# 📦 Live Data & Real Deal Telemetry

The following real records in our ServiceNow PDI demonstrate HADRON's intelligence in action:

### Case Study 1: DHL Courier (`PRI0001027`) — High Confidence Enterprise Deal
- **Service**: *Advanced Routing Service for Fleet*
- **Objective**: Implement Quantum Optimization across Fleet Carrier network
- **Confidence**: `1.0` (100%)
- **Recommended Balanced Price**: **$12,821,451**
- **Floor Base Cost**: $11,871,714 (Target Margin: 30.0%)
- **ServiceNow Intelligence Produced**:
  - *Customer Intelligence*: Matched CRM record ($94B revenue, 590K FTE, Tier-1 Global Enterprise, $85M budget).
  - *Service Intelligence*: Matched catalog (78% complexity, 9-month delivery, 15 FTE pod: 2 Architects, 2 Quantum Engineers, 4 AI Engineers, 3 Data Engineers, 1 PM, 1 Lead, 2 QA).
  - *Market Intelligence*: 3 competitor signals captured: Accenture ($7.58M), IBM Quantum ($6.94M), Deloitte ($6.1M).
  - *Offer Set*: 4 tiers generated from **$11.87M (Entry)** to **$15.64M (Premium)**.

### Case Study 2: Google (`PRI0001021` / `PRI0001018`) — Large-Scale AI Transformation
- **Service**: *Enterprise AI Transformation*
- **Confidence**: `0.75` (75%)
- **Offer Range**: **$26.4M (Entry)** → **$37.7M (Premium)**
- **ServiceNow Intelligence Produced**:
  - 82% Catalog complexity, 18-month duration, 25 FTE delivery pod.
  - Market intelligence active ($9.8M–$14.5M competitor range).

### Case Study 3: Infosys (`PRI0001025`) — Low Confidence Data-Sparse Fallback
- **Service**: *Quantum based ERP System Migration*
- **Confidence**: `0.20` (20% — Correctly flagged as data-sparse)
- **Recommended Price**: **$505,080**
- **System Behavior**: Customer not found in CRM, service not in catalog. HADRON automatically dropped confidence, engaged parametric baseline estimation, and flagged 4 critical risk warnings to prevent underquoting.

---

# 🚀 Live Deployment Guide

You can deploy HADRON live connected to ServiceNow via **Cloud PaaS (Railway / Render)** or via **Instant Tunnel (ngrok)**.

```text
┌────────────────────────┐         HTTPS Public URL         ┌────────────────────────┐
│   ServiceNow PDI       ├─────────────────────────────────►│  HADRON Live Engine    │
│   Flow Designer Actions│◄─────────────────────────────────┤  (Render / Railway)    │
└────────────────────────┘         JSON Telemetry           └────────────────────────┘
```

### Option A: 1-Click Cloud Deployment (Railway / Render)

HADRON is container-ready and includes production `Procfile`, `start.sh`, and `requirements.txt`.

1. **Push your repository to GitHub**:
   ```bash
   git push origin main
   ```
2. **Deploy on [Railway.app](https://railway.app) or [Render.com](https://render.com)**:
   - Select **Deploy from GitHub repo**.
   - Set the start command to:
     ```bash
     ./start.sh
     ```
   - Add your Environment Variables in the cloud dashboard:
     ```env
     SERVICENOW_INSTANCE_URL=https://devXXXXXX.service-now.com
     SERVICENOW_USERNAME=admin
     SERVICENOW_PASSWORD=your_password
     GEMINI_API_KEY=your_gemini_api_key
     HADRON_ENV=production
     ```
3. **Copy your Public HTTPS Domain**:
   - Railway/Render gives you a URL like: `https://hadron-production.up.railway.app`
4. **Update ServiceNow Flow Actions**:
   - Open ServiceNow **Flow Designer** → Edit Action `Run Quantum Pricing` → Update REST endpoint URL to:
     ```
     https://hadron-production.up.railway.app/run_quantum_pricing
     ```
   - Edit Action `Run HADRON Intelligence` → Update REST endpoint URL to:
     ```
     https://hadron-production.up.railway.app/hadron/analyze
     ```
   - Click **Save** and **Activate**. Now your ServiceNow instance calls your live cloud deployment 24/7!

---

### Option B: Instant Live Tunneling (ngrok)

If you are demoing live from your development machine:

1. **Start HADRON API**:
   ```bash
   python app.py
   ```
2. **Start ngrok tunnel on port 5000**:
   ```bash
   ngrok http 5000
   ```
3. **Copy the forwarding HTTPS URL** (e.g. `https://xxxx-xx-xx.ngrok-free.app`).
4. **Update ServiceNow Flow Actions** with the ngrok URL:
   - Quantum Action: `https://xxxx-xx-xx.ngrok-free.app/run_quantum_pricing`
   - Intelligence Action: `https://xxxx-xx-xx.ngrok-free.app/hadron/analyze`
5. **Start HADRON Control Tower**:
   ```bash
   python control_tower_app.py
   ```
   Open `http://127.0.0.1:5050` (or run a second ngrok tunnel `ngrok http 5050` to share the executive dashboard with judges!).

---

# 💻 Local Setup Instructions

### Prerequisites
- Python 3.9, 3.10, or 3.11
- A ServiceNow Developer Instance (PDI) with the `x_2216687_optimu_0_pricing_request` table
- Google Gemini API key(s)

### 1. Clone & Environment Setup
```bash
git clone https://github.com/jayanthoffl/hadron-ai-plus.git
cd hadron-ai-plus

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Copy the example file and populate your credentials:
```bash
cp .env.example .env
```
Edit `.env`:
```env
SERVICENOW_INSTANCE_URL=https://devXXXXXX.service-now.com
SERVICENOW_USERNAME=admin
SERVICENOW_PASSWORD=your_instance_password
GEMINI_API_KEY=AIzaSy...
```

### 3. Launch the Stack
You can start both services with a single command:
```bash
./start.sh
```
Or start them in separate terminals:
- **Terminal 1 (AI & Quantum Engine)**:
  ```bash
  python app.py
  # Running on http://127.0.0.1:5000
  ```
- **Terminal 2 (Control Tower Cockpit)**:
  ```bash
  python control_tower_app.py
  # Running on http://127.0.0.1:5050
  ```

Open your browser to **`http://127.0.0.1:5050`**.
- Credentials: User `admin` / Password `gM1T6@iJepI*` (or your ServiceNow credentials).

---

# 🔌 API Specification

### 1. `POST /run_quantum_pricing`
Called by ServiceNow Flow Action `Run Quantum Pricing`.

**Request Body**:
```json
{
  "client_revenue": 94000000000,
  "employee_count": 590000,
  "competitor_price": 7580000,
  "market_volatility": 0.45,
  "target_margin": 0.30,
  "operating_cost": 8310000,
  "hr_budget": 500000,
  "deal_urgency": 8
}
```

**Response Body**:
```json
{
  "classical_price": 10803000.0,
  "quantum_price": 12821451.0,
  "recommended_price": 12821451.0,
  "expected_margin": 0.352,
  "acceptance_probability": 0.92,
  "ai_value_drivers": "Operating Cost, Competitor Price, Target Margin, Deal Urgency",
  "ai_explanation": "[SYS_LOG: 2026-09-26T21:41:00Z] - HADRON OPTIMIZATION LOCK: Classical price $10.8M vs Quantum QAOA price $12.8M...",
  "intelligence_status": "2"
}
```

---

### 2. `POST /hadron/analyze`
Called by ServiceNow Flow Action `Run HADRON Intelligence` or Control Tower.

**Request Body**:
```json
{
  "customer_name": "DHL Courier",
  "service_product_name": "Advanced Routing Service for Fleet",
  "commercial_objective": "Implement Quantum across their Fleet Carrier",
  "additional_context": "Requires on-premise industrial wireless mesh, edge TPU deployment"
}
```

**Response Body**:
```json
{
  "confidence": 1.0,
  "customer_intelligence": {
    "account_tier": "Tier 1 - Global Enterprise",
    "annual_revenue": 94000000000,
    "budget": 85000000,
    "capacity_pressure": 0.92
  },
  "service_intelligence": {
    "complexity": 0.78,
    "duration_months": 9,
    "fte_required": 15
  },
  "internal_economics": {
    "baseline_delivery_cost": 8310000,
    "floor_price": 11871714,
    "target_margin": 0.30
  },
  "offer_set": [
    { "name": "Entry Offer", "price": 11871714, "margin": 0.30 },
    { "name": "Balanced Offer", "price": 12821451, "margin": 0.352 },
    { "name": "Strategic Offer", "price": 14010000, "margin": 0.407 },
    { "name": "Premium Offer", "price": 15640000, "margin": 0.469 }
  ],
  "executive_summary": "Executive Decision Brief: DHL Courier commercial strategy approved..."
}
```

---

### 3. `GET /api/requests`
Used by HADRON Control Tower. Features a 15-second in-memory TTL cache with sub-3ms response times. Returns active deals from ServiceNow table `x_2216687_optimu_0_pricing_request`.

---

# 🏆 Why HADRON Wins

| Assessment Dimension | Traditional Pricing / Standard GenAI | HADRON AI++ |
| :--- | :--- | :--- |
| **Financial Integrity** | LLMs hallucinate prices; risks negative margins. | **Deterministic Math Floor**: 30% margin is mathematically guaranteed before GenAI ever sees the deal. |
| **Optimization Depth** | Static spreadsheets or basic linear regression. | **Qiskit QAOA Quantum Simulation**: Explores non-linear multi-dimensional combinatorial price states. |
| **System of Record** | Disconnected tools (Salesforce, Excel, Slack). | **ServiceNow-Native**: Full roundtrip orchestration with Flow Designer, custom tables, and audit logs. |
| **C-Level Explainability**| Black-box answers ("trust me, it's $5M"). | **Audited Evidence Chain**: Every quote is backed by GDC FTE rate cards, competitor signals, and risk factors. |
| **Production Speed** | 3 to 4 weeks across multi-tier approvals. | **Sub-30 Second Full Roundtrip**: Instantaneous algorithmic intelligence with 1-click ServiceNow write-back. |
| **UI Experience** | Standard form grids and manual data entry. | **Executive 3D Cockpit**: Radial node graph, live opportunity orbs, dual donut telemetry, and instant pre-rendering. |

---

<div align="center">

### ⚛️ HADRON AI++
**Architected for the Google & ServiceNow Enterprise AI Hackathon**

*Built with Qiskit, Google Gemini, ServiceNow Flow Designer, and Flask.*

</div>
