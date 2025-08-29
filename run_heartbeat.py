import os
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_graphql.crm.settings')
django.setup()

from alx_graphql.crm.cron import log_crm_heartbeat

# Run heartbeat
log_crm_heartbeat()

