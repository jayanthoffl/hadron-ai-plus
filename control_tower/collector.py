from typing import Any, Dict, Optional

from integrations.servicenow.client import ServiceNowClient
from integrations.servicenow.mapper import ServiceNowMapper


class ControlTowerCollector:
    """
    Coordinates collection of enterprise intelligence from ServiceNow.

    This layer decides WHAT information HADRON needs.
    The ServiceNow client decides HOW to retrieve it.
    """

    def __init__(self, client: Optional[ServiceNowClient] = None):
        self.client = client or ServiceNowClient()
        self.mapper = ServiceNowMapper()

    def collect_customer_context(
        self,
        customer_sys_id: str,
    ):
        customer = self.client.get_record(
            table="core_company",
            sys_id=customer_sys_id,
        )

        return self.mapper.map_context(
            customer=self.mapper.map_customer(customer)
        )
