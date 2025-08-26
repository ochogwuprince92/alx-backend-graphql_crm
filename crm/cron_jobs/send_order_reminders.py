#!/usr/bin/env python3
"""
Script to send reminders for orders placed in the last 7 days via GraphQL.
"""

import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Timestamp
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# GraphQL transport setup
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Define GraphQL query
query = gql("""
query RecentOrders($startDate: DateTime!) {
  orders(filter: { orderDate_Gte: $startDate }) {
    id
    customer {
      email
    }
    orderDate
  }
}
""")

# Calculate date 7 days ago
seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat()

# Execute query
params = {"startDate": seven_days_ago}
result = client.execute(query, variable_values=params)

# Log reminders
with open("/tmp/order_reminders_log.txt", "a") as f:
    for order in result.get("orders", []):
        order_id = order["id"]
        email = order["customer"]["email"]
        log_line = f"{timestamp}: Order ID {order_id}, Customer Email: {email}\n"
        f.write(log_line)

print("Order reminders processed!")
