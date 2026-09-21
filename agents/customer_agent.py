import json
from pathlib import Path

from schemas import CustomerIntelligence, Evidence


DATA_FILE = Path(__file__).parent.parent / "data" / "customer.json"


class CustomerAgent:

    def __init__(self):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            self.customers = json.load(f)

    def analyze(self, customer_name: str) -> CustomerIntelligence:

        data = self.customers.get(customer_name)

        if not data:
            return CustomerIntelligence(
                customer_name=customer_name,
                strategic_importance="Unknown"
            )

        evidence = [
            Evidence(
                source="Internal CRM",
                statement=f"Customer has {data['employee_count']} employees "
                          f"and reported revenue of ${data['revenue']:,.0f}.",
                confidence=0.95
            ),
            Evidence(
                source="Internal Project System",
                statement=f"Customer has {len(data['active_projects'])} active strategic projects.",
                confidence=0.90
            )
        ]

        return CustomerIntelligence(
            customer_name=customer_name,
            industry=data["industry"],
            revenue=data["revenue"],
            employee_count=data["employee_count"],
            strategic_importance=data["strategic_importance"],
            active_projects=data["active_projects"],
            existing_relationship=data["existing_relationship"],
            known_needs=data["known_needs"],
            evidence=evidence
        )