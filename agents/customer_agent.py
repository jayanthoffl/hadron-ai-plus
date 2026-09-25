"""
CustomerAgent — Pure Python evidence retrieval. No Gemini.

Looks up the normalized customer name from HadronIntent in customer.json.

Returns:
  data_availability = FOUND   → full CustomerIntelligence from internal CRM data
  data_availability = NOT_FOUND → skeleton with explicit evidence gap
"""

import json
from pathlib import Path

from schemas import CustomerIntelligence, Evidence

_DATA_FILE = Path(__file__).parent.parent / "data" / "customer.json"
_PROJECTS_FILE = Path(__file__).parent.parent / "data" / "projects.json"


class CustomerAgent:

    def __init__(self):
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            self._customers = json.load(f)
        try:
            with open(_PROJECTS_FILE, "r", encoding="utf-8") as f:
                self._projects = json.load(f)
        except (OSError, json.JSONDecodeError):
            self._projects = {}

    def _find_customer(self, name: str):
        if not name:
            return None, None
        if name in self._customers:
            return name, self._customers[name]
        clean = name.strip().lower()
        # Case-insensitive exact match
        for c_name, c_data in self._customers.items():
            if c_name.strip().lower() == clean:
                return c_name, c_data
        # Substring / alias match
        for c_name, c_data in self._customers.items():
            c_clean = c_name.strip().lower()
            if clean in c_clean or c_clean in clean:
                return c_name, c_data
        return None, None

    def analyze(self, intent) -> CustomerIntelligence:
        raw_name = intent.customer_name.strip() if intent.customer_name else ""
        matched_name, data = self._find_customer(raw_name)
        name = matched_name or raw_name

        if data:
            project_data = self._projects.get(name, {}) or self._projects.get(raw_name, {})
            return CustomerIntelligence(
                customer_name=name,
                data_availability="FOUND",
                industry=data.get("industry", ""),
                revenue=data.get("revenue", 0),
                employee_count=data.get("employee_count", 0),
                strategic_importance=data.get("strategic_importance", ""),
                active_projects=data.get("active_projects", []),
                existing_relationship=data.get("existing_relationship", ""),
                known_needs=data.get("known_needs", []),
                active_budget=project_data.get("active_budget"),
                capacity_pressure=project_data.get("capacity_pressure"),
                evidence=[
                    Evidence(
                        source="Internal CRM",
                        evidence_type="internal_evidence",
                        statement=(
                            f"{name} found in internal customer database. "
                            f"Industry: {data.get('industry', 'N/A')}. "
                            f"Revenue: ${data.get('revenue', 0):,.0f}. "
                            f"Employees: {data.get('employee_count', 0):,}. "
                            f"Strategic importance: {data.get('strategic_importance', 'N/A')}."
                        ),
                        confidence=0.95,
                    )
                ],
            )

        # No internal record — NOT_FOUND is the explicit, truthful result.
        # We do not invent revenue, relationships, or strategic classification.
        return CustomerIntelligence(
            customer_name=name,
            data_availability="NOT_FOUND",
            evidence=[
                Evidence(
                    source="Internal CRM",
                    evidence_type="internal_evidence",
                    statement=(
                        f"No internal CRM record found for '{name}'. "
                        f"Customer intelligence is unavailable from internal sources."
                    ),
                    confidence=0.0,
                )
            ],
        )
