from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HadronRequest(BaseModel):
    customer_name: str
    service_product_name: str
    commercial_objective: str
    additional_context: str = ""
    record_sys_id: str = ""

    # Future document pipeline
    document_text: str = ""


class HadronIntent(BaseModel):
    """
    Structured extraction of what the ServiceNow request actually means.
    Produced by ExtractionAgent (Gemini).
    This is interpretation only — not commercial conclusions.
    """
    customer_name: str = ""
    service_name: str = ""
    service_catalog_key: str = "CUSTOM_SERVICE"   # exact catalog key or CUSTOM_SERVICE
    objective_summary: str = ""
    context_summary: str = ""
    inferred_industry: str = ""                    # tagged as inference, not fact
    estimated_complexity: Optional[float] = None     # planning estimate; not verified scope
    estimated_duration_months: Optional[int] = None  # planning estimate; not verified scope
    estimated_resource_requirements: Dict[str, int] = {}
    service_estimate_notes: str = ""
    service_estimate_confidence: float = 0.0
    key_requirements: List[str] = []
    ambiguities: List[str] = []
    extraction_confidence: float = 0.5
    extraction_notes: str = ""


class CommercialContext(BaseModel):
    """
    Deterministic commercial strategy signals derived from retrieved intelligence.
    These influence scenario construction — not the underlying delivery cost.
    """
    strategic_importance_signal: str = "UNKNOWN"   # HIGH, MEDIUM, LOW, UNKNOWN
    urgency_signal: str = "NORMAL"                 # HIGH, NORMAL, LOW
    scope_complexity: float = 0.5
    relationship_strength: str = "UNKNOWN"          # ESTABLISHED, NEW, UNKNOWN
    customer_evidence_available: bool = False
    service_evidence_available: bool = False
    market_evidence_available: bool = False
    data_completeness: float = 0.0                 # 0–1, drives confidence and risk


class Evidence(BaseModel):
    source: str
    evidence_type: str = "unknown"   # internal_evidence | model_inference | external | unknown
    statement: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: Optional[str] = None


class CustomerIntelligence(BaseModel):
    customer_name: str
    data_availability: str = "NOT_FOUND"           # FOUND | NOT_FOUND
    industry: str = ""
    revenue: float = 0
    employee_count: int = 0
    strategic_importance: str = ""
    active_projects: List[str] = []
    existing_relationship: str = ""
    known_needs: List[str] = []
    active_budget: Optional[float] = None
    capacity_pressure: Optional[float] = None
    evidence: List[Evidence] = []


class ServiceIntelligence(BaseModel):
    service_name: str
    data_availability: str = "NOT_FOUND"           # FOUND | NOT_FOUND
    description: str = ""
    scope: List[str] = []
    complexity: Optional[float] = None
    estimated_duration_months: Optional[int] = None
    resource_requirements: Dict[str, Any] = {}
    value_drivers: List[str] = []
    evidence: List[Evidence] = []


class MarketIntelligence(BaseModel):
    data_availability: str = "NOT_FOUND"           # FOUND | NOT_FOUND
    market_size_signal: str = ""
    demand_signal: str = ""
    pricing_environment: str = ""
    volatility: float = 0.5
    competitor_signals: List[str] = []
    market_reference_price: Optional[float] = None
    market_factors: List[str] = []
    evidence: List[Evidence] = []


class InternalEconomics(BaseModel):
    estimated_cost: float = 0
    resource_cost: float = 0
    infrastructure_cost: float = 0
    delivery_cost: float = 0
    minimum_viable_price: float = 0
    target_margin: float = 0.30
    capacity_available: float = 0.0
    required_capacity: Optional[float] = None
    revenue_target: Optional[float] = None
    confirmed_pipeline_value: Optional[float] = None
    pipeline_gap: Optional[float] = None
    project_budget: Optional[float] = None
    historical_deal_count: int = 0
    historical_average_deal_value: Optional[float] = None
    economics_source: str = "NOT_FOUND"            # CATALOG | PARAMETRIC_BASELINE


class Scenario(BaseModel):
    name: str
    price: float
    term_months: int
    scope_factor: float
    expected_margin: float
    strategic_value: float
    risk: float
    win_signal: float
    objective_score: float = 0


class Offer(BaseModel):
    name: str
    price: float
    term_months: int
    scope: str
    expected_margin: float
    win_signal: float = 0.0
    strategic_value: float = 0.0
    risk_score: float = 0.0
    objective_score: float = 0.0
    strategic_rationale: str
    negotiation_levers: List[str] = []
    risks: List[str] = []
    confidence: float = 0.5


class HadronResponse(BaseModel):
    executive_summary: str

    customer_intelligence: str
    market_intelligence: str
    service_intelligence: str
    internal_economics: str
    competitive_intelligence: str

    offer_set: str
    risks: str
    evidence: str
    confidence: float

    request_intent: str = ""
    commercial_context: str = ""

    run_id: str = ""
