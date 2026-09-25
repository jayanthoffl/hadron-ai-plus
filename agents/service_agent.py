"""
ServiceAgent — Pure Python catalog retrieval. No Gemini.

Uses the service_catalog_key resolved by ExtractionAgent (Gemini already
did the semantic matching at extraction time).

Returns FOUND for catalog services, INFERRED for a service with extracted
planning inputs, or NOT_FOUND when there is not enough evidence to estimate.
"""

import json
from pathlib import Path

from schemas import ServiceIntelligence, Evidence

_DATA_FILE = Path(__file__).parent.parent / "data" / "services.json"


class ServiceAgent:

    def __init__(self):
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            self._services = json.load(f)

    def _find_service(self, key: str, fallback_name: str = ""):
        if key and key in self._services:
            return key, self._services[key]
        candidates = [k for k in (key, fallback_name) if k and k != "CUSTOM_SERVICE"]
        for c in candidates:
            clean = c.strip().lower()
            for s_name, s_data in self._services.items():
                if s_name.strip().lower() == clean:
                    return s_name, s_data
            for s_name, s_data in self._services.items():
                s_clean = s_name.strip().lower()
                if clean in s_clean or s_clean in clean:
                    return s_name, s_data
        return None, None

    def analyze(self, intent) -> ServiceIntelligence:
        catalog_key = intent.service_catalog_key or "CUSTOM_SERVICE"
        matched_key, data = self._find_service(catalog_key, intent.service_name)
        if matched_key:
            catalog_key = matched_key

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

        # CUSTOM_SERVICE — use extraction estimates only as provisional
        # planning inputs. Missing estimates stay visibly unknown.
        raw_name = intent.service_name or catalog_key
        estimated_complexity = intent.estimated_complexity
        estimated_duration = intent.estimated_duration_months
        estimated_resources = intent.estimated_resource_requirements or {}
        has_estimate = any((estimated_complexity is not None, estimated_duration, estimated_resources))
        estimate_notes = intent.service_estimate_notes or "No service-specific estimate was available."
        estimation_status = "INFERRED" if has_estimate else "NOT_FOUND"
        estimate_statement = (
            f"Provisional extraction estimate: {estimate_notes}"
            if has_estimate else
            "No reliable complexity, duration, or staffing estimate is available; pricing is withheld pending scope clarification."
        )
        return ServiceIntelligence(
            service_name=raw_name,
            data_availability=estimation_status,
            description=(
                "Service is not in the internal delivery catalog. "
                f"{estimate_statement}"
            ),
            scope=intent.key_requirements or ["Custom requirements discovery", "Tailored delivery"],
            complexity=(max(0.1, min(1.0, estimated_complexity)) if estimated_complexity is not None else None),
            estimated_duration_months=(max(1, estimated_duration) if estimated_duration else None),
            resource_requirements=estimated_resources,
            value_drivers=[],
            evidence=[
                Evidence(
                    source="Gemini service planning estimate" if has_estimate else "Internal Service Catalog",
                    evidence_type="model_inference" if has_estimate else "internal_evidence",
                    statement=(
                        f"'{raw_name}' does not match any internal catalog service. "
                        f"No verified delivery history is available. {estimate_statement}"
                    ),
                    confidence=(max(0.0, min(1.0, intent.service_estimate_confidence)) if has_estimate else 0.0),
                )
            ],
        )
