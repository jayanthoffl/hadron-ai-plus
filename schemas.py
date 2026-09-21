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


class Evidence(BaseModel):
    source: str
    statement: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    timestamp: Optional[str] = None


class CustomerIntelligence(BaseModel):
    customer_name: str
    industry: str = ""
    revenue: float = 0
    employee_count: int = 0
    strategic_importance: str = ""
    active_projects: List[str] = []
    existing_relationship: str = ""
    known_needs: List[str] = []
    evidence: List[Evidence] = []


class ServiceIntelligence(BaseModel):
    service_name: str
    description: str = ""
    scope: List[str] = []
    complexity: float = 0.5
    estimated_duration_months: int = 12
    resource_requirements: Dict[str, Any] = {}
    value_drivers: List[str] = []
    evidence: List[Evidence] = []


class MarketIntelligence(BaseModel):
    market_size_signal: str = ""
    demand_signal: str = ""
    pricing_environment: str = ""
    volatility: float = 0.5
    competitor_signals: List[str] = []
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

    run_id: str = ""