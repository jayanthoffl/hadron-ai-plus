"""
gemini_pool.py — Multi-Key Failover and Quota Pooling for Google Gemini.

Supports defining multiple API keys in GEMINI_API_KEYS (comma, space, or newline-separated).
Automatically rotates to the next available key upon encountering:
  - 429 RESOURCE_EXHAUSTED (Rate limit or daily quota)
  - 400 INVALID_ARGUMENT (Invalid key)
  - 403 PERMISSION_DENIED
  - 503 UNAVAILABLE (Temporary demand spike)
"""

import os
import re
import threading
from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiKeyPool:
    def __init__(self):
        self._lock = threading.Lock()
        self._keys = []
        self._current_idx = 0
        self.reload_keys()

    def reload_keys(self):
        with self._lock:
            raw = os.getenv("GEMINI_API_KEYS") or os.getenv("GEMINI_API_KEY", "")
            # Split on commas, whitespace, or newlines
            keys = [k.strip() for k in re.split(r"[\s,\n]+", raw) if k.strip()]
            # Preserve order and deduplicate
            seen = set()
            self._keys = [k for k in keys if not (k in seen or seen.add(k))]
            self._current_idx = 0

    @property
    def keys(self):
        return list(self._keys)

    def get_current_key(self) -> str:
        with self._lock:
            if not self._keys:
                return ""
            return self._keys[self._current_idx % len(self._keys)]

    def rotate(self, failed_key: str = None) -> str:
        with self._lock:
            if not self._keys:
                return ""
            # If the failed key matches the current key, advance
            if failed_key and failed_key in self._keys:
                idx = self._keys.index(failed_key)
                if idx == (self._current_idx % len(self._keys)):
                    self._current_idx = (self._current_idx + 1) % len(self._keys)
            else:
                self._current_idx = (self._current_idx + 1) % len(self._keys)

            new_key = self._keys[self._current_idx % len(self._keys)]
            print(f"[HADRON KeyPool] Rotated to key ...{new_key[-6:]} (Pool size: {len(self._keys)})")
            return new_key

    def get_client(self, api_key: str = None) -> genai.Client:
        key = api_key or self.get_current_key()
        if not key:
            raise ValueError("No Gemini API keys configured in GEMINI_API_KEYS or GEMINI_API_KEY.")
        return genai.Client(api_key=key)

    def execute_with_failover(self, call_fn, max_key_rotations: int = None):
        """
        Executes call_fn(client) with automatic key failover on 429, 400, 403, 503 errors.
        Cycles through keys in the pool up to len(keys) times.
        """
        if not self._keys:
            raise ValueError("No Gemini API keys available in pool.")

        attempts_left = max_key_rotations or len(self._keys)
        last_error = None

        while attempts_left > 0:
            current_key = self.get_current_key()
            try:
                client = self.get_client(current_key)
                return call_fn(client)
            except Exception as exc:
                err_str = str(exc)
                last_error = exc

                is_quota = "429" in err_str or "RESOURCE_EXHAUSTED" in err_str
                is_auth = "400" in err_str or "API_KEY_INVALID" in err_str or "403" in err_str
                is_overload = "503" in err_str or "UNAVAILABLE" in err_str

                if is_quota or is_auth or is_overload:
                    reason = (
                        "Quota exhausted (429)"
                        if is_quota
                        else ("Auth invalid (400)" if is_auth else "High demand (503)")
                    )
                    print(f"[HADRON KeyPool] Key ...{current_key[-6:]} failed: {reason}. Switching to next key...")
                    self.rotate(failed_key=current_key)
                    attempts_left -= 1
                    if attempts_left > 0:
                        continue
                raise last_error

        if last_error:
            raise last_error


gemini_key_pool = GeminiKeyPool()
