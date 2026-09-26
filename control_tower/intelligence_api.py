"""
Backend API routes for HADRON Internal Intelligence Data.

These endpoints serve and persist the internal company data that feeds
the pricing engine:
  - Capacity / utilization
  - Department budgets
  - Resource rate card
  - Historical deals (won/lost with prices)
  - Service delivery economics

This replaces static JSON files with live, editable internal truth.
Input still originates from ServiceNow pricing requests.
"""

import json
import os
from pathlib import Path
from flask import Blueprint, request, jsonify

intel_bp = Blueprint("intelligence", __name__)

_DATA_DIR = Path(__file__).parent.parent / "data"

_FILES = {
    "capacity":   _DATA_DIR / "internal_capacity.json",
    "economics":  _DATA_DIR / "economics.json",
    "deals":      _DATA_DIR / "historical_deals.json",
    "rates":      _DATA_DIR / "rate_card.json",
    "services":   _DATA_DIR / "services.json",
    "company":    _DATA_DIR / "company_profile.json",
}

# ── defaults written on first run ──────────────────────────────────────────────

_DEFAULTS = {
    "capacity": {
        "overall_utilization": 0.68,
        "available_billable_capacity": 0.32,
        "quarterly_revenue_target": 12000000,
        "confirmed_pipeline_value": 8400000,
        "headcount": {
            "solution_architects": 12,
            "ai_engineers": 28,
            "data_engineers": 22,
            "project_managers": 8,
            "total_billable": 70
        },
        "upcoming_commitments": [],
        "notes": ""
    },
    "rates": {
        "Solution Architect":    185,
        "AI Engineer":           145,
        "Data Engineer":         125,
        "Project Manager":       110,
        "Business Analyst":       95,
        "QA / Test Engineer":     90,
        "Delivery Lead":         165,
    },
    "deals": []
}

from typing import Union

def _load(key: str) -> Union[dict, list]:
    path = _FILES[key]
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    # write default and return it
    default = _DEFAULTS.get(key, {} if key != "deals" else [])
    _save(key, default)
    return default


def _save(key: str, data):
    path = _FILES[key]
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ── Capacity ───────────────────────────────────────────────────────────────────

@intel_bp.get("/api/intelligence/capacity")
def get_capacity():
    return jsonify(_load("capacity"))


@intel_bp.put("/api/intelligence/capacity")
def save_capacity():
    data = request.get_json(force=True)
    _save("capacity", data)
    return jsonify({"ok": True})


# ── Rate card ──────────────────────────────────────────────────────────────────

@intel_bp.get("/api/intelligence/rates")
def get_rates():
    return jsonify(_load("rates"))


@intel_bp.put("/api/intelligence/rates")
def save_rates():
    data = request.get_json(force=True)
    _save("rates", data)
    return jsonify({"ok": True})


# ── Historical deals ───────────────────────────────────────────────────────────

@intel_bp.get("/api/intelligence/deals")
def get_deals():
    return jsonify(_load("deals"))


@intel_bp.post("/api/intelligence/deals")
def add_deal():
    deal = request.get_json(force=True)
    deals = _load("deals")
    deal["id"] = len(deals) + 1
    deals.append(deal)
    _save("deals", deals)
    return jsonify(deal), 201


@intel_bp.delete("/api/intelligence/deals/<int:deal_id>")
def delete_deal(deal_id):
    deals = [d for d in _load("deals") if d.get("id") != deal_id]
    _save("deals", deals)
    return jsonify({"ok": True})


# ── Service economics ──────────────────────────────────────────────────────────

@intel_bp.get("/api/intelligence/economics")
def get_economics():
    return jsonify(_load("economics"))


@intel_bp.put("/api/intelligence/economics")
def save_economics():
    data = request.get_json(force=True)
    _save("economics", data)
    return jsonify({"ok": True})


# ── Services catalog ──────────────────────────────────────────────────────────

@intel_bp.get("/api/intelligence/services")
def get_services():
    return jsonify(_load("services"))


# ── Company profile (Hadron GBS) ──────────────────────────────────────────────

@intel_bp.get("/api/intelligence/company")
def get_company():
    return jsonify(_load("company"))


@intel_bp.put("/api/intelligence/company")
def save_company():
    data = request.get_json(force=True)
    _save("company", data)
    return jsonify({"ok": True})

