import os
from typing import Any, Dict, Optional

import requests


class ServiceNowClient:
    """
    Minimal ServiceNow REST client.

    The client is intentionally independent from the pricing engine.
    Its only responsibility is retrieving records from ServiceNow.
    """

    def __init__(
        self,
        instance_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 20,
    ):
        self.instance_url = (
            instance_url or os.getenv("SERVICENOW_INSTANCE_URL", "")
        ).rstrip("/")

        self.username = username or os.getenv("SERVICENOW_USERNAME")
        self.password = password or os.getenv("SERVICENOW_PASSWORD")
        self.timeout = timeout

        if not self.instance_url:
            raise ValueError("SERVICENOW_INSTANCE_URL is not configured")

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

        if self.username and self.password:
            self.session.auth = (self.username, self.password)

    def get_record(
        self,
        table: str,
        sys_id: str,
        fields: Optional[str] = None,
    ) -> Dict[str, Any]:

        params = {}

        if fields:
            params["sysparm_fields"] = fields

        url = f"{self.instance_url}/api/now/table/{table}/{sys_id}"

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        return payload.get("result", payload)

    def query(
        self,
        table: str,
        query: Optional[str] = None,
        fields: Optional[str] = None,
        limit: int = 100,
    ) -> list:

        params = {
            "sysparm_limit": limit,
        }

        if query:
            params["sysparm_query"] = query

        if fields:
            params["sysparm_fields"] = fields

        url = f"{self.instance_url}/api/now/table/{table}"

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload = response.json()

        return payload.get("result", [])

    def create_record(
        self,
        table: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        url = f"{self.instance_url}/api/now/table/{table}"

        response = self.session.post(
            url,
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload_resp = response.json()

        return payload_resp.get("result", payload_resp)

    def update_record(
        self,
        table: str,
        sys_id: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:

        url = f"{self.instance_url}/api/now/table/{table}/{sys_id}"

        response = self.session.put(
            url,
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        payload_resp = response.json()

        return payload_resp.get("result", payload_resp)

    def get_attachments(self, table_name: str, table_sys_id: str) -> list:
        """List metadata for all attachments attached to a specific record."""
        return self.query(
            table="sys_attachment",
            query=f"table_name={table_name}^table_sys_id={table_sys_id}"
        )

    def download_attachment(self, attachment_sys_id: str) -> bytes:
        """Download the actual binary content of an attachment."""
        url = f"{self.instance_url}/api/now/attachment/{attachment_sys_id}/file"
        # We must use a raw session get because the response is binary, not JSON
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.content

