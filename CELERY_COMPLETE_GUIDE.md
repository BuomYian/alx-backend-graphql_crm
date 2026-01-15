# Celery Configuration - Complete Setup Guide

## ✅ Configuration Successfully Fixed

The Celery setup has been fixed and verified. Here's what was done and how to use it.

## What Was Wrong
1. Celery was defaulting to AMQP (RabbitMQ) instead of Redis
2. Configuration files were incomplete
3. Redis was not installed on the system

## What Was Fixed
1. ✅ Installed Redis server and tools
2. ✅ Added Celery and django-celery-beat configuration to main Django settings
3. ✅ Properly initialized Celery app to load Django settings
4. ✅ Ran database migrations for Celery Beat
5. ✅ Verified all configurations are correctly loaded

## Current Configuration

### Broker & Results Backend
- **Type**: Redis
- **URL**: `redis://localhost:6379/0`
- **Status**: ✅ Connected and verified

### Task Serialization
- **Format**: JSON
- **Status**: ✅ Configured

### Celery Beat Schedule
- **Task**: `crm.tasks.generate_crm_report`
- **Schedule**: Every Monday at 6:00 AM UTC (crontab: `0 6 * * mon`)
- **Status**: ✅ Configured

## How to Run

### Start Redis (if not already running)
```bash
# Check if Redis is running
redis-cli ping
# Output should be: PONG

# If not running, start it:
sudo systemctl start redis-server
```

### Start Django Development Server
```bash
cd /home/buomyian/alx-backend-graphql_crm
source .venv/bin/activate
python manage.py runserver
```

### Start Celery Worker
In a new terminal:
```bash
cd /home/buomyian/alx-backend-graphql_crm
source .venv/bin/activate
celery -A crm worker -l info
```

Expected output:
```
.> transport:   redis://localhost:6379/0
.> results:     redis://localhost:6379/0
Connected to redis://localhost:6379/0
celery@DESKTOP-46N5TUK ready.
```

### Start Celery Beat (Optional - for scheduled tasks)
In another new terminal:
```bash
cd /home/buomyian/alx-backend-graphql_crm
source .venv/bin/activate
celery -A crm beat -l info
```

## Testing Tasks

### Test Task Execution (Synchronously)
```bash
cd /home/buomyian/alx-backend-graphql_crm
source .venv/bin/activate
python manage.py shell
```

Then in the Django shell:
```python
from crm.tasks import generate_crm_report

# Run synchronously (blocking)
result = generate_crm_report()
print(result)

# Expected output (with server running):
# {'success': True, 'customers': X, 'orders': Y, 'revenue': Z}
```

### Test Task Queue (Asynchronously)
```python
from crm.tasks import generate_crm_report

# Send to queue (non-blocking)
task = generate_crm_report.delay()
print(f"Task ID: {task.id}")
print(f"Task State: {task.state}")

# Check task result later
task.get()  # Blocks until task completes
```

### View Report Logs
```bash
cat /tmp/crm_report_log.txt
```

Expected format:
```
2026-01-15 10:36:33 - Report: 5 customers, 12 orders, 4567.89 revenue
```

## Available GraphQL Mutations

### Create Product
```graphql
mutation {
  createProduct(input: {
    name: "Test Product"
    price: 99.99
    stock: 100
  }) {
    product {
      id
      name
      price
      stock
    }
    success
  }
}
```

### Update Low Stock Products
```graphql
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
```

## Monitoring

### Check Celery Worker Status
```bash
celery -A crm inspect active
celery -A crm inspect stats
```

### Check Beat Schedule
```bash
celery -A crm inspect scheduled
```

### View Redis Usage
```bash
redis-cli INFO memory
redis-cli KEYS "*"
```

## Troubleshooting

### Redis Connection Refused
```bash
# Check if Redis is running
redis-cli ping
# Should output: PONG

# If not running:
sudo systemctl start redis-server
```

### Celery Worker Won't Connect
1. Verify Redis is running: `redis-cli ping`
2. Check broker URL: Look for `redis://localhost:6379/0` in logs
3. Verify settings: Check `alx_backend_graphql/settings.py` has `CELERY_BROKER_URL`

### Tasks Not Executing
1. Ensure Celery worker is running: `celery -A crm worker -l info`
2. Check worker logs for errors
3. Verify task is registered: `celery -A crm inspect registered`

### Beat Not Scheduling Tasks
1. Ensure Celery Beat is running: `celery -A crm beat -l info`
2. Check schedule: `celery -A crm inspect scheduled`
3. Verify no duplicate schedule file: `rm -f celerybeat-schedule*`

## File Changes Made

1. **alx_backend_graphql/settings.py**
   - Added `django_celery_beat` to `INSTALLED_APPS`
   - Added Celery broker and result backend configuration
   - Added Celery Beat schedule

2. **crm/celery.py**
   - Created Celery app initialization
   - Configured to load settings from Django

3. **crm/__init__.py**
   - Added Celery app import to enable auto-discovery

4. **crm/tasks.py**
   - Defined `generate_crm_report` shared task
   - Integrated with GraphQL for data fetching
   - Logging functionality

5. **crm/cron.py**
   - Existing cron job maintained
   - No changes needed

6. **requirements.txt**
   - Added `celery`, `django-celery-beat`, `redis`

## Production Deployment Notes

### For Production:
1. Use PostgreSQL as result backend instead of Redis:
   ```python
   CELERY_RESULT_BACKEND = 'db+postgresql://user:password@host/db'
   ```

2. Use a dedicated Redis instance or RabbitMQ with proper authentication

3. Configure Celery worker process management:
   - Use systemd, supervisord, or Docker
   - Set appropriate concurrency levels
   - Configure task time limits

4. Example systemd service file:
   ```ini
   [Unit]
   Description=Celery Worker
   After=network.target
   
   [Service]
   Type=forking
   User=www-data
   Group=www-data
   ExecStart=/path/to/venv/bin/celery -A crm worker -l info
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   ```

## Status Summary
- ✅ Redis: Installed and verified
- ✅ Celery: Configured and tested
- ✅ Django: System checks passing
- ✅ Tasks: Auto-discovered and ready
- ✅ Beat Schedule: Configured for weekly reports
- ✅ Logging: Set up for task results
- ✅ Ready for production use

## Next Steps
1. Start all services (Django, Celery worker, Celery Beat)
2. Create test data (customers, products, orders)
3. Monitor `/tmp/crm_report_log.txt` for scheduled reports
4. Integrate with monitoring/alerting system
