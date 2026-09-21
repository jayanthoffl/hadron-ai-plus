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

        summary_parts = []

        summary_parts.append(
            "HADRON evaluated the opportunity using "
            "customer, service, market, internal economic, "
            "optimization, and deterministic risk signals."
        )

        if minimum_price is not None:

            summary_parts.append(
                f"The internal economic model establishes "
                f"a minimum viable price of "
                f"{minimum_price:,.2f}."
            )

        if target_margin is not None:

            summary_parts.append(
                f"The modeled target margin is "
                f"{target_margin:.1%}."
            )

        if complexity is not None:

            summary_parts.append(
                f"The service intelligence reports "
                f"a delivery complexity of "
                f"{complexity:.2f}."
            )

        if (
            capacity is not None
            and required_capacity is not None
        ):

            summary_parts.append(
                f"Modeled delivery capacity is "
                f"{required_capacity} required versus "
                f"{capacity} available."
            )

        if high_risks:

            summary_parts.append(
                "High-severity risk signals include: "
                + ", ".join(
                    risk_titles
                )
                + "."
            )

        elif medium_risks:

            summary_parts.append(
                "Medium-severity risk signals include: "
                + ", ".join(
                    risk_titles
                )
                + "."
            )

        else:

            summary_parts.append(
                "No material deterministic risk trigger "
                "was identified from the currently "
                "available structured evidence."
            )

        summary_parts.append(
            "The generated offer set should be evaluated "
            "as a set of commercial alternatives with "
            "different economic and strategic trade-offs; "
            "HADRON does not select a single offer."
        )

        # --------------------------------------------------
        # Competitive intelligence
        # --------------------------------------------------

        competitive_summary = (
            "Competitive intelligence is based on the "
            "structured market signals supplied to HADRON. "
            "No additional market facts are introduced "
            "by the deterministic fallback."
        )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        evidence = [

            {
                "source": "customer_intelligence",
                "type": "internal",
                "status": "available"
            },

            {
                "source": "service_intelligence",
                "type": "internal",
                "status": "available"
            },

            {
                "source": "market_intelligence",
                "type": "market-derived",
                "status": "available"
            },

            {
                "source": "internal_economics",
                "type": "calculated",
                "status": "available"
            },

            {
                "source": "optimization_offer_set",
                "type": "calculated",
                "status": "available"
            },

            {
                "source": "deterministic_risk_engine",
                "type": "calculated",
                "status": "available"
            }
        ]

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        # This is evidence completeness, NOT win probability.

        confidence = 0.75

        if not market_data:
            confidence -= 0.15

        if not offer_data:
            confidence -= 0.15

        if not economics_data:
            confidence -= 0.15

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
