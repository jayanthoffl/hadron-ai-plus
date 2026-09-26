"""
Similarity Engine — Pure Python & Mathematical Modeling.
No Gemini. Zero API cost.

Uses:
1. TF-IDF vectorization & Cosine Similarity on deal scope and objectives.
2. Jaccard Similarity on tokenized terminology.
3. Customer & vertical affinity weighting.

Finds the Top-K historical deals matching the incoming request from ServiceNow,
calculates statistical price benchmarks (min, max, median, win-rate),
and compiles a compact evidence pack for Gemini commercial reasoning.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_DATA_DIR = Path(__file__).parent.parent / "data"
_DEALS_FILE = _DATA_DIR / "historical_deals.json"


class SimilarityEngine:

    def __init__(self, deals_file: Optional[Path] = None):
        self.deals_file = deals_file or _DEALS_FILE
        self._load_deals()

    def _load_deals(self):
        try:
            with open(self.deals_file, "r", encoding="utf-8") as f:
                self.deals = json.load(f)
        except (OSError, json.JSONDecodeError):
            self.deals = []

        # Prepare text representations for vectorization
        self.documents = []
        for deal in self.deals:
            doc = (
                f"{deal.get('customer_name', '')} "
                f"{deal.get('service_name', '')} "
                f"{deal.get('outcome', '')} "
                f"{deal.get('delivery_performance', '')}"
            )
            self.documents.append(doc.lower())

        if self.documents:
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            self.tfidf_matrix = self.vectorizer.fit_transform(self.documents)
        else:
            self.vectorizer = None
            self.tfidf_matrix = None

    @staticmethod
    def _jaccard_similarity(text_a: str, text_b: str) -> float:
        """Token-level Jaccard similarity between two texts."""
        set_a = set(re.findall(r"\w+", (text_a or "").lower()))
        set_b = set(re.findall(r"\w+", (text_b or "").lower()))
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        return intersection / float(union) if union else 0.0

    def find_similar_deals(
        self,
        customer_name: str,
        service_name: str,
        commercial_objective: str = "",
        additional_context: str = "",
        top_k: int = 4
    ) -> Dict[str, Any]:
        """
        Find Top-K similar deals and compute comparable pricing envelope.
        """
        if not self.deals or self.vectorizer is None:
            return {
                "top_deals": [],
                "count": 0,
                "median_price": None,
                "price_range": (None, None),
                "avg_margin": None,
                "win_rate": None,
                "evidence_gist": "No historical deals database available for precedent search."
            }

        # Build query representation
        query_text = f"{customer_name} {service_name} {commercial_objective} {additional_context}".lower().strip()
        query_vec = self.vectorizer.transform([query_text])
        
        # 1. Cosine similarity via TF-IDF
        cosine_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # 2. Score combining Cosine, Jaccard, and Customer Affinity
        scored_deals = []
        cust_clean = (customer_name or "").strip().lower()

        for idx, deal in enumerate(self.deals):
            doc_text = self.documents[idx]
            cos_score = float(cosine_scores[idx])
            jaccard_score = self._jaccard_similarity(query_text, doc_text)

            deal_cust = (deal.get("customer_name") or "").strip().lower()
            customer_match = 1.0 if deal_cust and (deal_cust in cust_clean or cust_clean in deal_cust) else 0.0

            # Composite similarity score (0.0 to 1.0)
            composite_score = round(
                (0.50 * cos_score) + (0.25 * jaccard_score) + (0.25 * customer_match),
                4
            )

            scored_deals.append({
                "deal": deal,
                "similarity_score": composite_score,
                "cosine": round(cos_score, 4),
                "jaccard": round(jaccard_score, 4)
            })

        # Sort by similarity descending
        scored_deals.sort(key=lambda x: x["similarity_score"], reverse=True)
        top_matches = scored_deals[:top_k]

        # Extract comparable metrics
        prices = [d["deal"].get("deal_value", 0) for d in top_matches if d["deal"].get("deal_value")]
        margins = [d["deal"].get("margin", 0) for d in top_matches if d["deal"].get("margin") is not None]
        wins = [1 for d in top_matches if d["deal"].get("outcome") == "WON"]

        median_price = float(np.median(prices)) if prices else None
        min_price = float(min(prices)) if prices else None
        max_price = float(max(prices)) if prices else None
        avg_margin = float(np.mean(margins)) if margins else None
        win_rate = float(len(wins) / len(top_matches)) if top_matches else None

        # Build compact GIST for Gemini
        gist_lines = []
        for idx, match in enumerate(top_matches, start=1):
            d = match["deal"]
            gist_lines.append(
                f"{idx}. {d.get('deal_id', 'DEAL')}: {d.get('customer_name')} — {d.get('service_name')} "
                f"| Price: ${d.get('deal_value', 0):,.0f} | Margin: {d.get('margin', 0):.1%} "
                f"| Outcome: {d.get('outcome')} | Similarity: {match['similarity_score']:.0%}"
            )

        evidence_gist = "\n".join(gist_lines) if gist_lines else "No matching historical precedent found."

        return {
            "top_deals": top_matches,
            "count": len(top_matches),
            "median_price": median_price,
            "min_price": min_price,
            "max_price": max_price,
            "avg_margin": avg_margin,
            "win_rate": win_rate,
            "evidence_gist": evidence_gist
        }
