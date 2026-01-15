from datetime import datetime
from django.utils import timezone
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to confirm the CRM application's health.
    Also queries the GraphQL hello field to verify the endpoint is responsive.
    """
    # Format the current timestamp as DD/MM/YYYY-HH:MM:SS
    now = timezone.now()
    timestamp = now.strftime('%d/%m/%Y-%H:%M:%S')

    # Prepare the heartbeat message
    message = f'{timestamp} CRM is alive'

    # Try to verify GraphQL endpoint is responsive
    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("""
            {
                hello
            }
        """)

        result = client.execute(query)
        if result and 'hello' in result:
            message += ' - GraphQL endpoint responsive'
    except Exception as e:
        message += f' - GraphQL endpoint check failed: {str(e)}'

    # Log the message to the heartbeat log file
    try:
        with open('/tmp/crm_heartbeat_log.txt', 'a') as log_file:
            log_file.write(message + '\n')
    except Exception as e:
        print(f'Error writing to heartbeat log: {str(e)}')


def update_low_stock():
    """
    Executes the UpdateLowStockProducts GraphQL mutation every 12 hours.
    Updates products with stock < 10 by incrementing stock by 10.
    Logs updated product names and new stock levels to /tmp/low_stock_updates_log.txt.
    """
    now = timezone.now()
    timestamp = now.strftime('%d/%m/%Y-%H:%M:%S')

    try:
        transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
        client = Client(transport=transport, fetch_schema_from_transport=False)

        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        id
                        name
                        stock
                    }
                    updatedCount
                    message
                    success
                }
            }
        """)

        result = client.execute(mutation)

        if result and 'updateLowStockProducts' in result:
            mutation_result = result['updateLowStockProducts']
            success = mutation_result.get('success', False)
            updated_count = mutation_result.get('updatedCount', 0)
            updated_products = mutation_result.get('updatedProducts', [])

            log_message = f"{timestamp} - Stock update executed\n"
            log_message += f"  Success: {success}\n"
            log_message += f"  Updated count: {updated_count}\n"

            if updated_products:
                log_message += "  Updated products:\n"
                for product in updated_products:
                    product_name = product.get('name', 'Unknown')
                    product_stock = product.get('stock', 'N/A')
                    log_message += f"    - {product_name}: new stock level = {product_stock}\n"

            # Log the update to file
            try:
                with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                    log_file.write(log_message)
            except Exception as e:
                print(f'Error writing to low stock updates log: {str(e)}')
        else:
            error_message = f"{timestamp} - Error: No response from mutation\n"
            try:
                with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                    log_file.write(error_message)
            except Exception as e:
                print(f'Error writing to low stock updates log: {str(e)}')

    except Exception as e:
        error_message = f"{timestamp} - Error executing mutation: {str(e)}\n"
        try:
            with open('/tmp/low_stock_updates_log.txt', 'a') as log_file:
                log_file.write(error_message)
        except Exception as write_error:
            print(
                f'Error writing to low stock updates log: {str(write_error)}')
