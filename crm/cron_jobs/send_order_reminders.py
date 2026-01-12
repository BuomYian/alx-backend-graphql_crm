#!/usr/bin/env python
import os
import sys
import django
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup Django
sys.path.insert(0, '/home/buomyian/alx-backend-graphql_crm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')
django.setup()

# GraphQL Client Setup
transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# GraphQL Query to get orders from the last 7 days
query = gql("""
    query {
        allOrders(orderDate_Gte: "%s") {
            edges {
                node {
                    id
                    orderDate
                    customer {
                        email
                    }
                }
            }
        }
    }
""")

try:
    # Calculate date from 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()

    # Format the query with the date
    formatted_query = gql("""
        query {{
            allOrders(orderDate_Gte: "{}") {{
                edges {{
                    node {{
                        id
                        orderDate
                        customer {{
                            email
                        }}
                    }}
                }}
            }}
        }}
    """.format(seven_days_ago))

    # Execute the query
    result = client.execute(formatted_query)

    # Process results and log
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open('/tmp/order_reminders_log.txt', 'a') as log:
        orders = result.get('allOrders', {}).get('edges', [])
        for order in orders:
            node = order.get('node', {})
            order_id = node.get('id', 'N/A')
            customer_email = node.get('customer', {}).get('email', 'N/A')
            log.write(
                f'{timestamp} - Order ID: {order_id}, Customer Email: {customer_email}\n')

    print("Order reminders processed!")

except Exception as e:
    # Log errors
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('/tmp/order_reminders_log.txt', 'a') as log:
        log.write(f'{timestamp} - Error: {str(e)}\n')
    print(f"Error: {str(e)}")
