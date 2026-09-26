"""
ExtractionAgent — Gemini-powered structured request understanding.

This is the ONLY place Gemini runs before the executive synthesis step.
Its job: parse the raw ServiceNow request into a clean HadronIntent.

It does NOT:
  - Produce commercial conclusions
  - Invent customer facts
  - Generate prices or economics
  - Browse the internet

It DOES:
  - Normalize customer name
  - Semantically match the requested service to the internal catalog
  - Summarize the objective and context
  - Identify key requirements and ambiguities
  - Infer industry (tagged explicitly as inference)
"""

import json
import os
import re
from pathlib import Path

from google import genai
from schemas import HadronIntent

_SERVICES_FILE = Path(__file__).parent.parent / "data" / "services.json"


class ExtractionAgent:

    def __init__(self):
        with open(_SERVICES_FILE, "r", encoding="utf-8") as f:
            self._catalog_keys = list(json.load(f).keys())

        api_key = os.environ.get("GEMINI_API_KEY", "")
        self._client = genai.Client(api_key=api_key) if api_key else None

    def extract(self, request) -> HadronIntent:
        """
        Convert a raw HadronRequest into a structured HadronIntent.
        Falls back to a deterministic baseline on any Gemini error.
        """
        if self._client is None:
            return self._deterministic_fallback(request)

        prompt = self._build_prompt(request)

        from gemini_pool import gemini_key_pool

        for model_name in ["gemini-3.8-flash", "gemini-flash-latest"]:
            try:
                response = gemini_key_pool.execute_with_failover(
                    lambda client: client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                )
                text = (response.text or "").strip()
                json_match = re.search(r"\{.*\}", text, re.DOTALL)
                if json_match:
                    text = json_match.group(0)

                data = json.loads(text)
                return HadronIntent(**data)
            except Exception as exc:
                print(f"[ExtractionAgent] {model_name} error: {exc}.")
                continue

        print("[ExtractionAgent] All Gemini models unavailable. Using deterministic fallback.")
        return self._deterministic_fallback(request)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, request) -> str:
        prompt = f"""
You are the HADRON request extraction agent.

Your ONLY job is to understand and structure the inbound pricing request.

Rules:
- Do NOT produce commercial conclusions, prices, or recommendations.
- Do NOT invent facts about the customer.
- Do NOT browse the internet.
- Mark any inference clearly.
- Do not treat missing scope, staffing, or duration as known facts.
- For an unmatched service (CUSTOM_SERVICE), act as an Enterprise Solution Architect: provide a realistic provisional delivery plan based on the client requirements. Estimate complexity (0.1 to 1.0, typically 0.65–0.85 for enterprise systems), duration (months, typically 6–9 months), and team composition using only these Hadron GBS delivery roles:
  * Solution Architect
  * AI / ML Engineer
  * Quantum Algorithm Specialist
  * Cybersecurity Specialist
  * ServiceNow Developer
  * ServiceNow Technical Architect
  * Data Engineer
  * Project Manager
  * Business Analyst
  * QA / Test Automation Engineer
  * Delivery Lead
- Provide these estimates in estimated_complexity, estimated_duration_months, and estimated_resource_requirements so downstream delivery economics can be calculated. Summarize the delivery rationale in service_estimate_notes.

ServiceNow Pricing Request:
  Customer Name: {request.customer_name}
  Service / Product: {request.service_product_name}
  Commercial Objective: {request.commercial_objective}
  Additional Context: {request.additional_context}
"""
        if request.document_text:
            prompt += f"\nExtracted Document Content:\n{request.document_text[:30000]}\n"

        prompt += f"""
Internal service catalog keys:
{json.dumps(self._catalog_keys, indent=2)}

Tasks:
1. Normalize the customer name (fix spacing/capitalization only).
2. If the requested service semantically matches one catalog key, output that EXACT key.
   If it does not match, output "CUSTOM_SERVICE".
3. Write a 1-sentence objective summary.
4. Write a 1–2 sentence context/requirements summary.
5. Infer the industry from available context only. Explicitly mark as inference.
6. List key business/technical requirements extracted from the text.
7. List any ambiguities or missing information in the request.
8. If CUSTOM_SERVICE, supply the estimated_complexity (0.1-1.0), estimated_duration_months (integer), and estimated_resource_requirements dict (role -> headcount).
9. Set extraction_confidence (0.0–1.0) based on how clearly the request is specified.

Return ONLY valid JSON, no markdown:
{{
  "customer_name": "...",
  "service_name": "...",
  "service_catalog_key": "...",
  "objective_summary": "...",
  "context_summary": "...",
  "inferred_industry": "...",
  "estimated_complexity": 0.75,
  "estimated_duration_months": 6,
  "estimated_resource_requirements": {{"Solution Architect": 1, "AI / ML Engineer": 2, "Cybersecurity Specialist": 1, "ServiceNow Developer": 2, "Project Manager": 1, "QA / Test Automation Engineer": 1}},
  "service_estimate_notes": "...",
  "service_estimate_confidence": 0.85,
  "key_requirements": ["..."],
  "ambiguities": ["..."],
  "extraction_confidence": 0.80,
  "extraction_notes": "..."
}}
"""
        return prompt

    def _deterministic_fallback(self, request) -> HadronIntent:
        """
        If Gemini is unavailable, build a best-effort intent from raw fields.
        Attempt exact catalog key match first.
        """
        raw_service = (request.service_product_name or "").strip()
        catalog_key = "CUSTOM_SERVICE"

        # Exact match first
        if raw_service in self._catalog_keys:
            catalog_key = raw_service
        else:
            # Case-insensitive match
            for key in self._catalog_keys:
                if key.lower() == raw_service.lower():
                    catalog_key = key
                    break

        is_custom = (catalog_key == "CUSTOM_SERVICE")
        default_resources = (
            {
                "Solution Architect": 1,
                "AI / ML Engineer": 2,
                "Cybersecurity Specialist": 1,
                "ServiceNow Developer": 2,
                "Project Manager": 1,
                "QA / Test Automation Engineer": 1
            }
            if is_custom else {}
        )

        return HadronIntent(
            customer_name=(request.customer_name or "").strip(),
            service_name=raw_service,
            service_catalog_key=catalog_key,
            objective_summary=(request.commercial_objective or "").strip(),
            context_summary=(request.additional_context or "").strip(),
            inferred_industry="",
            estimated_complexity=0.75 if is_custom else None,
            estimated_duration_months=6 if is_custom else None,
            estimated_resource_requirements=default_resources,
            service_estimate_notes="Provisional enterprise baseline: 6-month delivery pod with 8 billable FTEs." if is_custom else "",
            service_estimate_confidence=0.75 if is_custom else 0.0,
            key_requirements=[
                "Enterprise integration and workflow orchestration",
                "Automated compliance and policy enforcement",
                "Production deployment and technical handover"
            ] if is_custom else [],
            ambiguities=["Gemini extraction unavailable — intent derived from raw request fields only."],
            extraction_confidence=0.75,
            extraction_notes="Deterministic fallback used due to Gemini unavailability.",
        )
