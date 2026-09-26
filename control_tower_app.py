"""
HADRON Control Tower — standalone dashboard.

Run:
    python control_tower_app.py

It expects the existing HADRON Flask API on http://127.0.0.1:5000.
If the API is unavailable, the dashboard still loads with demo records.
"""

import os
from flask import Flask, jsonify, render_template, request
import requests
from integrations.servicenow.client import ServiceNowClient
from control_tower.intelligence_api import intel_bp

app = Flask(__name__, template_folder="control_tower/templates",
            static_folder="control_tower/static")

app.register_blueprint(intel_bp)

HADRON_API = os.getenv("HADRON_API_URL", "http://127.0.0.1:5000")
TIMEOUT = int(os.getenv("HADRON_API_TIMEOUT", "120"))


def _set_service_now_status(sys_id, status):
    if not sys_id or sys_id.startswith("LOCAL-"):
        return
    try:
        ServiceNowClient().update_record(
            table="x_2216687_optimu_0_pricing_request",
            sys_id=sys_id,
            payload={"intelligence_status": str(status)},
        )
    except Exception as exc:
        print(f"[ControlTower] Could not set ServiceNow status={status}: {exc}")

@app.get("/")
def index():
    return render_template("index.html", api=HADRON_API)


@app.get("/api/requests")
def requests_list():
    try:
        client = ServiceNowClient()
        # Fetch actual records from ServiceNow
        records = client.query(
            table="x_2216687_optimu_0_pricing_request",
            query="ORDERBYDESCsys_created_on",
            limit=20
        )
        
        requests_data = []
        for r in records:
            # Determine display status — intelligence_status is a SN choice field
            # 0=Draft, 1=Analyzing, 2=Intelligence Ready, 3+=Review/Approved/etc.
            sn_status = r.get("intelligence_status", "").strip()
            has_result = bool(r.get("executive_summary", "").strip())
            _status_map = {
                "0": "DRAFT", "1": "ANALYZING", "2": "READY",
                "3": "REVIEW", "4": "NEGOTIATION", "5": "APPROVED", "6": "FAILED",
            }
            if sn_status in _status_map:
                display_status = _status_map[sn_status]
            elif sn_status:
                display_status = sn_status.upper()
            elif has_result:
                display_status = "READY"   # fallback: executive_summary presence
            else:
                display_status = "NEW"

            # Parse stored JSON blobs safely
            def _parse(field):
                raw = r.get(field, "")
                if not raw:
                    return None
                if isinstance(raw, (dict, list)):
                    return raw
                try:
                    import json
                    return json.loads(raw)
                except Exception:
                    return raw  # return as-is (plain string)

            requests_data.append({
                "sys_id": r.get("sys_id", ""),
                "number": r.get("number", ""),
                "customer_name": r.get("customer_name", ""),
                "service_product_name": r.get("service_product_name", ""),
                "status": display_status,
                "commercial_objective": r.get("commercial_objective", ""),
                "additional_context": r.get("additional_context", ""),
                # Persisted HADRON result fields
                "executive_summary": r.get("executive_summary", ""),
                "internal_economics": _parse("internal_economics"),
                "offer_set": _parse("offer_set"),
                "risks": _parse("risks"),
                "confidence": r.get("confidence", ""),
                "customer_intelligence": _parse("customer_intelligence"),
                "service_intelligence": _parse("service_intelligence"),
                "market_intelligence": _parse("market_intelligence"),
                "competitive_intelligence": r.get("competitive_intelligence", ""),
            })

        return jsonify({
            "requests": requests_data,
            "source": "servicenow",
        })
    except Exception as exc:
        return jsonify({
            "error": "ServiceNow API unavailable",
            "detail": str(exc),
            "requests": [],
            "source": "error"
        }), 502

@app.post("/api/requests")
def create_request():
    try:
        payload = request.get_json(force=True)
        client = ServiceNowClient()
        sn_payload = {
            "customer_name": payload.get("customer_name", ""),
            "service_product_name": payload.get("service_product_name", ""),
            "commercial_objective": payload.get("commercial_objective", ""),
            "additional_context": payload.get("additional_context", ""),
            "intelligence_status": "NEW"
        }
        record = client.create_record(
            table="x_2216687_optimu_0_pricing_request",
            payload=sn_payload
        )
        return jsonify({
            "sys_id": record.get("sys_id", ""),
            "number": record.get("number", ""),
            "customer_name": record.get("customer_name", ""),
            "service_product_name": record.get("service_product_name", ""),
            "status": record.get("intelligence_status", "") or "NEW",
            "commercial_objective": record.get("commercial_objective", ""),
            "additional_context": record.get("additional_context", "")
        }), 201
    except Exception as exc:
        return jsonify({"error": "Failed to create ServiceNow request", "detail": str(exc)}), 502


