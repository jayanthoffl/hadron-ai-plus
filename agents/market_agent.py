import json
from pathlib import Path

from schemas import MarketIntelligence, Evidence


DATA_FILE = Path(__file__).parent.parent / "data" / "competitors.json"


class MarketAgent:

    def __init__(self):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            self.competitors = json.load(f)

    def analyze(self, service_name: str) -> MarketIntelligence:

        competitor_data = self.competitors.get(
            service_name,
            {}
        )

        competitors = competitor_data.get("competitors", [])

        price_signals = [
            c["price_signal"]
            for c in competitors
            if c.get("price_signal")
        ]

        average_price = (
            sum(price_signals) / len(price_signals)
            if price_signals
            else 0
        )

        evidence = []

        if price_signals:
            evidence.append(
                Evidence(
                    source="Competitive Intelligence Dataset",
                    statement=(
                        f"Observed competitive price signals range from "
                        f"${min(price_signals):,.0f} to "
                        f"${max(price_signals):,.0f}, with an average "
                        f"signal of ${average_price:,.0f}."
                    ),
                    confidence=0.75
                )
            )

        return MarketIntelligence(
            market_size_signal="Strong enterprise demand",
            demand_signal="Positive",
            pricing_environment="Competitive",
            volatility=0.35,
            competitor_signals=[
                f"{c['name']}: ${c['price_signal']:,.0f}"
                for c in competitors
            ],
            market_factors=[
                "Enterprise AI investment",
                "Transformation program competition",
                "Long-term strategic contracts"
            ],
            evidence=evidence
        )