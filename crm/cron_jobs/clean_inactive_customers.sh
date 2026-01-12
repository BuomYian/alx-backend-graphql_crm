#!/bin/bash

# Script to clean up inactive customers (no orders in the past year)
cd /home/buomyian/alx-backend-graphql_crm

python manage.py shell << EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Calculate the date from a year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find and delete customers with no orders since a year ago
customers_to_delete = Customer.objects.filter(
    orders__isnull=True
) | Customer.objects.filter(
    orders__order_date__lt=one_year_ago
).distinct()

count = customers_to_delete.count()
customers_to_delete.delete()

# Log the result with timestamp
import datetime
with open('/tmp/customer_cleanup_log.txt', 'a') as log:
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log.write(f'{timestamp} - Deleted {count} inactive customers\n')

print(f'Successfully deleted {count} inactive customers')
EOF
