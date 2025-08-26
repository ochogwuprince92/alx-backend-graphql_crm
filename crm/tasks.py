from datetime import datetime
import requests
from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    """Generates weekly CRM report via GraphQL."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    query = gql("""
    {
      totalCustomers: allCustomers {
        totalCount
      }
      totalOrders: allOrders {
        totalCount
        totalRevenue: totalAmount
      }
    }
    """)

    try:
        result = client.execute(query)
        customers = result.get("totalCustomers", {}).get("totalCount", 0)
        orders = result.get("totalOrders", {}).get("totalCount", 0)
        revenue = result.get("totalOrders", {}).get("totalRevenue", 0)

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{timestamp} - Report: {customers} customers, {orders} orders, {revenue} revenue\n")

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(f"{timestamp} - ERROR generating report: {e}\n")
