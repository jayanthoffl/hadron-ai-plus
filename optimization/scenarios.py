from typing import List

from schemas import (
    CustomerIntelligence,
    ServiceIntelligence,
    MarketIntelligence,
    InternalEconomics,
    CommercialContext,
    Scenario,
)


class ScenarioGenerator:

    def generate(
        self,
        customer: CustomerIntelligence,
        service: ServiceIntelligence,
        market: MarketIntelligence,
        economics: InternalEconomics,
        context: CommercialContext = None,
    ) -> List[Scenario]:

        mvp = economics.minimum_viable_price

        # ----------------------------------------------------------------
        # Commercial context modifiers
        # ----------------------------------------------------------------
        # These affect scenario PRICING STRATEGY — not delivery cost.
        # The underlying cost ($17.1M) remains deterministic from the catalog.
        # ----------------------------------------------------------------

        if context:
            # Strategic importance → pricing floor position
            importance = context.strategic_importance_signal
            if importance == "HIGH":
                # Established high-value customer → less aggressive entry pricing
                floor_multiplier = 1.08
            elif importance == "LOW":
                # Competitive / new customer → price to win
                floor_multiplier = 0.98
            else:
                # Unknown — use standard multipliers
                floor_multiplier = 1.0

            # Data completeness → range spread
            # Low completeness = higher uncertainty = wider range
            completeness = context.data_completeness
            if completeness < 0.34:
                spread_multiplier = 1.60   # very wide range under high uncertainty
            elif completeness < 0.67:
                spread_multiplier = 1.50
            else:
                spread_multiplier = 1.45   # tighter range when evidence is strong

            # Relationship strength → premium ceiling
            if context.relationship_strength == "ESTABLISHED":
                premium_ceiling = 1.55     # trusted relationship → can price higher
            else:
                premium_ceiling = spread_multiplier

            # Data completeness risk premium on base risk scores
            evidence_risk_premium = max(0.0, 0.15 * (1.0 - completeness))

        else:
            floor_multiplier = 1.0
            spread_multiplier = 1.50
            premium_ceiling = 1.50
            evidence_risk_premium = 0.0

        # ----------------------------------------------------------------
        # Scenario price envelope (derived from MVP + context signals)
        # ----------------------------------------------------------------

        prices = [
            mvp * floor_multiplier * 1.05,
            mvp * floor_multiplier * 1.15,
            mvp * floor_multiplier * 1.30,
            mvp * floor_multiplier * premium_ceiling,
        ]

        names = ["Entry", "Balanced", "Strategic", "Premium"]

        scenarios = []

        for name, price in zip(names, prices):

            margin = (
                (price - economics.estimated_cost) / price
                if price else 0.0
            )

            strategic_value = (
                0.85 if name in ("Strategic", "Balanced") else 0.60
            )

            base_risk = (
                0.25 if name == "Entry"
                else 0.35 if name == "Balanced"
                else 0.50 if name == "Strategic"
                else 0.65
            )

            # Evidence quality risk premium applied to all scenarios
            risk = min(1.0, base_risk + evidence_risk_premium)

            win_signal = max(
                0.10,
                min(
                    0.95,
                    0.90 - ((price / mvp) - 1.0) * 0.8,
                ),
            ) if mvp else 0.10

            scenarios.append(
                Scenario(
                    name=name,
                    price=round(price, 2),
                    term_months=service.estimated_duration_months,
                    scope_factor=1.0,
                    expected_margin=round(margin, 4),
                    strategic_value=strategic_value,
                    risk=round(risk, 3),
                    win_signal=win_signal,
                )
            )

        return scenarios