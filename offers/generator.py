from typing import List

from schemas import Scenario, Offer


class OfferGenerator:

    def generate(
        self,
        scenarios: List[Scenario],
        objective: str
    ) -> List[Offer]:

        offers = []

        for scenario in scenarios[:4]:

            if scenario.name == "Entry":
                scope = "Core transformation scope"
                rationale = (
                    "Lower initial commercial barrier while "
                    "creating an expansion path."
                )
                levers = [
                    "Reduce scope",
                    "Add expansion options",
                    "Shorter initial commitment"
                ]

            elif scenario.name == "Balanced":
                scope = "Core transformation + priority capabilities"
                rationale = (
                    "Balances economics, customer value and "
                    "commercial risk."
                )
                levers = [
                    "Moderate discount for longer commitment",
                    "Volume commitment",
                    "Milestone-based expansion"
                ]

            elif scenario.name == "Strategic":
                scope = "Full transformation program"
                rationale = (
                    "Optimizes long-term strategic account value "
                    "and transformation depth."
                )
                levers = [
                    "Multi-year commitment",
                    "Executive sponsorship",
                    "Expansion rights"
                ]

            else:
                scope = "Full premium transformation"
                rationale = (
                    "Maximizes value capture for broad scope "
                    "and accelerated delivery."
                )
                levers = [
                    "Premium SLA",
                    "Accelerated delivery",
                    "Additional capabilities"
                ]

            offers.append(
                Offer(
                    name=scenario.name,
                    price=round(scenario.price, 2),
                    term_months=scenario.term_months,
                    scope=scope,
                    expected_margin=round(
                        scenario.expected_margin,
                        4
                    ),
                    strategic_rationale=rationale,
                    negotiation_levers=levers,
                    risks=[
                        f"Commercial risk score: {scenario.risk:.2f}"
                    ],
                    confidence=0.70
                )
            )

        return offers