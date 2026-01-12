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
