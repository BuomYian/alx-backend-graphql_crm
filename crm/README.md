# CRM Backend - Setup and Configuration Guide

## Overview
This document provides step-by-step instructions to set up and run the CRM backend application with all its components including Django Crontab jobs and Celery tasks.

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- Redis server
- Virtual environment (optional but recommended)

## Installation Steps

### 1. Install Redis
Redis is required as the message broker for Celery. Install it based on your operating system:

**On Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**On macOS:**
```bash
brew install redis
brew services start redis
```

**On Windows:**
Download and install from [redis.io/download](https://redis.io/download) or use Windows Subsystem for Linux (WSL).

### 2. Install Python Dependencies
```bash
# Activate your virtual environment (if using one)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install all required packages
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py migrate
```

This will create all necessary database tables including those for django-celery-beat.

### 4. Create a Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 5. Collect Static Files (Optional)
```bash
python manage.py collectstatic --noinput
```

## Running the Application

### Start the Django Development Server
```bash
python manage.py runserver
```

The GraphQL endpoint will be available at `http://localhost:8000/graphql`

### Start the Celery Worker
In a new terminal, run:
```bash
celery -A crm worker -l info
```

This will start the Celery worker that processes background tasks.

### Start Celery Beat Scheduler
In another new terminal, run:
```bash
celery -A crm beat -l info
```

This will start Celery Beat, which schedules the weekly CRM report generation.

## Features

### 1. Django Crontab Jobs
Configured in `crm/settings.py`:

- **CRM Heartbeat (Every 5 minutes):** Logs application health status
  - Log file: `/tmp/crm_heartbeat_log.txt`
  
- **Update Low Stock (Every 12 hours):** Updates product stock for items with stock < 10
  - Increments stock by 10 (simulating restocking)
  - Log file: `/tmp/low_stock_updates_log.txt`

### 2. Celery Tasks
Scheduled via Celery Beat in `crm/settings.py`:

- **Generate CRM Report (Weekly - Monday 6:00 AM UTC):**
  - Fetches total customers, orders, and revenue via GraphQL
  - Logs report to `/tmp/crm_report_log.txt`
  - Format: `YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue`

## Verifying Operations

### Check Celery Beat Schedule
```bash
celery -A crm inspect scheduled
```

### Monitor Celery Tasks
```bash
celery -A crm events
```

### View Generated Reports
```bash
# CRM Report
cat /tmp/crm_report_log.txt

# Low Stock Updates
cat /tmp/low_stock_updates_log.txt

# CRM Heartbeat
cat /tmp/crm_heartbeat_log.txt
```

## GraphQL Operations

### Query Customers
```graphql
{
  allCustomers {
    totalCount
    edges {
      node {
        id
        name
        email
      }
    }
  }
}
```

### Query Orders
```graphql
{
  allOrders {
    totalCount
    edges {
      node {
        id
        customer {
          name
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

### Create a Product
```graphql
mutation {
  createProduct(input: {
    name: "Product Name"
    price: 99.99
    stock: 100
  }) {
    product {
      id
      name
      price
      stock
    }
    message
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

## Troubleshooting

### Redis Connection Error
If you get "Connection refused" errors:
1. Ensure Redis is running: `redis-cli ping` (should return PONG)
2. Check Redis is accessible at `localhost:6379`
3. Restart Redis if needed

### Celery Task Not Running
1. Verify Celery worker is running (`celery -A crm worker -l info`)
2. Check Celery Beat is running (`celery -A crm beat -l info`)
3. Verify task is in schedule: `celery -A crm inspect scheduled`

### Migration Errors
```bash
# Reset migrations if needed (caution: will delete data)
python manage.py migrate crm zero
python manage.py migrate crm
```

### GraphQL Endpoint Not Accessible
1. Ensure Django development server is running
2. Check `http://localhost:8000/graphql` in browser
3. Verify no other service is using port 8000

## Advanced Configuration

### Change Report Schedule
Edit `crm/settings.py` and modify the `CELERY_BEAT_SCHEDULE`:
```python
CELERY_BEAT_SCHEDULE = {
    'generate-crm-report': {
        'task': 'crm.tasks.generate_crm_report',
        'schedule': crontab(day_of_week='wed', hour=10, minute=30),  # Wednesday 10:30 AM
    },
}
```

### Change Celery Broker URL
Modify `CELERY_BROKER_URL` in `crm/settings.py` to point to your Redis instance:
```python
CELERY_BROKER_URL = 'redis://your-host:your-port/0'
```

### Use PostgreSQL as Result Backend
Install psycopg2 and update settings:
```python
CELERY_RESULT_BACKEND = 'db+postgresql://user:password@localhost/celery_db'
```

## Performance Tips

1. **Use a dedicated Redis instance for production**
2. **Configure Celery worker concurrency based on CPU cores:** `celery -A crm worker -l info -c 4`
3. **Monitor task queue:** `celery -A crm inspect active`
4. **Set task time limits:** Configure in `crm/settings.py`

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Celery documentation: https://docs.celeryproject.io/
3. Check django-celery-beat: https://github.com/celery/django-celery-beat
4. Review GraphQL schema at `http://localhost:8000/graphql`
