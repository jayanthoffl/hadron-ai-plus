from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class HadronContext:
    """
    Unified intelligence context collected from ServiceNow and
    other external intelligence sources.

    This is the contract between the Control Tower and the
    existing HADRON pricing engine.
    """

    customer: Dict[str, Any] = field(default_factory=dict)

    workforce: Dict[str, Any] = field(default_factory=dict)

    financials: Dict[str, Any] = field(default_factory=dict)

    projects: List[Dict[str, Any]] = field(default_factory=list)

    contracts: List[Dict[str, Any]] = field(default_factory=list)

    opportunities: List[Dict[str, Any]] = field(default_factory=list)

    services: List[Dict[str, Any]] = field(default_factory=list)

    incidents: List[Dict[str, Any]] = field(default_factory=list)

    requests: List[Dict[str, Any]] = field(default_factory=list)

    organizational_signals: Dict[str, Any] = field(default_factory=dict)

    source_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer": self.customer,
            "workforce": self.workforce,
            "financials": self.financials,
            "projects": self.projects,
            "contracts": self.contracts,
            "opportunities": self.opportunities,
            "services": self.services,
            "incidents": self.incidents,
            "requests": self.requests,
            "organizational_signals": self.organizational_signals,
            "source_metadata": self.source_metadata,
        }
