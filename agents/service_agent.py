import json
from pathlib import Path

from schemas import ServiceIntelligence, Evidence


DATA_FILE = Path(__file__).parent.parent / "data" / "services.json"


class ServiceAgent:

    def __init__(self):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            self.services = json.load(f)

    def analyze(self, service_name: str) -> ServiceIntelligence:

        data = self.services.get(service_name)

        if not data:
            return ServiceIntelligence(
                service_name=service_name,
                description="Service information unavailable"
            )

        evidence = [
            Evidence(
                source="Internal Service Catalog",
                statement=data["description"],
                confidence=0.95
            )
        ]

        return ServiceIntelligence(
            service_name=service_name,
            description=data["description"],
            scope=data["scope"],
            complexity=data["complexity"],
            estimated_duration_months=data["estimated_duration_months"],
            resource_requirements=data["resource_requirements"],
            value_drivers=data["value_drivers"],
            evidence=evidence
        )