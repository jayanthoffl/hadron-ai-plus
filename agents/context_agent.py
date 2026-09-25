"""
ContextAgent — Pure Python commercial context derivation.

Derives CommercialContext from the retrieved intelligence objects.
This is deterministic — no Gemini.

CommercialContext drives:
  - Scenario pricing multipliers (strategic importance signal)
  - Risk confidence weighting (data completeness)
  - Evidence completeness risk signals
"""

from schemas import CommercialContext


class ContextAgent:

    def derive(
        self,
        intent,
        customer,
        service,
        market,
    ) -> CommercialContext:

        customer_found = customer.data_availability == "FOUND"
        service_found = service.data_availability == "FOUND"
        market_found = market.data_availability == "FOUND"

        # ---- Data completeness ----
        found_count = sum([customer_found, service_found, market_found])
        data_completeness = round(found_count / 3.0, 3)

        # ---- Strategic importance ----
        # From internal CRM if available; UNKNOWN otherwise.
        if customer_found and customer.strategic_importance:
            raw = customer.strategic_importance.strip().upper()
            if raw in {"HIGH", "MEDIUM", "LOW"}:
                strategic = raw
            else:
                strategic = "UNKNOWN"
        else:
            strategic = "UNKNOWN"

        # ---- Relationship strength ----
        if customer_found and customer.existing_relationship:
            relationship = "ESTABLISHED"
        elif customer_found:
            relationship = "NEW"
        else:
            relationship = "UNKNOWN"

        # ---- Urgency ----
        # Derived from intent context keywords only — not invented.
        urgency_keywords = ["urgent", "immediately", "asap", "critical", "deadline"]
        context_lower = (intent.context_summary or "").lower()
        objective_lower = (intent.objective_summary or "").lower()
        if any(kw in context_lower or kw in objective_lower for kw in urgency_keywords):
            urgency = "HIGH"
        else:
            urgency = "NORMAL"

        # ---- Scope complexity ----
        scope_complexity = service.complexity if service_found else 0.75

        return CommercialContext(
            strategic_importance_signal=strategic,
            urgency_signal=urgency,
            scope_complexity=scope_complexity,
            relationship_strength=relationship,
            customer_evidence_available=customer_found,
            service_evidence_available=service_found,
            market_evidence_available=market_found,
            data_completeness=data_completeness,
        )
