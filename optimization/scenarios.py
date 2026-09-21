from typing import List

from schemas import (
    CustomerIntelligence,
    ServiceIntelligence,
    MarketIntelligence,
    InternalEconomics,
    Scenario
)


class ScenarioGenerator:

    def generate(
        self,
        customer: CustomerIntelligence,
        service: ServiceIntelligence,
        market: MarketIntelligence,
        economics: InternalEconomics
    ) -> List[Scenario]:

        market_reference = economics.minimum_viable_price

        # Strategic pricing envelope
        prices = [
            market_reference * 1.05,
            market_reference * 1.15,
            market_reference * 1.30,
            market_reference * 1.50
        ]

        names = [
            "Entry",
            "Balanced",
            "Strategic",
            "Premium"
        ]

        scenarios = []

        for name, price in zip(names, prices):

            margin = (
                (price - economics.estimated_cost) / price
            ) if price else 0.0

            strategic_value = (
                0.8
                if name in ["Strategic", "Balanced"]
                else 0.55
            )

            risk = (
                0.25 if name == "Entry"
                else 0.35 if name == "Balanced"
                else 0.50 if name == "Strategic"
                else 0.65
            )

            win_signal = max(
                0.1,
                min(
                    0.95,
                    0.90 - ((price / market_reference) - 1) * 0.8
                )
            ) if market_reference else 0.1

            scenarios.append(
                Scenario(
                    name=name,
                    price=round(price, 2),
                    term_months=service.estimated_duration_months,
                    scope_factor=1.0,
                    expected_margin=round(margin, 4),
                    strategic_value=strategic_value,
                    risk=risk,
                    win_signal=win_signal
                )
            )

        return scenarios