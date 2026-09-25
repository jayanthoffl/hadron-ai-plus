from dotenv import load_dotenv
load_dotenv()
from integrations.servicenow.client import ServiceNowClient

client = ServiceNowClient()
TABLE = "x_2216687_optimu_0_pricing_request"
try:
    records = client.query(table=TABLE, limit=1)
    print("RECORD:")
    print(records[0] if records else "NO RECORDS")
except Exception as e:
    print(f"Error: {e}")