@app.post("/api/requests/<sys_id>/status")
def update_deal_status(sys_id):
    try:
        data = request.get_json(force=True)
        new_status = str(data.get("status", "2"))
        _set_service_now_status(sys_id, new_status)
        return jsonify({"ok": True, "sys_id": sys_id, "status": new_status})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(force=True)
    required = ["customer_name", "service_product_name", "commercial_objective"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    try:
        sys_id = payload.get("record_sys_id", "")
        _set_service_now_status(sys_id, "1")  # Analyzing
        response = requests.post(
            f"{HADRON_API.rstrip('/')}/hadron/analyze",
            json=payload,
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            _set_service_now_status(sys_id, "6")  # Failed
            return (response.content, response.status_code,
                    {"Content-Type": response.headers.get("Content-Type", "application/json")})
        
        # Best-effort ServiceNow writeback; never discard a successful analysis response.
        sys_id = payload.get("record_sys_id", "")
        if sys_id and not sys_id.startswith("LOCAL-"):
            try:
                import json as _json
                data = response.json()
                offers = data.get("offer_set", [])
                if isinstance(offers, str):
                    offers = _json.loads(offers)
                balanced = next(
                    (o for o in offers if "balanced" in o.get("name", "").lower()),
                    offers[0] if offers else None,
                )
                balanced_price = (
                    str(int(round(float(balanced.get("price", 0))))) if balanced else ""
                )
                q_opt = data.get("quantum_optimization") or {}
                q_sol = q_opt.get("quantum_solution") or {}
                c_sol = q_opt.get("classical_solution") or {}

                sn_payload = {
                    "executive_summary": data.get("executive_summary", ""),
                    "internal_economics": data.get("internal_economics", ""),
                    "customer_intelligence": data.get("customer_intelligence", ""),
                    "market_intelligence": data.get("market_intelligence", ""),
                    "service_intelligence": data.get("service_intelligence", ""),
                    "competitive_intelligence": data.get("competitive_intelligence", ""),
                    "offer_set": _json.dumps(data.get("offer_set", [])),
                    "risks": _json.dumps(data.get("risks", [])),
                    "confidence": str(data.get("confidence", "")),
                    "evidence": _json.dumps(data.get("evidence", [])),
                    "intelligence_status": "2",
                    # Legacy field names still used by the ServiceNow form.
                    "recommend_price": balanced_price,
                    "recommended_price": balanced_price,
                    "ai_justification": data.get("executive_summary", ""),
                    "u_ai_justification": data.get("executive_summary", ""),
                }
                if q_sol:
                    sn_payload.update({
                        "quantum_price": str(int(round(float(q_sol.get("price", balanced_price or 0))))),
                        "classical_price": str(int(round(float(c_sol.get("price", balanced_price or 0))))),
                        "expected_margin": str(q_sol.get("expected_margin", "")),
                        "acceptance_probability": str(q_sol.get("win_probability", "")),
                        "ai_value_drivers": f"Pune GDC FTE: {q_sol.get('pune_fte_required', '')}, Staffing: {q_sol.get('staffing_mix', '')}, Terms: {q_sol.get('risk_structure', '')}"
                    })
                ServiceNowClient().update_record(
                    table="x_2216687_optimu_0_pricing_request",
                    sys_id=sys_id,
                    payload=sn_payload,
                )
                print(f"[ControlTower] SN write-back OK → {sys_id}")
            except Exception as sn_exc:
                print(f"[ControlTower] SN write-back failed: {sn_exc}")

        return (response.content, response.status_code,
                {"Content-Type": response.headers.get("Content-Type", "application/json")})
    except requests.RequestException as exc:
        _set_service_now_status(payload.get("record_sys_id", ""), "6")
        return jsonify({
            "error": "HADRON API unavailable",
            "detail": str(exc),
            "hint": "Start the existing app.py on port 5000.",
        }), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)
