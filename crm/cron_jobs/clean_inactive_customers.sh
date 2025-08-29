#!/bin/bash

# Activate virtual environment
source /c/Users/Admin/alx-backend-graphql-crm/venv/Scripts/activate

# Move to project directory
cd /c/Users/Admin/alx-backend-graphql-crm

# Run the management command and append output to log
python manage.py clean_inactive_customers >> /tmp/customer_cleanup_log.txt 2>&1

