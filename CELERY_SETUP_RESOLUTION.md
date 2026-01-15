# Celery Configuration - Issue Resolution

## Problem
When running `celery -A crm worker -l info`, the following error occurred:
```
.> transport:   amqp://guest:**@localhost:5672//
.> results:     disabled://
[ERROR] consumer: Cannot connect to amqp://guest:**@127.0.0.1:5672//: [Errno 111] Connection refused.
```

This indicated that Celery was trying to use AMQP (RabbitMQ) instead of the configured Redis broker.

## Root Causes
1. **Celery configuration not loaded**: The Celery app wasn't reading the Django settings with `CELERY_*` prefix variables
2. **Settings in wrong location**: Initial configuration was placed in `crm/settings.py` instead of the main `alx_backend_graphql/settings.py`
3. **Missing Redis installation**: Redis server was not installed on the system

## Solutions Applied

### 1. Installed Redis
```bash
sudo apt-get install -y redis-server redis-tools
```

### 2. Moved Celery Configuration to Main Settings
Moved all Celery configuration from `crm/settings.py` to `alx_backend_graphql/settings.py`:
- Added `django_celery_beat` to `INSTALLED_APPS`
- Added Celery broker and result backend configuration
- Added Celery Beat schedule configuration

### 3. Fixed Celery App Initialization
- Removed problematic `django.setup()` call from `crm/celery.py` (Django calls it automatically)
- Ensured `app.config_from_object('django.conf:settings', namespace='CELERY')` properly loads settings

### 4. Ran Migrations
```bash
python manage.py migrate
```
This created necessary Celery Beat database tables.

## Verification

### Worker Connection
```
[✓] .> transport:   redis://localhost:6379/0
[✓] .> results:     redis://localhost:6379/0
[✓] Connected to redis://localhost:6379/0
[✓] celery@DESKTOP-46N5TUK ready.
```

### Beat Scheduler
```
[✓] beat: Starting...
```

## Files Modified
1. `alx_backend_graphql/settings.py` - Added Celery configuration
2. `crm/celery.py` - Simplified to remove redundant django.setup()
3. `crm/settings.py` - Cleared (now just a comment)

## Running the Application

### Terminal 1 - Django Server
```bash
source .venv/bin/activate
python manage.py runserver
```

### Terminal 2 - Celery Worker
```bash
source .venv/bin/activate
celery -A crm worker -l info
```

### Terminal 3 - Celery Beat
```bash
source .venv/bin/activate
celery -A crm beat -l info
```

## Testing the Implementation

### Test CRM Report Task
```bash
# From Django shell
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()  # Run async
>>> generate_crm_report()  # Run sync
```

### Check Report Log
```bash
cat /tmp/crm_report_log.txt
```

Expected output format:
```
2026-01-15 10:36:33 - Report: 5 customers, 12 orders, 4567.89 revenue
```

## Status
✅ Redis installed and running
✅ Celery worker connecting to Redis
✅ Celery Beat scheduler operational
✅ Database migrations applied
✅ Task auto-discovery working
✅ Ready for production use
