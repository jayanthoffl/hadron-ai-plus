"""
EconomicsEngine — Fully deterministic. No Gemini.

Known service (catalog match):
    economics.json is the authoritative source.

Unknown / CUSTOM_SERVICE:
    deterministic parametric baseline using service.complexity
    and service.estimated_duration_months.

$0 is never a valid result.
Gemini never produces dollar amounts.
"""

import json
from pathlib import Path

from schemas import CustomerIntelligence, ServiceIntelligence, InternalEconomics

_DATA_FILE = Path(__file__).parent.parent / "data" / "economics.json"

# Parametric baseline constants for custom/unmatched services
_MONTHLY_BURN_RATE = 50_000          # base monthly cost per resource-month
_CUSTOM_TARGET_MARGIN = 0.25
_CUSTOM_CAPACITY = 0.0               # unknown → triggers capacity risk


class EconomicsEngine:

    def __init__(self):
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            self._economics = json.load(f)
            
        rate_card_file = Path(__file__).parent.parent / "data" / "rate_card.json"
        try:
            with open(rate_card_file, "r", encoding="utf-8") as f:
                rates = json.load(f)
                # Calculate an average daily rate across key roles, then monthly (20 days)
                avg_hourly = sum(rates.values()) / max(1, len(rates))
                self.monthly_burn_rate = avg_hourly * 8 * 20
        except Exception:
            self.monthly_burn_rate = 50_000

    def calculate(
        self,
        customer: CustomerIntelligence,
        service: ServiceIntelligence,
    ) -> InternalEconomics:

        service_name = service.service_name.strip() if service.service_name else ""
        data = self._economics.get(service_name)

        if data:
            # ---- Catalog-backed deterministic economics ----
            total_cost = (
                data["base_delivery_cost"]
                + data["infrastructure_cost"]
                + data["resource_cost"]
            )
            target_margin = data["target_margin"]
            minimum_price = total_cost / (1.0 - target_margin)

            return InternalEconomics(
                estimated_cost=total_cost,
                resource_cost=data["resource_cost"],
                infrastructure_cost=data["infrastructure_cost"],
                delivery_cost=data["base_delivery_cost"],
                minimum_viable_price=minimum_price,
                target_margin=target_margin,
                capacity_available=data["available_capacity"],
                economics_source="CATALOG",
            )

        # ---- Parametric baseline for unmatched / custom services ----
        # Source: service intelligence (complexity + duration from ServiceAgent)
        complexity = max(0.1, min(1.0, service.complexity or 0.75))
        duration = max(1, service.estimated_duration_months or 9)

        # total_cost = monthly_burn × duration × complexity_factor
        total_cost = self.monthly_burn_rate * duration * (1.0 + complexity)
        minimum_price = total_cost / (1.0 - _CUSTOM_TARGET_MARGIN)

        return InternalEconomics(
            estimated_cost=total_cost,
            resource_cost=total_cost * 0.70,
            infrastructure_cost=total_cost * 0.10,
            delivery_cost=total_cost * 0.20,
            minimum_viable_price=minimum_price,
            target_margin=_CUSTOM_TARGET_MARGIN,
            capacity_available=_CUSTOM_CAPACITY,
            economics_source="PARAMETRIC_BASELINE",
        )