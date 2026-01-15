from celery import shared_task
from django.utils import timezone
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report summarizing:
    - Total number of customers
    - Total number of orders
    - Total revenue (sum of total_amount from orders)

    Logs the report to /tmp/crm_report_log.txt with timestamp.
    """
    now = timezone.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')

    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # GraphQL query to fetch report data
        query = gql("""
            {
                allCustomers {
                    totalCount
                }
                allOrders {
                    totalCount
                    edges {
                        node {
                            totalAmount
                        }
                    }
                }
            }
        """)

        result = client.execute(query)

        # Extract data from the result
        total_customers = result.get('allCustomers', {}).get('totalCount', 0)
        orders_data = result.get('allOrders', {})
        total_orders = orders_data.get('totalCount', 0)

        # Calculate total revenue
        total_revenue = 0
        if orders_data.get('edges'):
            for edge in orders_data['edges']:
                node = edge.get('node', {})
                total_amount = node.get('totalAmount', 0)
                if total_amount:
                    try:
                        total_revenue += float(total_amount)
                    except (ValueError, TypeError):
                        pass

        # Format the report message
        report_message = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n"

        # Log to file
        try:
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(report_message)
        except Exception as e:
            print(f'Error writing to CRM report log: {str(e)}')
            return {'success': False, 'error': str(e)}

        return {
            'success': True,
            'customers': total_customers,
            'orders': total_orders,
            'revenue': total_revenue
        }

    except Exception as e:
        error_message = f"{timestamp} - Error generating report: {str(e)}\n"
        try:
            with open('/tmp/crm_report_log.txt', 'a') as log_file:
                log_file.write(error_message)
        except Exception as write_error:
            print(f'Error writing to CRM report log: {str(write_error)}')

        return {'success': False, 'error': str(e)}
