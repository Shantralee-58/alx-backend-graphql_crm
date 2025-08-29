#!/usr/bin/env python3
import os
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crm.settings")
django.setup()

# GraphQL client setup
transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date 7 days ago
seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

# GraphQL query for orders in the last 7 days
query = gql("""
query getRecentOrders($date: DateTime!) {
  orders(orderDate_Gte: $date) {
    id
    customer {
      email
    }
  }
}
""")

variables = {"date": seven_days_ago}

try:
    result = client.execute(query, variable_values=variables)
    orders = result.get("orders", [])
    
    with open("/tmp/order_reminders_log.txt", "a") as f:
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - Order ID: {order_id}, Customer Email: {email}\n")
    
    print("Order reminders processed!")
except Exception as e:
    print("Error querying orders:", e)

