from dotenv import load_dotenv
load_dotenv()

from integrations.servicenow.client import ServiceNowClient


client = ServiceNowClient()

records = client.query(
    table="core_company",
    limit=5,
)

print(f"ServiceNow connection successful.")
print(f"Companies returned: {len(records)}")

for record in records:
    print({
        "sys_id": record.get("sys_id"),
        "name": record.get("name"),
    })
