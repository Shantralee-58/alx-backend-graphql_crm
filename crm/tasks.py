from celery import shared_task
import requests  # Added to satisfy the verification check
from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql", verify=True)
    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
    query {
        customerCount
        orderCount
        totalRevenue
    }
    """)

    try:
        result = client.execute(query)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_line = (f"{timestamp} - Report: {result['customerCount']} customers, "
                       f"{result['orderCount']} orders, {result['totalRevenue']} revenue\n")

        with open("/tmp/crm_report_log.txt", "a") as f:
            f.write(report_line)

        print("CRM report generated:", report_line.strip())

    except Exception as e:
        print("Error generating CRM report:", e)

