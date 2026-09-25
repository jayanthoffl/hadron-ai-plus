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
import re
from pathlib import Path

from schemas import CustomerIntelligence, ServiceIntelligence, InternalEconomics

_DATA_FILE = Path(__file__).parent.parent / "data" / "economics.json"

# Parametric baseline constants for custom/unmatched services
_MONTHLY_BURN_RATE = 50_000          # base monthly cost per resource-month
_CUSTOM_TARGET_MARGIN = 0.25
_CUSTOM_CAPACITY = 0.0               # unknown → triggers capacity risk
_HOURS_PER_MONTH = 160


class EconomicsEngine:

    def __init__(self):
        root = Path(__file__).parent.parent / "data"
        self._rate_card_file = root / "rate_card.json"
        self._capacity_file = root / "internal_capacity.json"
        self._deals_file = root / "historical_deals.json"
        self._refresh_data()

    def _refresh_data(self):
        """Reload editable commercial data so dashboard changes affect new analyses."""
        def read(path, fallback):
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return fallback

        self._economics = read(_DATA_FILE, {})
        self.capacity = read(self._capacity_file, {})
        self.deals = read(self._deals_file, [])
        rates = self._load_rates()
        if rates:
            avg_hourly = sum(float(value) for value in rates.values()) / len(rates)
            self.monthly_burn_rate = avg_hourly * 8 * 20
        else:
            self.monthly_burn_rate = 50_000

    def calculate(
        self,
        customer: CustomerIntelligence,
        service: ServiceIntelligence,
        request=None,
    ) -> InternalEconomics:

        self._refresh_data()

        capacity_headcount = self.capacity.get("headcount", {})
        available_fraction = float(self.capacity.get("available_billable_capacity", 0.0) or 0.0)
        available_fte = sum(
            float(count or 0) for role, count in capacity_headcount.items()
            if role != "total_billable"
        ) * available_fraction
        required_fte = sum(float(count or 0) for count in service.resource_requirements.values())
        required_capacity = required_fte if service.resource_requirements else None
        revenue_target = self.capacity.get("quarterly_revenue_target")
        pipeline_value = self.capacity.get("confirmed_pipeline_value")
        pipeline_gap = (
            max(0.0, float(revenue_target) - float(pipeline_value))
            if revenue_target is not None and pipeline_value is not None else None
        )
        deal_values = [
            float(deal.get("deal_value", deal.get("contract_value", deal.get("price", 0))) or 0)
            for deal in self.deals if isinstance(deal, dict)
        ]
        deal_values = [value for value in deal_values if value > 0]
        historical_average = sum(deal_values) / len(deal_values) if deal_values else None
        project_budget = self._extract_project_budget(
            getattr(request, "additional_context", "") if request else ""
        )

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
                capacity_available=available_fte,
                required_capacity=required_capacity,
                revenue_target=revenue_target,
                confirmed_pipeline_value=pipeline_value,
                pipeline_gap=pipeline_gap,
                project_budget=project_budget,
                historical_deal_count=len(deal_values),
                historical_average_deal_value=historical_average,
                economics_source="CATALOG",
            )

        # A custom service with no extracted scope is not priceable. Returning
        # a confident-looking number from a generic default produced the same
        # quote for unrelated requests and hid the missing evidence.
        if (
            service.data_availability == "NOT_FOUND"
            or service.complexity is None
            or service.estimated_duration_months is None
        ):
            return InternalEconomics(
                estimated_cost=0,
                resource_cost=0,
                infrastructure_cost=0,
                delivery_cost=0,
                minimum_viable_price=0,
                target_margin=_CUSTOM_TARGET_MARGIN,
                capacity_available=available_fte,
                required_capacity=None,
                revenue_target=revenue_target,
                confirmed_pipeline_value=pipeline_value,
                pipeline_gap=pipeline_gap,
                project_budget=project_budget,
                historical_deal_count=len(deal_values),
                historical_average_deal_value=historical_average,
                economics_source="INSUFFICIENT_SCOPE",
            )

        # ---- Parametric baseline for unmatched / custom services ----
        # Source: service intelligence (complexity + duration from ServiceAgent)
        complexity = max(0.1, min(1.0, service.complexity))
        duration = max(1, service.estimated_duration_months)

        # total_cost = monthly_burn × duration × complexity_factor
        resource_requirements = service.resource_requirements or {}
        if resource_requirements:
            normalized_rates = {
                self._normalize_role(key): float(value)
                for key, value in self._load_rates().items()
            }
            estimated_labor = sum(
                float(count or 0) * normalized_rates.get(self._normalize_role(role), 0.0)
                * _HOURS_PER_MONTH * duration
                for role, count in resource_requirements.items()
            )
            # Role names with no configured rate are excluded instead of silently assigned a made-up rate.
            if estimated_labor > 0:
                resource_cost = estimated_labor
                delivery_cost = estimated_labor * (0.15 + complexity * 0.15)
                infrastructure_cost = estimated_labor * 0.10
                total_cost = resource_cost + delivery_cost + infrastructure_cost
            else:
                total_cost = self.monthly_burn_rate * duration * (1.0 + complexity)
                resource_cost, infrastructure_cost, delivery_cost = total_cost * 0.70, total_cost * 0.10, total_cost * 0.20
        else:
            total_cost = self.monthly_burn_rate * duration * (1.0 + complexity)
            resource_cost, infrastructure_cost, delivery_cost = total_cost * 0.70, total_cost * 0.10, total_cost * 0.20
        minimum_price = total_cost / (1.0 - _CUSTOM_TARGET_MARGIN)

        return InternalEconomics(
            estimated_cost=total_cost,
            resource_cost=resource_cost,
            infrastructure_cost=infrastructure_cost,
            delivery_cost=delivery_cost,
            minimum_viable_price=minimum_price,
            target_margin=_CUSTOM_TARGET_MARGIN,
            capacity_available=available_fte,
            required_capacity=required_capacity,
            revenue_target=revenue_target,
            confirmed_pipeline_value=pipeline_value,
            pipeline_gap=pipeline_gap,
            project_budget=project_budget,
            historical_deal_count=len(deal_values),
            historical_average_deal_value=historical_average,
            economics_source="PARAMETRIC_BASELINE",
        )

    def _load_rates(self):
        try:
            return json.loads(self._rate_card_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _normalize_role(role: str):
        normalized = re.sub(r"[^a-z]", "", (role or "").lower())
        return normalized[:-1] if normalized.endswith("s") else normalized

    @staticmethod
    def _extract_project_budget(context: str):
        """Read only an explicitly labelled project budget from request context."""
        match = re.search(
            r"\b(?:project\s+)?budget\b\s*(?:is|of|around|approximately|:|=)?\s*\$?\s*([\d,]+(?:\.\d+)?)\s*(million|millions|m|thousand|k)?\b",
            context or "",
            re.IGNORECASE,
        )
        if not match:
            return None
        amount = float(match.group(1).replace(",", ""))
        unit = (match.group(2) or "").lower()
        if unit in {"million", "millions", "m"}:
            amount *= 1_000_000
        elif unit in {"thousand", "k"}:
            amount *= 1_000
        return amount
