from django.core.management.base import BaseCommand
from crm.models import Customer
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Delete customers who have been inactive for more than 1 year (based on created_at)'

    def handle(self, *args, **kwargs):
        cutoff_date = timezone.now() - timedelta(days=365)
        inactive_customers = Customer.objects.filter(created_at__lt=cutoff_date)
        count = inactive_customers.count()
        inactive_customers.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} inactive customers"))

