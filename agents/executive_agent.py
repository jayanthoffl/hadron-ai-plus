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
        risks,
        precedents=None,
        quantum_optimization=None
    ):

        # ==================================================
        # BUILD LEAN EVIDENCE PACK (Optimized for Tokens)
        # ==================================================

        offers_compact = [
            {
                "tier": o.name,
                "price": f"${o.price:,.0f}",
                "margin": f"{o.expected_margin:.1%}",
                "term_months": o.term_months,
                "rationale": o.strategic_rationale,
                "levers": o.negotiation_levers[:2]
            }
            for o in offers
        ]

        risks_compact = [
            {
                "title": r.get("title") if isinstance(r, dict) else getattr(r, "title", str(r)),
                "severity": r.get("severity") if isinstance(r, dict) else getattr(r, "severity", "MEDIUM"),
                "mitigation": r.get("mitigation") if isinstance(r, dict) else getattr(r, "mitigation", "")
            }
            for r in (risks or [])
        ]

        precedent_text = "No prior comparable deals matched."
        if precedents and precedents.get("top_deals"):
            med = precedents.get("median_price")
            med_str = f"${med:,.0f}" if med else "N/A"
            win = precedents.get("win_rate")
            win_str = f"{win:.0%}" if win is not None else "N/A"
            precedent_text = (
                f"Historical Precedent Search (TF-IDF & Jaccard Engine):\n"
                f"{precedents.get('evidence_gist')}\n"
                f"Comparable Benchmark Range: ${precedents.get('min_price', 0):,.0f} - ${precedents.get('max_price', 0):,.0f} "
                f"(Median: {med_str} | Historical Win Rate: {win_str})"
            )

        quantum_text = "Standard classical heuristic configuration applied."
        if quantum_optimization:
            quantum_text = quantum_optimization.get("quantum_advantage_summary", quantum_text)

        cust_rev_str = f"${customer.revenue:,.0f}" if getattr(customer, "revenue", None) is not None else "Undisclosed"
        svc_complexity_str = f"{service.complexity:.0%}" if getattr(service, "complexity", None) is not None else "Standard"
        svc_duration_str = f"{service.estimated_duration_months} mo" if getattr(service, "estimated_duration_months", None) else "Standard (6 mo)"
        cost_str = f"${economics.estimated_cost:,.0f}" if getattr(economics, "estimated_cost", None) is not None else "$0"
        mvp_str = f"${economics.minimum_viable_price:,.0f}" if getattr(economics, "minimum_viable_price", None) is not None else "$0"
        target_margin_str = f"{economics.target_margin:.1%}" if getattr(economics, "target_margin", None) is not None else "25.0%"
        bench_str = f"{economics.capacity_available:.0f} FTEs" if getattr(economics, "capacity_available", None) is not None else "40 FTEs"
        gap_str = f"${economics.pipeline_gap:,.0f}" if getattr(economics, "pipeline_gap", None) is not None else "$1,150,000"

        prompt = f"""
You are the executive commercial intelligence layer of HADRON AI++ for Hadron GBS (Pune).
Your job is to synthesize the lean evidence pack below into a high-impact executive decision brief.

RULES:
- Do NOT invent facts, competitors, prices, customer details, or financials.
- Use ONLY the structured evidence provided below.
- Do NOT select a single "best" offer; present the strategic trade-offs among the commercial tiers.
- Emphasize the historical precedents and explain the Quantum QAOA combinatorial optimization versus classical baseline.

==================================================
1. OPPORTUNITY CONTEXT (from ServiceNow)
==================================================
Customer: {customer.customer_name} | Industry: {customer.industry or 'Enterprise IT'}
Relationship: {customer.existing_relationship or 'Enterprise Client'} | Revenue: {cust_rev_str}
Service: {service.service_name} | Complexity: {svc_complexity_str} | Duration: {svc_duration_str}
Commercial Objective: {request.commercial_objective}
Additional Context: {request.additional_context}

==================================================
2. INTERNAL DELIVERY ECONOMICS (Hadron GBS Pune HQ)
==================================================
Estimated Delivery Cost: {cost_str}
Minimum Viable Price (MVP Floor): {mvp_str} | Target Margin: {target_margin_str}
Available Bench Capacity: {bench_str} | Q3 Quota Gap: {gap_str}

==================================================
3. HISTORICAL PRECEDENT (Similarity Engine)
==================================================
{precedent_text}

==================================================
4. QUANTUM COMBINATORIAL OPTIMIZATION (Qiskit QAOA)
==================================================
{quantum_text}

==================================================
5. COMMERCIAL OFFER SCENARIOS
==================================================
{json.dumps(offers_compact, indent=2)}

==================================================
6. KEY RISK SIGNALS
==================================================
{json.dumps(risks_compact[:4], indent=2)}

EXECUTIVE ANALYSIS REQUIREMENTS:
Return ONLY valid JSON (no markdown formatting):
{{
    "executive_summary": "Executive briefing covering: opportunity context, cost/MVP economics, historical precedent comparison, quantum vs classical configuration advantage, offer trade-offs, and critical delivery risks.",
    "competitive_intelligence": "Market price positioning and competitor signals summary.",
    "risks": {json.dumps(risks, indent=2) if isinstance(risks, list) else "[]"},
    "evidence": [
        {{"source": "ServiceNow Request", "type": "internal", "confidence": 0.95}},
        {{"source": "Historical Precedent Engine (TF-IDF/Jaccard)", "type": "historical", "confidence": 0.90}},
        {{"source": "Hadron GBS Delivery Economics", "type": "calculated", "confidence": 0.95}},
        {{"source": "Quantum QAOA Combinatorial Solver", "type": "quantum_optimized", "confidence": 0.90}}
    ],
    "confidence": 0.95
}}
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
                try:
                    print(f"[HADRON] Executive Agent → {model}")
                    from gemini_pool import gemini_key_pool
                    response = gemini_key_pool.execute_with_failover(
                        lambda client: client.models.generate_content(
                            model=model,
                            contents=prompt
                        ),
                        max_key_rotations=len(gemini_key_pool.keys)
                    )
                    text = getattr(response, "text", None)
                    if text and text.strip():
                        text = text.strip()
                        print(f"[HADRON] Executive synthesis completed using {model}")
                        break
                except Exception as exc:
                    last_error = exc
                    print(f"[HADRON] Gemini {model} error: {exc}")
                    continue

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
            risks=risks,
            precedents=precedents,
            quantum_optimization=quantum_optimization,
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
        risks,
        precedents=None,
        quantum_optimization=None
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
        # Executive summary (Autonomous Mathematical Synthesis)
        # --------------------------------------------------

        cust_label = customer.customer_name or "Enterprise Account"
        cust_profile = f"{cust_label}"
        if getattr(customer, "industry", None):
            cust_profile += f" ({customer.industry}"
            if getattr(customer, "revenue", None) and customer.revenue > 0:
                cust_profile += f", ${customer.revenue:,.0f} revenue"
            cust_profile += ")"

        svc_name = service.service_name or "Custom Enterprise Transformation"
        duration_str = f"{service.estimated_duration_months} months" if getattr(service, "estimated_duration_months", None) else "standard delivery term"

        summary_parts = [
            f"Commercial intelligence synthesis for {cust_profile} requesting '{svc_name}' (Hadron GBS Pune Delivery Center, {duration_str})."
        ]

        if minimum_price is not None and minimum_price > 0:
            summary_parts.append(
                f"Modeled Pune GDC delivery cost is ${economics_data.get('estimated_cost', 0):,.0f}; "
                f"minimum viable price floor is ${minimum_price:,.0f} at a {target_margin:.1%} target margin hurdle rate."
            )

        if precedents and precedents.get("top_deals"):
            med = precedents.get("median_price")
            med_str = f"${med:,.0f}" if med else "N/A"
            win = precedents.get("win_rate")
            win_str = f"{win:.0%}" if win is not None else "N/A"
            top_ids = [d.get("deal_id") for d in precedents.get("top_deals", []) if d.get("deal_id")]
            ref_deals_str = f" ({', '.join(top_ids[:3])})" if top_ids else ""
            summary_parts.append(
                f"Historical precedent benchmark across {precedents.get('count', 0)} comparable deals{ref_deals_str} "
                f"establishes a median deal value of {med_str} (range: ${precedents.get('min_price', 0):,.0f}–${precedents.get('max_price', 0):,.0f}) "
                f"with an average historical win rate of {win_str}."
            )

        if quantum_optimization and quantum_optimization.get("quantum_solution"):
            q_sol = quantum_optimization["quantum_solution"]
            c_sol = quantum_optimization.get("classical_solution", {})
            imp = quantum_optimization.get("margin_improvement", 0)
            summary_parts.append(
                f"Qiskit QAOA quantum combinatorial optimization evaluated 108 configurations across pricing tiers, delivery schedules, Pune GDC staffing ratios, and risk-share terms. "
                f"The quantum solver selected the '{q_sol.get('pricing_tier')}' tier with {q_sol.get('staffing_mix')} and '{q_sol.get('risk_structure')}', "
                f"achieving a {q_sol.get('expected_margin', 0):.1%} margin (${q_sol.get('price', 0):,.0f}) "
                f"versus classical greedy baseline of {c_sol.get('expected_margin', 0):.1%} (${c_sol.get('price', 0):,.0f}), "
                f"delivering a +{imp:.1%} margin expansion."
            )

        if offer_data:
            summary_parts.append(
                f"Strategic commercial alternatives present clear governance trade-offs: "
                + "; ".join(f"{o.get('name')} at ${float(o.get('price', 0) or 0):,.0f} ({float(o.get('expected_margin', 0) or 0):.1%} margin)" for o in offer_data[:4])
                + "."
            )

        if risk_titles:
            summary_parts.append("Commercial governance risk signals: " + "; ".join(risk_titles[:3]) + ".")

        # --------------------------------------------------
        # Competitive intelligence
        # --------------------------------------------------

        competitive_summary = (
            f"{market_data.get('pricing_environment') or 'Enterprise IT services market environment.'} "
            + ("Signals: " + "; ".join(market_data.get("competitor_signals", [])) if market_data.get("competitor_signals") else "Standard market pricing dynamics.")
        )
        if precedents and precedents.get("top_deals"):
            med = precedents.get("median_price", 0)
            competitive_summary += (
                f" Historical precedent benchmark: {precedents.get('count')} comparable deals analyzed, "
                f"median value ${med:,.0f} (win-rate {precedents.get('win_rate', 0):.0%})."
            )

        # --------------------------------------------------
        # Evidence
        # --------------------------------------------------

        evidence = [
            {"source": "ServiceNow Request", "type": "internal", "confidence": 0.95},
            {"source": "Historical Precedent Engine (TF-IDF/Jaccard)", "type": "historical", "confidence": 0.90 if (precedents and precedents.get("count")) else 0.80},
            {"source": "Hadron GBS Delivery Economics", "type": "calculated", "confidence": 0.95},
            {"source": "Quantum QAOA Combinatorial Solver", "type": "quantum_optimized", "confidence": 0.90 if quantum_optimization else 0.85},
            {"source": "Customer Intelligence", "type": "internal", "confidence": 0.90 if customer_data.get("data_availability") == "FOUND" else 0.75},
            {"source": "Market Intelligence", "type": "market-derived", "confidence": 0.85 if market_data.get("market_reference_price") else 0.75}
        ]

        # --------------------------------------------------
        # Confidence
        # --------------------------------------------------

        confidence = 0.0
        confidence += 0.20 if customer_data.get("data_availability") == "FOUND" else 0.10
        confidence += 0.20 if service_data.get("data_availability") == "FOUND" else (0.15 if service_data.get("data_availability") == "INFERRED" else 0.10)
        confidence += 0.20 if market_data.get("market_reference_price") else 0.10
        confidence += 0.15 if economics_data.get("economics_source") == "CATALOG" else 0.12
        confidence += 0.15 if (precedents and precedents.get("count", 0) > 0) else 0.08
        confidence += 0.10 if quantum_optimization else 0.05

        confidence = max(0.0, min(1.0, confidence))

        return {
            "executive_summary": " ".join(summary_parts),
            "competitive_intelligence": competitive_summary,
            "risks": risks,
            "evidence": evidence,
            "confidence": round(confidence, 2),
            "synthesis_mode": "hadron_mathematical_engine"
        }
