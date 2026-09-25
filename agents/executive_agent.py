import json
import time

from google import genai

from config import settings


class ExecutiveAgent:

    def __init__(self):

        if not settings.GEMINI_API_KEY:
            self.client = None
            return

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def synthesize(
        self,
        request,
        customer,
        service,
        market,
        economics,
        offers,
        risks
    ):

        # ==================================================
        # BUILD EXECUTIVE PROMPT
        # ==================================================

        prompt = f"""
You are the executive commercial intelligence layer
of HADRON AI++.

Your job is to synthesize structured enterprise,
market, economic, optimization, and risk intelligence
into an executive decision brief.

You are NOT the source of truth.

Do NOT invent facts, competitors, prices, customer
information, financial information, or market statistics.

If economics_source is INSUFFICIENT_SCOPE, the zero-valued
economics fields mean "not calculated". Do not present them
as a zero-dollar cost or price. State what scope information
is needed before pricing can be produced.

Use only the information supplied below.

Clearly distinguish:

- internal enterprise information
- market intelligence
- competitive signals
- calculated economics
- optimization outputs
- assumptions
- identified risks

==================================================
CUSTOMER INTELLIGENCE
==================================================

{customer.model_dump_json(indent=2)}

==================================================
SERVICE INTELLIGENCE
==================================================

{service.model_dump_json(indent=2)}

==================================================
MARKET INTELLIGENCE
==================================================

{market.model_dump_json(indent=2)}

==================================================
INTERNAL ECONOMICS
==================================================

{economics.model_dump_json(indent=2)}

==================================================
OFFER SET
==================================================

{json.dumps(
    [o.model_dump() for o in offers],
    indent=2
)}

==================================================
DETERMINISTIC RISK INTELLIGENCE
==================================================

{json.dumps(
    risks,
    indent=2
)}

==================================================
COMMERCIAL OBJECTIVE
==================================================

{request.commercial_objective}

==================================================
ADDITIONAL CONTEXT
==================================================

{request.additional_context}

==================================================
EXECUTIVE ANALYSIS REQUIREMENTS
==================================================

The executive summary must explain:

1. What is happening with the opportunity.
2. What the customer/service context indicates.
3. What the market and competitive signals indicate.
4. What the internal economics indicate.
5. How the different offers should be interpreted.
6. The major risks.
7. Important assumptions or missing evidence.

Do NOT select a single "best" offer.

Do NOT rank the offers.

Present the alternatives and their trade-offs so that
an executive can make the commercial decision.

The supplied deterministic risk analysis is authoritative
for identified risk triggers. Do not remove or invent
risk categories.

The scenario win_signal is a rule-based price heuristic, not
historical win-rate evidence. Never describe it as a measured
probability of winning.

Return ONLY valid JSON.

Return exactly these keys:

{{
    "executive_summary": "...",
    "competitive_intelligence": "...",
    "risks": [],
    "evidence": [],
    "confidence": 0.0
}}

The "risks" field should preserve the supplied
deterministic risk objects.

The "evidence" field should identify the major evidence
used in the analysis and whether it is internal,
market-derived, calculated, or an assumption.

The "confidence" field must be a number between 0 and 1
representing the completeness and reliability of the
available evidence, NOT confidence that a deal will win.
"""

        # ==================================================
        # TRY GEMINI
        # ==================================================

        if self.client is not None:

            models_to_try = [
                settings.GEMINI_MODEL
            ]

            fallback = getattr(
                settings,
                "GEMINI_FALLBACK_MODEL",
                None
            )

            if (
                fallback
                and fallback not in models_to_try
            ):
                models_to_try.append(
                    fallback
                )

            last_error = None
            text = None

            for model in models_to_try:

                # Three attempts per model.
                for attempt in range(3):

                    try:

                        print(
                            f"[HADRON] Executive Agent → "
                            f"{model} "
                            f"(attempt {attempt + 1}/3)"
                        )

                        response = (
                            self.client.models.generate_content(
                                model=model,
                                contents=prompt
                            )
                        )

                        text = getattr(
                            response,
                            "text",
                            None
                        )

                        if not text:
                            raise RuntimeError(
                                "Gemini returned an empty response."
                            )

                        text = text.strip()

                        print(
                            f"[HADRON] Executive synthesis "
                            f"completed using {model}"
                        )

                        break

                    except Exception as exc:

                        last_error = exc

                        print(
                            f"[HADRON] Gemini error: {exc}"
                        )

                        if attempt < 2:

                            delay = 2 ** attempt

                            print(
                                f"[HADRON] Retrying in "
                                f"{delay}s..."
                            )

                            time.sleep(delay)

                if text:
                    break

            # ==================================================
            # GEMINI SUCCESS
            # ==================================================

            if text:

                try:

                    result = self._parse_json(
                        text
                    )

                    return self._normalize_result(
                        result,
                        risks
                    )

                except Exception as exc:

                    print(
                        "[HADRON] Gemini synthesis "
                        f"could not be parsed: {exc}"
                    )

            else:

                print(
                    "[HADRON] All Gemini models "
                    "unavailable."
                )

                print(
                    f"[HADRON] Last Gemini error: "
                    f"{last_error}"
                )

        else:

            print(
                "[HADRON] Gemini API key unavailable. "
                "Using deterministic executive fallback."
            )

        # ==================================================
        # DETERMINISTIC FALLBACK
        # ==================================================

        return self._deterministic_fallback(
            request=request,
            customer=customer,
            service=service,
            market=market,
            economics=economics,
            offers=offers,
            risks=risks
        )

    # ======================================================
    # GEMINI JSON PARSER
    # ======================================================

    @staticmethod
    def _parse_json(text):

        text = text.strip()

        if text.startswith("```"):

            text = text.replace(
                "```json",
                ""
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()

        return json.loads(text)

    # ======================================================
    # RESULT NORMALIZATION
    # ======================================================

    @staticmethod
    def _normalize_result(
        result,
        risks
    ):

        result.setdefault(
            "executive_summary",
            ""
        )

        result.setdefault(
            "competitive_intelligence",
            ""
        )

        result.setdefault(
            "risks",
            risks
        )

        result.setdefault(
            "evidence",
            []
        )

        result.setdefault(
            "confidence",
            0.5
        )
        result.setdefault("synthesis_mode", "gemini")

        # Deterministic risks are authoritative.
        # Gemini cannot silently delete them.

        if not result["risks"]:
            result["risks"] = risks

        # Clamp confidence to [0, 1].

        try:

            confidence = float(
                result["confidence"]
            )

        except (
            TypeError,
            ValueError
        ):

            confidence = 0.5

        result["confidence"] = max(
            0.0,
            min(
                1.0,
                confidence
            )
        )

        return result

    # ======================================================
    # DETERMINISTIC EXECUTIVE FALLBACK
    # ======================================================

    @staticmethod
    def _deterministic_fallback(
        request,
        customer,
        service,
        market,
        economics,
        offers,
        risks
    ):

        print(
            "[HADRON] Building deterministic "
            "executive intelligence fallback."
        )

        customer_data = (
            customer.model_dump()
        )

        service_data = (
            service.model_dump()
        )

        market_data = (
            market.model_dump()
        )

        economics_data = (
            economics.model_dump()
        )

        offer_data = [
            offer.model_dump()
            for offer in offers
        ]

        # --------------------------------------------------
        # Extract useful economics
        # --------------------------------------------------

        minimum_price = (
            economics_data.get(
                "minimum_viable_price"
            )
        )

        target_margin = (
            economics_data.get(
                "target_margin"
            )
        )

        complexity = (
            service_data.get(
                "complexity"
            )
        )

        capacity = (
            economics_data.get(
                "capacity_available"
            )
        )

        required_capacity = (
            economics_data.get(
                "required_capacity"
            )
        )

        # --------------------------------------------------
        # Risk summary
        # --------------------------------------------------

        high_risks = [
            risk
            for risk in risks
            if risk.get("severity") == "HIGH"
        ]

        medium_risks = [
            risk
            for risk in risks
            if risk.get("severity") == "MEDIUM"
        ]

        risk_titles = [
            risk.get(
                "title",
                risk.get("type", "Unknown risk")
            )
            for risk in risks
        ]

        # --------------------------------------------------
        # Executive summary
        # --------------------------------------------------

        summary_parts = [
            f"Preliminary pricing analysis for {customer.customer_name or 'the named customer'} — {service.service_name or 'the requested service'}."
        ]
        if minimum_price is not None and minimum_price > 0:
            summary_parts.append(
                f"The modeled delivery cost is ${economics_data.get('estimated_cost', 0):,.0f}; "
                f"the minimum viable price is ${minimum_price:,.0f} at a {target_margin:.1%} target margin."
            )
        else:
            summary_parts.append(
                "No defensible price was produced because verified catalog data and usable custom-service scope estimates were unavailable. The zero-valued economics fields indicate not calculated, not free delivery."
            )
        if offer_data:
            prices = [float(o.get("price", 0) or 0) for o in offer_data]
            margins = [float(o.get("expected_margin", 0) or 0) for o in offer_data]
            summary_parts.append(
                f"The generated alternatives range from ${min(prices):,.0f} to ${max(prices):,.0f}; "
                f"modeled margins range from {min(margins):.1%} to {max(margins):.1%}. "
                "These are scenario calculations, not a validated win-probability forecast."
            )
        if market_data.get("market_reference_price"):
            summary_parts.append(
                f"Available market reference is ${market_data['market_reference_price']:,.0f} "
                f"({market_data.get('pricing_environment') or 'pricing environment unspecified'})."
            )
        else:
            summary_parts.append(
                "No usable competitor price reference was available, so the offer range is not market-validated."
            )
        if required_capacity is not None:
            summary_parts.append(
                f"Capacity model: {required_capacity:g} estimated role FTE required versus "
                f"{capacity or 0:g} available FTE from the internal capacity file."
            )
        else:
            summary_parts.append(
                "Staffing requirements could not be estimated from the request; capacity feasibility remains unverified."
            )
        if economics_data.get("project_budget") is not None:
            summary_parts.append(
                f"The explicitly stated project budget is ${economics_data['project_budget']:,.0f}."
            )
        if economics_data.get("historical_deal_count", 0):
            summary_parts.append(
                f"Comparison uses {economics_data['historical_deal_count']} historical deals "
                f"with an average value of ${economics_data['historical_average_deal_value']:,.0f}."
            )
        else:
            summary_parts.append("No usable historical deal values are available for a past-project comparison.")
        if risk_titles:
            summary_parts.append("Risks requiring review: " + "; ".join(risk_titles[:4]) + ".")
        summary_parts.append(
            "Treat this as a provisional decision aid: validate the scope, staffing plan, market evidence, and cost assumptions before committing."
        )

        # --------------------------------------------------
        # Competitive intelligence
        # --------------------------------------------------

        competitive_summary = (
            f"{market_data.get('pricing_environment') or 'No market pricing environment was established.'} "
            + ("Signals: " + "; ".join(market_data.get("competitor_signals", [])) if market_data.get("competitor_signals") else "No competitor price signals are available.")
        )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        evidence = [
            {"source": "customer_intelligence", "type": "internal", "status": customer_data.get("data_availability", "UNKNOWN")},
            {"source": "service_intelligence", "type": "internal_or_inferred", "status": service_data.get("data_availability", "UNKNOWN")},
            {"source": "market_intelligence", "type": "market-derived", "status": market_data.get("data_availability", "UNKNOWN"), "reference_price": market_data.get("market_reference_price")},
            {"source": "internal_economics", "type": "calculated", "status": economics_data.get("economics_source", "UNKNOWN")},
            {"source": "internal_capacity", "type": "internal", "status": "available" if capacity is not None else "unavailable"},
            {"source": "historical_deals", "type": "internal", "status": "available" if economics_data.get("historical_deal_count") else "no_usable_records"},
        ]

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        # This is evidence completeness, NOT win probability.

        confidence = 0.0
        confidence += 0.25 if customer_data.get("data_availability") == "FOUND" else 0.0
        confidence += 0.25 if service_data.get("data_availability") == "FOUND" else (0.10 if service_data.get("data_availability") == "INFERRED" else 0.0)
        confidence += 0.25 if market_data.get("market_reference_price") else 0.0
        confidence += 0.15 if economics_data.get("economics_source") == "CATALOG" else 0.05
        confidence += 0.10 if required_capacity is not None else 0.0

        confidence = max(
            0.0,
            min(
                1.0,
                confidence
            )
        )

        return {
            "executive_summary": " ".join(
                summary_parts
            ),

            "competitive_intelligence": (
                competitive_summary
            ),

            "risks": risks,

            "evidence": evidence,

            "confidence": round(
                confidence,
                2
            ),

            "synthesis_mode": (
                "deterministic_fallback"
            )
        }
