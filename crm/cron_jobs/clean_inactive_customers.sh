#!/bin/bash

# Activate virtual environment
source /c/Users/Admin/alx-backend-graphql_crm/venv/Scripts/activate

# Move to project directory
cd /c/Users/Admin/alx-backend-graphql_crm

# Delete inactive customers (1 year = 365 days)
count=$(python - <<END
from crm.customers.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(created_at__lt=cutoff_date)
deleted_count = inactive_customers.count()
inactive_customers.delete()
print(f"Deleted {deleted_count} inactive customers")
deleted_count
END
)

# Log the output
echo "$(date) - Deleted $count inactive customers" >> /tmp/customer_cleanup_log.txt

