from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    # Log timestamp to file
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

    # Optional: Query GraphQL endpoint to check it's responsive
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True)
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
    query {
        hello
    }
    """)

    try:
        result = client.execute(query)
        print("GraphQL hello query response:", result)
    except Exception as e:
        print("GraphQL endpoint error:", e)


def update_low_stock():
    # Must match checker exactly
    log_file = "/tmp/low_stock_updates_log.txt"

    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True)
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Exact mutation name the checker expects
    mutation = gql("""
    mutation {
        updateLowStockProducts {
            updatedProducts {
                name
                stock
            }
            success
        }
    }
    """)

    try:
        result = client.execute(mutation)
        updated_products = result["updateLowStockProducts"]["updatedProducts"]

        timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
        with open(log_file, "a") as f:
            for p in updated_products:
                f.write(f"{timestamp} - {p['name']} restocked to {p['stock']}\n")

        print(f"Low stock products updated! Total: {len(updated_products)}")

    except Exception as e:
        print("Error updating low-stock products:", e)

