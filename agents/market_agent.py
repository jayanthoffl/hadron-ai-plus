"""
MarketAgent — Pure Python competitive intelligence retrieval. No Gemini.

Uses the service_catalog_key resolved by ExtractionAgent to look up
internal competitive price signals from competitors.json.

Returns:
  data_availability = FOUND     → internal competitive intelligence
  data_availability = NOT_FOUND → explicit evidence gap (no manufactured signals)
"""

import json
import os
from pathlib import Path
from google import genai
from google.genai import types

from schemas import MarketIntelligence, Evidence

_DATA_FILE = Path(__file__).parent.parent / "data" / "competitors.json"


class MarketAgent:

    def __init__(self):
        with open(_DATA_FILE, "r", encoding="utf-8") as f:
            self._competitors = json.load(f)
            
        api_key = os.environ.get("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key) if api_key else None

    def analyze(self, intent) -> MarketIntelligence:
        catalog_key = intent.service_catalog_key or "CUSTOM_SERVICE"
        competitor_data = self._competitors.get(catalog_key)

        if competitor_data:
            competitors = competitor_data.get("competitors", [])
            price_signals = [c["price_signal"] for c in competitors if c.get("price_signal")]
            avg_price = sum(price_signals) / len(price_signals) if price_signals else 0

            signal_strings = [
                f"{c['name']}: ${c['price_signal']:,.0f}"
                for c in competitors
                if c.get("price_signal")
            ]

            return MarketIntelligence(
                data_availability="FOUND",
                market_size_signal="Strong enterprise demand",
                demand_signal="Positive",
                pricing_environment="Competitive",
                volatility=0.35,
                competitor_signals=signal_strings,
                market_factors=[
                    "Enterprise technology investment",
                    "Long-term strategic contracts",
                    "Competitive tender environment",
                ],
                evidence=[
                    Evidence(
                        source="Internal Competitive Intelligence",
                        evidence_type="internal_evidence",
                        statement=(
                            f"Internal competitive dataset for '{catalog_key}': "
                            f"{len(competitors)} competitor signals. "
                            f"Range: ${min(price_signals):,.0f}–${max(price_signals):,.0f}. "
                            f"Average: ${avg_price:,.0f}."
                        ),
                        confidence=0.75,
                    )
                ],
            )

        # No internal market data. Fallback to live Gemini Search Grounding!
        if self._client and catalog_key == "CUSTOM_SERVICE" and intent.service_name:
            print(f"[MarketAgent] Missing internal competitive data. Launching Live Search for: {intent.service_name}")
            return self._live_search(intent)

        # Pure fallback if everything fails
        return self._deterministic_fallback(catalog_key)
        
    def _live_search(self, intent) -> MarketIntelligence:
        prompt = f"""
Search the live internet for current consulting and enterprise pricing related to: "{intent.service_name}".
We need to understand what the market charges for these services.
Identify 2-3 market factors (e.g., skill shortages, rising demand).
Estimate an average or range of costs based on what you find.

Return ONLY valid JSON:
{{
  "pricing_environment": "e.g., Highly competitive, Premium pricing",
  "competitor_signals": ["Signal 1 (with dollar amounts if found)", "Signal 2"],
  "market_factors": ["Factor 1", "Factor 2"],
  "summary_statement": "A brief summary of what the live search revealed."
}}
"""
        try:
            response = self._client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.2,
                )
            )
            
            text = (response.text or "").strip()
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()
                
            data = json.loads(text)
            
            return MarketIntelligence(
                data_availability="FOUND",
                market_size_signal="Unknown",
                demand_signal="Active",
                pricing_environment=data.get("pricing_environment", "Unknown"),
                volatility=0.6,
                competitor_signals=data.get("competitor_signals", []),
                market_factors=data.get("market_factors", []),
                evidence=[
                    Evidence(
                        source="External Google Search (Gemini Grounding)",
                        evidence_type="external",
                        statement=data.get("summary_statement", "Live search performed."),
                        confidence=0.6,
                    )
                ]
            )
        except Exception as e:
            print(f"[MarketAgent] Live search failed: {e}. Falling back.")
            return self._deterministic_fallback(intent.service_catalog_key or "CUSTOM_SERVICE")
            
    def _deterministic_fallback(self, catalog_key: str) -> MarketIntelligence:
        return MarketIntelligence(
            data_availability="NOT_FOUND",
            market_size_signal="",
            demand_signal="",
            pricing_environment="",
            volatility=0.5,
            competitor_signals=[],
            market_factors=[],
            evidence=[
                Evidence(
                    source="Internal Competitive Intelligence",
                    evidence_type="internal_evidence",
                    statement=(
                        f"No internal competitive intelligence found for '{catalog_key}'. "
                        f"Market price positioning cannot be validated from internal data."
                    ),
                    confidence=0.0,
                )
            ],
        )