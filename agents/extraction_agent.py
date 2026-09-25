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

        try:
            response = self._client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
            )
            text = (response.text or "").strip()
            if text.startswith("```"):
                text = text.replace("```json", "").replace("```", "").strip()

            data = json.loads(text)
            return HadronIntent(**data)

        except Exception as exc:
            print(f"[ExtractionAgent] Gemini error: {exc}. Using deterministic fallback.")
            return self._deterministic_fallback(request)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, request) -> str:
        return f"""
You are the HADRON request extraction agent.

Your ONLY job is to understand and structure the inbound pricing request.

Rules:
- Do NOT produce commercial conclusions, prices, or recommendations.
- Do NOT invent facts about the customer.
- Do NOT browse the internet.
- Mark any inference clearly.

ServiceNow Pricing Request:
  Customer Name: {request.customer_name}
  Service / Product: {request.service_product_name}
  Commercial Objective: {request.commercial_objective}
  Additional Context: {request.additional_context}
"""
        if request.document_text:
            prompt += f"\nExtracted Document Content:\n{request.document_text}\n"

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
6. List key business/technical requirements extracted from the text (not invented).
7. List any ambiguities or missing information in the request.
8. Set extraction_confidence (0.0–1.0) based on how clearly the request is specified.

Return ONLY valid JSON, no markdown:
{{
  "customer_name": "...",
  "service_name": "...",
  "service_catalog_key": "...",
  "objective_summary": "...",
  "context_summary": "...",
  "inferred_industry": "...",
  "key_requirements": ["..."],
  "ambiguities": ["..."],
  "extraction_confidence": 0.0,
  "extraction_notes": "..."
}}
"""

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

        return HadronIntent(
            customer_name=(request.customer_name or "").strip(),
            service_name=raw_service,
            service_catalog_key=catalog_key,
            objective_summary=(request.commercial_objective or "").strip(),
            context_summary=(request.additional_context or "").strip(),
            inferred_industry="",
            key_requirements=[],
            ambiguities=["Gemini extraction unavailable — intent derived from raw request fields only."],
            extraction_confidence=0.60,
            extraction_notes="Deterministic fallback used due to Gemini unavailability.",
        )
