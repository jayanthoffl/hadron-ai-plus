import time
import random

import google.generativeai as genai

from config import (
    GEMINI_MODEL,
    GEMINI_FALLBACK_MODELS,
)


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class GeminiClient:
    """
    Resilient Gemini client for HADRON.

    Responsibilities:
    - configure Gemini
    - call the primary model
    - retry transient failures
    - fail over to secondary models
    - return the generated text
    """

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Gemini API key is required.")

        genai.configure(api_key=api_key)

        self.models = [
            GEMINI_MODEL,
            *GEMINI_FALLBACK_MODELS,
        ]

    def generate(
        self,
        prompt,
        max_retries_per_model=2,
        initial_delay=1.5,
    ):
        last_error = None

        for model_name in self.models:
            print(f"[HADRON] Attempting Gemini model: {model_name}")

            for attempt in range(max_retries_per_model + 1):
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)

                    if not response:
                        raise RuntimeError(
                            f"Gemini returned an empty response from {model_name}"
                        )

                    text = getattr(response, "text", None)

                    if not text:
                        raise RuntimeError(
                            f"Gemini returned no text from {model_name}"
                        )

                    print(
                        f"[HADRON] Gemini success: "
                        f"{model_name}, attempt={attempt + 1}"
                    )

                    return {
                        "model": model_name,
                        "text": text,
                        "attempt": attempt + 1,
                    }

                except Exception as exc:
                    last_error = exc

                    status_code = self._extract_status_code(exc)
                    retryable = (
                        status_code in RETRYABLE_STATUS_CODES
                        or self._looks_transient(exc)
                    )

                    print(
                        f"[HADRON] Gemini error: "
                        f"model={model_name}, "
                        f"attempt={attempt + 1}, "
                        f"retryable={retryable}, "
                        f"error={exc}"
                    )

                    if not retryable:
                        break

                    if attempt >= max_retries_per_model:
                        break

                    delay = initial_delay * (2 ** attempt)
                    delay += random.uniform(0, 0.5)

                    print(
                        f"[HADRON] Retrying {model_name} "
                        f"in {delay:.2f}s..."
                    )

                    time.sleep(delay)

            print(
                f"[HADRON] Model exhausted: {model_name}. "
                f"Trying next model."
            )

        raise RuntimeError(
            "All configured Gemini models failed. "
            f"Last error: {last_error}"
        )

    @staticmethod
    def _extract_status_code(error):
        """
        Best-effort extraction of an HTTP status code
        from Google SDK exceptions.
        """
        code = getattr(error, "code", None)
        if isinstance(code, int):
            return code

        response = getattr(error, "response", None)
        if response is not None:
            response_code = getattr(response, "status_code", None)
            if isinstance(response_code, int):
                return response_code

        return None

    @staticmethod
    def _looks_transient(error):
        """
        Some Google SDK errors expose the HTTP status
        only through their message.
        """
        message = str(error).lower()
        transient_terms = [
            "503",
            "unavailable",
            "temporarily unavailable",
            "high demand",
            "overloaded",
            "429",
            "resource exhausted",
            "timeout",
            "timed out",
            "internal server error",
            "bad gateway",
            "gateway timeout",
        ]
        return any(term in message for term in transient_terms)
