import json
from pathlib import Path

from schemas import (
    CustomerIntelligence,
    ServiceIntelligence,
    InternalEconomics
)


DATA_FILE = Path(__file__).parent.parent / "data" / "economics.json"


class EconomicsEngine:

    def __init__(self):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            self.economics = json.load(f)

    def calculate(
        self,
        customer: CustomerIntelligence,
        service: ServiceIntelligence
    ) -> InternalEconomics:

        data = self.economics.get(service.service_name)

        if not data:
            return InternalEconomics()

        total_cost = (
            data["base_delivery_cost"]
            + data["infrastructure_cost"]
            + data["resource_cost"]
        )

        target_margin = data["target_margin"]

        minimum_price = total_cost / (1 - target_margin)

        return InternalEconomics(
            estimated_cost=total_cost,
            resource_cost=data["resource_cost"],
            infrastructure_cost=data["infrastructure_cost"],
            delivery_cost=data["base_delivery_cost"],
            minimum_viable_price=minimum_price,
            target_margin=target_margin,
            capacity_available=data["available_capacity"]
        )