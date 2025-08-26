import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """Logs a heartbeat message every 5 minutes and checks GraphQL endpoint."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_message = f"{timestamp} CRM is alive\n"

    # Append heartbeat to log file
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(log_message)

    # Optional: check GraphQL endpoint using gql
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    try:
        query = gql("{ hello }")
        result = client.execute(query)
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL endpoint is responsive: {result}\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL endpoint error: {e}\n")

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def update_low_stock():
    """Runs the UpdateLowStockProducts mutation every 12 hours."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # GraphQL setup
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Mutation query
    mutation = gql("""
    mutation {
      updateLowStockProducts {
        message
        updatedProducts {
          id
          name
          stock
        }
      }
    }
    """)

    try:
        result = client.execute(mutation)
        updated = result['updateLowStockProducts']['updatedProducts']

        # Log updates
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - {result['updateLowStockProducts']['message']}\n")
            for prod in updated:
                f.write(f"Product: {prod['name']}, New Stock: {prod['stock']}\n")

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - ERROR executing mutation: {e}\n")
