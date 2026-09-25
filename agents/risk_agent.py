from typing import Any, Dict, List


class RiskAgent:
    """
    Deterministic commercial risk analysis layer for HADRON AI++.

    This agent does NOT use Gemini.

    Risks are derived from:
    - customer intelligence
    - service intelligence
    - market intelligence
    - internal economics
    - offer structure

    Gemini may explain these risks later, but it does not
    create or suppress deterministic risk signals.
    """

    def analyze(
        self,
        request,
        customer,
        service,
        market,
        economics,
        offers,
    ) -> List[Dict[str, Any]]:

        risks = []

        # =========================================================
        # 1. PRICE DISCONNECT
        # =========================================================

        internal_floor = self._get_numeric(
            economics,
            "minimum_viable_price"
        )

        market_reference = self._extract_market_reference(
            market
        )

        if (
            internal_floor is not None
            and market_reference is not None
            and market_reference > 0
        ):

            ratio = internal_floor / market_reference

            if ratio >= 1.50:
                severity = "HIGH"
            elif ratio >= 1.20:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            risks.append({
                "type": "PRICE_DISCONNECT",
                "severity": severity,
                "title": (
                    "Internal economics materially exceed "
                    "observed market signals"
                ),
                "description": (
                    "The internally calculated minimum viable "
                    "price is materially different from the "
                    "observed competitive market range."
                ),
                "metric": {
                    "internal_floor": round(
                        internal_floor,
                        2
                    ),
                    "market_reference": round(
                        market_reference,
                        2
                    ),
                    "ratio": round(
                        ratio,
                        3
                    )
                },
                "mitigation": (
                    "Review scope, delivery model, contract "
                    "term, differentiation, and commercial "
                    "structure before applying a major price "
                    "reduction."
                )
            })

        # =========================================================
        # 2. DELIVERY COMPLEXITY
        # =========================================================

        complexity = self._get_numeric(
            service,
            "complexity"
        )

        if complexity is not None:

            if complexity >= 0.80:
                severity = "HIGH"
            elif complexity >= 0.60:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            if severity != "LOW":

                risks.append({
                    "type": "DELIVERY_COMPLEXITY",
                    "severity": severity,
                    "title": "High service delivery complexity",
                    "description": (
                        "The service intelligence indicates "
                        "elevated implementation complexity that "
                        "may increase staffing requirements, "
                        "delivery effort, dependencies, or "
                        "execution risk."
                    ),
                    "metric": {
                        "complexity": round(
                            complexity,
                            3
                        )
                    },
                    "mitigation": (
                        "Validate staffing, milestones, "
                        "dependencies, governance, and delivery "
                        "assumptions before contract commitment."
                    )
                })

        # =========================================================
        # 3. MARGIN PRESSURE
        # =========================================================

        target_margin = self._get_numeric(
            economics,
            "target_margin"
        )

        projected_margin = self._extract_projected_margin(
            economics,
            offers
        )

        if (
            target_margin is not None
            and projected_margin is not None
        ):

            margin_gap = (
                target_margin -
                projected_margin
            )

            if margin_gap >= 0.15:
                severity = "HIGH"
            elif margin_gap >= 0.05:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            if severity != "LOW":

                risks.append({
                    "type": "MARGIN_PRESSURE",
                    "severity": severity,
                    "title": "Projected margin below target",
                    "description": (
                        "The modeled offer economics indicate "
                        "that projected commercial margin may "
                        "fall below the internal target."
                    ),
                    "metric": {
                        "target_margin": round(
                            target_margin,
                            3
                        ),
                        "projected_margin": round(
                            projected_margin,
                            3
                        ),
                        "gap": round(
                            margin_gap,
                            3
                        )
                    },
                    "mitigation": (
                        "Consider scope controls, contract "
                        "term adjustments, resource "
                        "optimization, or value-based pricing."
                    )
                })

        # =========================================================
        # 4. CAPACITY RISK
        # =========================================================

        required_capacity = self._get_numeric(
            economics,
            "required_capacity"
        )

        available_capacity = self._get_numeric(
            economics,
            "capacity_available"
        )

        if (
            required_capacity is not None
            and available_capacity is not None
        ):

            if available_capacity <= 0:

                risks.append({
                    "type": "CAPACITY_CONSTRAINT",
                    "severity": "HIGH",
                    "title": "No available delivery capacity",
                    "description": (
                        "The economics model indicates that "
                        "there is currently no available "
                        "internal delivery capacity."
                    ),
                    "metric": {
                        "required_capacity": required_capacity,
                        "capacity_available": available_capacity
                    },
                    "mitigation": (
                        "Validate hiring, subcontracting, "
                        "resource allocation, or phased delivery."
                    )
                })

            elif required_capacity > available_capacity:

                utilization = (
                    required_capacity /
                    available_capacity
                )

                risks.append({
                    "type": "CAPACITY_CONSTRAINT",
                    "severity": "HIGH",
                    "title": "Insufficient delivery capacity",
                    "description": (
                        "The modeled delivery requirement "
                        "exceeds currently available internal "
                        "capacity."
                    ),
                    "metric": {
                        "required_capacity": required_capacity,
                        "capacity_available": available_capacity,
                        "utilization_ratio": round(
                            utilization,
                            3
                        )
                    },
                    "mitigation": (
                        "Validate hiring, subcontracting, "
                        "resource allocation, or delivery "
                        "phasing before committing."
                    )
                })

        # =========================================================
        # 5. COMPETITIVE PRESSURE
        # =========================================================

        competitive_pressure = self._get_numeric(
            market,
            "competitive_pressure"
        )

        competitor_count = self._get_numeric(
            market,
            "competitor_count"
        )

        if (
            competitive_pressure is not None
            and competitive_pressure >= 0.70
        ):

            risks.append({
                "type": "COMPETITIVE_PRESSURE",
                "severity": "HIGH",
                "title": "High competitive pressure",
                "description": (
                    "Available market signals indicate a "
                    "competitive environment where "
                    "differentiation and commercial positioning "
                    "may materially affect the opportunity."
                ),
                "metric": {
                    "competitive_pressure": round(
                        competitive_pressure,
                        3
                    ),
                    "competitor_count": competitor_count
                },
                "mitigation": (
                    "Differentiate through measurable "
                    "outcomes, implementation capability, "
                    "scope, contract structure, or strategic "
                    "value."
                )
            })

        # =========================================================
        # 6. MARKET VOLATILITY
        # =========================================================

        volatility = self._get_numeric(
            market,
            "market_volatility"
        )

        if volatility is not None:

            if volatility >= 0.75:
                severity = "HIGH"
            elif volatility >= 0.50:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            if severity != "LOW":

                risks.append({
                    "type": "MARKET_VOLATILITY",
                    "severity": severity,
                    "title": "Market uncertainty",
                    "description": (
                        "Market conditions may change during "
                        "the commercial cycle and affect "
                        "pricing, demand, or customer willingness "
                        "to commit."
                    ),
                    "metric": {
                        "market_volatility": round(
                            volatility,
                            3
                        )
                    },
                    "mitigation": (
                        "Consider staged commitments, "
                        "commercial review points, contract "
                        "protections, or flexible pricing "
                        "structures."
                    )
                })

        # =========================================================
        # 7. DATA COMPLETENESS
        # =========================================================

        completeness = self._get_numeric(
            market,
            "data_completeness"
        )

        if (
            completeness is not None
            and completeness < 0.60
        ):

            risks.append({
                "type": "DATA_COMPLETENESS",
                "severity": "MEDIUM",
                "title": "Limited evidence coverage",
                "description": (
                    "Some commercial intelligence is based "
                    "on incomplete or lower-confidence "
                    "information."
                ),
                "metric": {
                    "data_completeness": round(
                        completeness,
                        3
                    )
                },
                "mitigation": (
                    "Collect additional customer, market, "
                    "competitive, and internal enterprise "
                    "evidence before final commercial "
                    "commitment."
                )
            })

        # =========================================================
        # 8. OFFER STRUCTURE CHECK
        # =========================================================

        if not offers:

            risks.append({
                "type": "OFFER_GENERATION",
                "severity": "HIGH",
                "title": "No commercial offers generated",
                "description": (
                    "The optimization pipeline did not "
                    "produce a usable offer set."
                ),
                "metric": {},
                "mitigation": (
                    "Review scenario generation, optimization, "
                    "and commercial assumptions."
                )
            })


        # =========================================================
        # 10. DATA COMPLETENESS — Customer evidence missing
        # =========================================================

        customer_avail = getattr(customer, "data_availability", None)
        if customer_avail == "NOT_FOUND":
            risks.append({
                "type": "DATA_COMPLETENESS",
                "severity": "MEDIUM",
                "title": "No internal customer evidence available",
                "description": (
                    "No internal CRM record was found for this customer. "
                    "Customer strategic importance, relationship history, "
                    "and account profile cannot be confirmed from internal data. "
                    "Commercial strategy is based on service and market evidence only."
                ),
                "metric": {"customer_evidence": "NOT_FOUND"},
                "mitigation": (
                    "Obtain customer background, relationship history, and strategic "
                    "classification before final commercial commitment."
                ),
            })

        # =========================================================
        # 11. DATA COMPLETENESS — Service not in delivery catalog
        # =========================================================

        service_avail = getattr(service, "data_availability", None)
        economics_source = getattr(economics, "economics_source", None)

        if service_avail == "NOT_FOUND" or economics_source == "PARAMETRIC_BASELINE":
            risks.append({
                "type": "DATA_COMPLETENESS",
                "severity": "HIGH",
                "title": "Service not in internal delivery catalog — parametric economics applied",
                "description": (
                    "The requested service has no historical delivery evidence in the "
                    "internal catalog. Economics are based on a deterministic parametric "
                    "baseline (complexity x duration x burn rate), not verified "
                    "historical delivery cost data."
                ),
                "metric": {
                    "service_evidence": service_avail or "UNKNOWN",
                    "economics_source": economics_source or "UNKNOWN",
                },
                "mitigation": (
                    "Review delivery requirements, obtain comparable historical estimates, "
                    "and validate the parametric cost baseline before commercial commitment."
                ),
            })

        # =========================================================
        # 12. DATA COMPLETENESS — No market intelligence
        # =========================================================

        market_avail = getattr(market, "data_availability", None)
        if market_avail == "NOT_FOUND":
            risks.append({
                "type": "DATA_COMPLETENESS",
                "severity": "MEDIUM",
                "title": "No internal competitive intelligence — price positioning unvalidated",
                "description": (
                    "No internal competitive price signals were found for this service. "
                    "The commercial offer range cannot be validated against market benchmarks."
                ),
                "metric": {"market_evidence": "NOT_FOUND"},
                "mitigation": (
                    "Gather external market pricing intelligence before finalizing commercial terms."
                ),
            })

        # =========================================================
        # 9. NO-EVIDENCE FALLBACK
        # =========================================================

        if not risks:

            risks.append({
                "type": "NO_MATERIAL_RISK_DETECTED",
                "severity": "LOW",
                "title": "No material automated risk trigger",
                "description": (
                    "The currently available structured "
                    "intelligence did not trigger a material "
                    "automated risk rule."
                ),
                "metric": {},
                "mitigation": (
                    "Executive review is still required "
                    "before commercial commitment."
                )
            })

        return risks

    # =============================================================
    # HELPERS
    # =============================================================

    @staticmethod
    def _get_numeric(
        source,
        field_name
    ):

        if source is None:
            return None

        if hasattr(source, field_name):

            value = getattr(
                source,
                field_name
            )

        elif isinstance(source, dict):

            value = source.get(
                field_name
            )

        else:

            return None

        if value is None:
            return None

        try:
            return float(value)

        except (
            TypeError,
            ValueError
        ):

            return None

    # =============================================================
    # MARKET PRICE EXTRACTION
    # =============================================================

    @staticmethod
    def _extract_market_reference(market):
        """
        Extract a representative market price from the current
        market intelligence.

        Supported formats:

        1. Structured:
           {"price": 14500000}

        2. Object:
           signal.price

        3. Current HADRON demo format:
           "Competitor A: $14,500,000"

        No price is invented if parsing fails.
        """

        import re

        # --------------------------------------------------
        # Direct market reference
        # --------------------------------------------------

        direct = RiskAgent._get_numeric(
            market,
            "market_price_reference"
        )

        if direct is not None:
            return direct

        # --------------------------------------------------
        # Competitor signals
        # --------------------------------------------------

        signals = None

        if hasattr(market, "competitor_signals"):
            signals = market.competitor_signals

        elif isinstance(market, dict):
            signals = market.get(
                "competitor_signals"
            )

        if not signals:
            return None

        prices = []

        for signal in signals:

            # ==============================================
            # STRUCTURED DICTIONARY
            # ==============================================

            if isinstance(signal, dict):

                for key in (
                    "price",
                    "estimated_price",
                    "observed_price",
                    "market_price"
                ):

                    value = signal.get(key)

                    if value is not None:

                        try:
                            prices.append(
                                float(value)
                            )
                            break

                        except (
                            TypeError,
                            ValueError
                        ):
                            pass

            # ==============================================
            # PYDANTIC / OBJECT SIGNAL
            # ==============================================

            elif not isinstance(signal, str):

                for key in (
                    "price",
                    "estimated_price",
                    "observed_price",
                    "market_price"
                ):

                    if hasattr(signal, key):

                        value = getattr(
                            signal,
                            key
                        )

                        try:
                            prices.append(
                                float(value)
                            )
                            break

                        except (
                            TypeError,
                            ValueError
                        ):
                            pass

            # ==============================================
            # STRING SIGNAL
            # ==============================================

            elif isinstance(signal, str):

                # Examples:
                #
                # Competitor A: $14,500,000
                # Competitor B: $9,800,000
                # Market price: $12.7M

                matches = re.findall(
                    r'\$?\s*([\d,]+(?:\.\d+)?)\s*(M|B|K)?',
                    signal,
                    flags=re.IGNORECASE
                )

                for number, suffix in matches:

                    try:

                        value = float(
                            number.replace(
                                ",",
                                ""
                            )
                        )

                        suffix = suffix.upper()

                        if suffix == "B":
                            value *= 1_000_000_000

                        elif suffix == "M":
                            value *= 1_000_000

                        elif suffix == "K":
                            value *= 1_000

                        prices.append(
                            value
                        )

                        # We only want the first
                        # monetary value in the signal.
                        break

                    except (
                        TypeError,
                        ValueError
                    ):
                        pass

        # --------------------------------------------------
        # No usable market prices
        # --------------------------------------------------

        if not prices:
            return None

        # --------------------------------------------------
        # Representative market reference
        # --------------------------------------------------
        #
        # We use the average of the observed signals.
        #
        # Example:
        #
        # 14.5M
        #  9.8M
        # 12.7M
        #
        # reference ≈ 12.33M
        #
        # This is a calculated reference, NOT a claim that
        # every competitor charges this amount.
        # --------------------------------------------------

        return sum(prices) / len(prices)

    # =============================================================
    # PROJECTED MARGIN
    # =============================================================

    @staticmethod
    def _extract_projected_margin(
        economics,
        offers
    ):

        direct = RiskAgent._get_numeric(
            economics,
            "projected_margin"
        )

        if direct is not None:
            return direct

        margins = []

        for offer in offers or []:

            margin = RiskAgent._get_numeric(
                offer,
                "margin"
            )

            if margin is not None:
                margins.append(
                    margin
                )

        if not margins:
            return None

        return sum(margins) / len(margins)
