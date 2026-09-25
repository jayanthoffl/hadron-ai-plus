from typing import Any, Dict, List

from domain.hadron_context import HadronContext


class ServiceNowMapper:
    """
    Converts raw ServiceNow records into the unified HADRON context.

    Keep ServiceNow-specific field names here rather than leaking
    them into the pricing engine.
    """

    @staticmethod
    def map_customer(record: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "sys_id": record.get("sys_id"),
            "name": record.get("name") or record.get("company"),
            "industry": record.get("industry"),
            "description": record.get("description"),
            "location": record.get("location"),
            "raw": record,
        }

    @staticmethod
    def map_context(
        customer: Dict[str, Any],
        workforce: List[Dict[str, Any]] = None,
        financials: Dict[str, Any] = None,
        projects: List[Dict[str, Any]] = None,
        contracts: List[Dict[str, Any]] = None,
        opportunities: List[Dict[str, Any]] = None,
        services: List[Dict[str, Any]] = None,
        incidents: List[Dict[str, Any]] = None,
        requests: List[Dict[str, Any]] = None,
    ) -> HadronContext:

        workforce = workforce or []
        projects = projects or []
        contracts = contracts or []
        opportunities = opportunities or []
        services = services or []
        incidents = incidents or []
        requests = requests or []

        workforce_summary = {
            "record_count": len(workforce),
            "records": workforce,
        }

        organizational_signals = {
            "active_projects": len(projects),
            "active_contracts": len(contracts),
            "open_opportunities": len(opportunities),
            "service_count": len(services),
            "open_incidents": len(incidents),
            "open_requests": len(requests),
        }

        return HadronContext(
            customer=customer,
            workforce=workforce_summary,
            financials=financials or {},
            projects=projects,
            contracts=contracts,
            opportunities=opportunities,
            services=services,
            incidents=incidents,
            requests=requests,
            organizational_signals=organizational_signals,
            source_metadata={
                "source": "servicenow",
                "adapter": "ServiceNowMapper",
            },
        )
