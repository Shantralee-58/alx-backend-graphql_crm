#!/bin/bash
# crm/cron_jobs/clean_inactive_customers.sh

# Exit immediately if a command exits with a non-zero status
set -e

# Go to the project root (adjust path if script is not inside project root)
cd "$(dirname "$0")/../.."

# Activate the virtual environment
source venv/scripts/activate

# Run Django management command
python manage.py clean_inactive_customers

# Deactivate virtual environment
deactivate

