from agents.extraction_agent import ExtractionAgent
from agents.customer_agent import CustomerAgent
from agents.service_agent import ServiceAgent
from agents.market_agent import MarketAgent
from agents.context_agent import ContextAgent
from agents.risk_agent import RiskAgent
from agents.executive_agent import ExecutiveAgent

from utils.document_parser import parse_document
from integrations.servicenow.client import ServiceNowClient

from economics.engine import EconomicsEngine

from optimization.scenarios import ScenarioGenerator
from optimization.classical import ClassicalOptimizer
from optimization.quantum import QuantumOptimizer

from offers.generator import OfferGenerator


class HadronOrchestrator:

    def __init__(self):

        # ------------------------------------------------
        # EXTRACTION  (Gemini — entry point only)
        # ------------------------------------------------

        self.extraction_agent = ExtractionAgent()

        # ------------------------------------------------
        # INTELLIGENCE RETRIEVAL  (Pure Python — no Gemini)
        # ------------------------------------------------

        self.customer_agent = CustomerAgent()
        self.service_agent = ServiceAgent()
        self.market_agent = MarketAgent()

        # ------------------------------------------------
        # COMMERCIAL CONTEXT  (Pure Python — deterministic)
        # ------------------------------------------------

        self.context_agent = ContextAgent()

        # ------------------------------------------------
        # ECONOMICS  (Pure Python — deterministic)
        # ------------------------------------------------

        self.economics = EconomicsEngine()

        # ------------------------------------------------
        # OPTIMIZATION  (Pure Python — deterministic)
        # ------------------------------------------------

        self.scenarios = ScenarioGenerator()
        self.classical = ClassicalOptimizer()
        self.quantum = QuantumOptimizer()

        # ------------------------------------------------
        # OFFER ENGINE  (Pure Python)
        # ------------------------------------------------

        self.offers = OfferGenerator()

        # ------------------------------------------------
        # RISK  (Pure Python — deterministic rules)
        # ------------------------------------------------

        self.risk_agent = RiskAgent()

        # ------------------------------------------------
        # EXECUTIVE SYNTHESIS  (Gemini — exit point only)
        # ------------------------------------------------

        self.executive = ExecutiveAgent()
    def run(self, request):

        # =================================================
        # STEP 0 — INGESTION & EXTRACTION
        # Fetch attachments from ServiceNow, parse them,
        # and use Gemini to structure the request intent.
        # =================================================

        print("[HADRON] Step 0: Ingestion & Extraction")
        
        # Ingest attachments if we have a real sys_id
        if request.record_sys_id and not request.record_sys_id.startswith("TEST-"):
            try:
                sn_client = ServiceNowClient()
                attachments = sn_client.get_attachments("x_2216687_optimu_0_pricing_request", request.record_sys_id)
                if attachments:
                    print(f"[HADRON]   Found {len(attachments)} attachments, parsing...")
                    doc_texts = []
                    for att in attachments:
                        file_name = att.get("file_name", "")
                        att_sys_id = att.get("sys_id", "")
                        print(f"[HADRON]     -> {file_name}")
                        raw_bytes = sn_client.download_attachment(att_sys_id)
                        parsed_text = parse_document(raw_bytes, file_name)
                        doc_texts.append(f"--- Document: {file_name} ---\n{parsed_text}")
                    
                    if doc_texts:
                        request.document_text = "\n\n".join(doc_texts)
            except Exception as e:
                print(f"[HADRON]   Error fetching attachments: {e}")

        intent = self.extraction_agent.extract(request)

        print(
            f"[HADRON]   customer='{intent.customer_name}' "
            f"  catalog_key='{intent.service_catalog_key}' "
            f"  extraction_confidence={intent.extraction_confidence:.0%}"
        )

        # =================================================
        # STEP 1 — CUSTOMER INTELLIGENCE
        # Pure Python lookup. NOT_FOUND is a valid state.
        # =================================================

        print("[HADRON] Step 1: Customer intelligence retrieval")
        customer = self.customer_agent.analyze(intent)
        print(f"[HADRON]   data_availability={customer.data_availability}")

        # =================================================
        # STEP 2 — SERVICE INTELLIGENCE
        # Pure Python lookup using extracted catalog key.
        # =================================================

        print("[HADRON] Step 2: Service intelligence retrieval")
        service = self.service_agent.analyze(intent)
        print(f"[HADRON]   data_availability={service.data_availability}  service='{service.service_name}'")

        # =================================================
        # STEP 3 — MARKET INTELLIGENCE
        # Pure Python lookup. NOT_FOUND is a valid state.
        # No manufactured competitor prices.
        # =================================================

        print("[HADRON] Step 3: Market intelligence retrieval")
        market = self.market_agent.analyze(intent)
        print(f"[HADRON]   data_availability={market.data_availability}")

        # =================================================
        # STEP 4 — COMMERCIAL CONTEXT
        # Deterministic derivation from retrieved intelligence.
        # Drives scenario strategy — NOT delivery cost.
        # =================================================

        print("[HADRON] Step 4: Commercial context derivation")
        context = self.context_agent.derive(intent, customer, service, market)
        print(
            f"[HADRON]   strategic={context.strategic_importance_signal} "
            f"  completeness={context.data_completeness:.0%} "
            f"  relationship={context.relationship_strength}"
        )

        # =================================================
        # STEP 5 — INTERNAL ECONOMICS
        # Fully deterministic. economics.json if matched,
        # parametric baseline if CUSTOM_SERVICE.
        # Gemini NEVER touches dollar amounts.
        # =================================================

        print("[HADRON] Step 5: Economics calculation")
        economics = self.economics.calculate(customer, service, request)
        print(
            f"[HADRON]   source={economics.economics_source} "
            f"  cost=${economics.estimated_cost:,.0f} "
            f"  MVP=${economics.minimum_viable_price:,.0f}"
        )

        # =================================================
        # STEP 6 — SCENARIO GENERATION
        # Context-aware pricing strategy.
        # Base costs remain deterministic.
        # =================================================

        print("[HADRON] Step 6: Scenario generation")
        scenarios = self.scenarios.generate(
            customer, service, market, economics, context
        )

        # =================================================
        # STEP 7 — CLASSICAL OPTIMIZATION
        # =================================================

        scenarios = self.classical.optimize(scenarios)

        # The current quantum module samples a uniform circuit without
        # encoding the pricing objective. Keep it out of the decision path
        # until it can produce a validated optimization signal.

        # =================================================
        # STEP 9 — OFFER GENERATION
        # =================================================

        print("[HADRON] Step 9: Offer generation")
        offers = self.offers.generate(
            scenarios,
            request.commercial_objective,
        )

        # =================================================
        # STEP 10 — RISK INTELLIGENCE
        # Deterministic rules including DATA_COMPLETENESS
        # checks on intelligence availability.
        # =================================================

        print("[HADRON] Step 10: Risk analysis")
        risks = self.risk_agent.analyze(
            request=request,
            customer=customer,
            service=service,
            market=market,
            economics=economics,
            offers=offers,
        )
        print(f"[HADRON]   {len(risks)} risk signal(s) identified")

        # =================================================
        # STEP 11 — EXECUTIVE SYNTHESIS
        # Gemini synthesizes all assembled evidence.
        # Does NOT invent facts or re-classify evidence.
        # =================================================

        print("[HADRON] Step 11: Executive synthesis")
        executive = self.executive.synthesize(
            request=request,
            customer=customer,
            service=service,
            market=market,
            economics=economics,
            offers=offers,
            risks=risks,
        )

        # =================================================
        # STEP 12 — FINAL RESPONSE
        # =================================================

        return {
            "executive_summary": executive.get("executive_summary", ""),

            "request_intent": intent.model_dump_json(indent=2),

            "commercial_context": context.model_dump_json(indent=2),

            "customer_intelligence": customer.model_dump_json(indent=2),

            "service_intelligence": service.model_dump_json(indent=2),

            "market_intelligence": market.model_dump_json(indent=2),

            "competitive_intelligence": executive.get("competitive_intelligence", ""),

            "internal_economics": economics.model_dump_json(indent=2),

            "offer_set": [offer.model_dump() for offer in offers],

            "risks": risks,

            "evidence": executive.get("evidence", []),

            "confidence": executive.get("confidence", 0.5),

            "synthesis_mode": executive.get("synthesis_mode", "gemini"),

            "run_id": request.record_sys_id,
        }
