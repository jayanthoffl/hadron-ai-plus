"""
ServiceAgent — Pure Python catalog retrieval. No Gemini.

Uses the service_catalog_key resolved by ExtractionAgent (Gemini already
did the semantic matching at extraction time).

Returns:
  data_availability = FOUND        → full ServiceIntelligence from catalog
  data_availability = NOT_FOUND    → CUSTOM_SERVICE baseline (parametric)
"""

import json
from pathlib import Path

from schemas import ServiceIntelligence, Evidence

_DATA_FILE = Path(__file__).parent.parent / "data" / "services.json"


class ServiceAgent:

    def __init__(self):
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            self._services = json.load(f)

    def analyze(self, intent) -> ServiceIntelligence:
        catalog_key = intent.service_catalog_key or "CUSTOM_SERVICE"
        data = self._services.get(catalog_key)

        if data:
            return ServiceIntelligence(
                service_name=catalog_key,
                data_availability="FOUND",
                description=data["description"],
                scope=data["scope"],
                complexity=data["complexity"],
                estimated_duration_months=data["estimated_duration_months"],
                resource_requirements=data["resource_requirements"],
                value_drivers=data["value_drivers"],
                evidence=[
                    Evidence(
                        source="Internal Service Catalog",
                        evidence_type="internal_evidence",
                        statement=(
                            f"Service '{catalog_key}' matched in internal delivery catalog. "
                            f"Complexity: {data['complexity']:.0%}. "
                            f"Standard duration: {data['estimated_duration_months']} months."
                        ),
                        confidence=0.95,
                    )
                ],
            )

        # CUSTOM_SERVICE — no catalog match.
        # Use inferred service name from intent.
        # Parametric economics will apply in EconomicsEngine.
        raw_name = intent.service_name or catalog_key
        return ServiceIntelligence(
            service_name=raw_name,
            data_availability="NOT_FOUND",
            description="Service not found in internal delivery catalog. Parametric baseline applied.",
            scope=["Custom requirements discovery", "Tailored delivery"],
            complexity=0.75,
            estimated_duration_months=9,
            resource_requirements={},
            value_drivers=[],
            evidence=[
                Evidence(
                    source="Internal Service Catalog",
                    evidence_type="internal_evidence",
                    statement=(
                        f"'{raw_name}' does not match any internal catalog service. "
                        f"No historical delivery data available. "
                        f"Parametric cost baseline will be applied."
                    ),
                    confidence=0.0,
                )
            ],
        )