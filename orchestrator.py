from agents.customer_agent import CustomerAgent
from agents.service_agent import ServiceAgent
from agents.market_agent import MarketAgent
from agents.risk_agent import RiskAgent
from agents.executive_agent import ExecutiveAgent

from economics.engine import EconomicsEngine

from optimization.scenarios import ScenarioGenerator
from optimization.classical import ClassicalOptimizer
from optimization.quantum import QuantumOptimizer

from offers.generator import OfferGenerator


class HadronOrchestrator:

    def __init__(self):

        # ------------------------------------------------
        # INTELLIGENCE AGENTS
        # ------------------------------------------------

        self.customer_agent = CustomerAgent()
        self.service_agent = ServiceAgent()
        self.market_agent = MarketAgent()
        self.risk_agent = RiskAgent()

        # ------------------------------------------------
        # ECONOMICS
        # ------------------------------------------------

        self.economics = EconomicsEngine()

        # ------------------------------------------------
        # OPTIMIZATION
        # ------------------------------------------------

        self.scenarios = ScenarioGenerator()
        self.classical = ClassicalOptimizer()
        self.quantum = QuantumOptimizer()

        # ------------------------------------------------
        # OFFER ENGINE
        # ------------------------------------------------

        self.offers = OfferGenerator()

        # ------------------------------------------------
        # EXECUTIVE SYNTHESIS
        # ------------------------------------------------

        self.executive = ExecutiveAgent()

    def run(self, request):

        # =================================================
        # 1. CUSTOMER INTELLIGENCE
        # =================================================

        customer = self.customer_agent.analyze(
            request.customer_name
        )

        # =================================================
        # 2. SERVICE INTELLIGENCE
        # =================================================

        service = self.service_agent.analyze(
            request.service_product_name
        )

        # =================================================
        # 3. MARKET / COMPETITIVE INTELLIGENCE
        # =================================================

        market = self.market_agent.analyze(
            request.service_product_name
        )

        # =================================================
        # 4. INTERNAL ECONOMICS
        # =================================================

        economics = self.economics.calculate(
            customer,
            service
        )

        # =================================================
        # 5. SCENARIO GENERATION
        # =================================================

        scenarios = self.scenarios.generate(
            customer,
            service,
            market,
            economics
        )

        # =================================================
        # 6. CLASSICAL OPTIMIZATION
        # =================================================

        scenarios = self.classical.optimize(
            scenarios
        )

        # =================================================
        # 7. QUANTUM EXPLORATION
        # =================================================

        scenarios = self.quantum.optimize(
            scenarios
        )

        # =================================================
        # 8. OFFER GENERATION
        # =================================================

        offers = self.offers.generate(
            scenarios,
            request.commercial_objective
        )

        # =================================================
        # 9. RISK INTELLIGENCE
        # =================================================

        risks = self.risk_agent.analyze(
            request=request,
            customer=customer,
            service=service,
            market=market,
            economics=economics,
            offers=offers
        )

        # =================================================
        # 10. EXECUTIVE SYNTHESIS
        # =================================================

        executive = self.executive.synthesize(
            request=request,
            customer=customer,
            service=service,
            market=market,
            economics=economics,
            offers=offers,
            risks=risks
        )

        # =================================================
        # 11. FINAL SERVICE CONTRACT
        # =================================================

        return {
            # ------------------------------------------------
            # EXECUTIVE VIEW
            # ------------------------------------------------

            "executive_summary": executive.get(
                "executive_summary",
                ""
            ),

            # ------------------------------------------------
            # CUSTOMER
            # ------------------------------------------------

            "customer_intelligence": customer.model_dump_json(
                indent=2
            ),

            # ------------------------------------------------
            # SERVICE
            # ------------------------------------------------

            "service_intelligence": service.model_dump_json(
                indent=2
            ),

            # ------------------------------------------------
            # MARKET
            # ------------------------------------------------

            "market_intelligence": market.model_dump_json(
                indent=2
            ),

            "competitive_intelligence": executive.get(
                "competitive_intelligence",
                ""
            ),

            # ------------------------------------------------
            # INTERNAL ECONOMICS
            # ------------------------------------------------

            "internal_economics": economics.model_dump_json(
                indent=2
            ),

            # ------------------------------------------------
            # OFFERS
            # ------------------------------------------------

            "offer_set": [
                offer.model_dump()
                for offer in offers
            ],

            # ------------------------------------------------
            # RISKS
            # ------------------------------------------------

            "risks": risks,

            # ------------------------------------------------
            # EXECUTIVE EVIDENCE
            # ------------------------------------------------

            "evidence": executive.get(
                "evidence",
                []
            ),

            # ------------------------------------------------
            # CONFIDENCE
            # ------------------------------------------------

            "confidence": executive.get(
                "confidence",
                0.5
            ),

            # ------------------------------------------------
            # TRACEABILITY
            # ------------------------------------------------

            "run_id": request.record_sys_id
        }
