from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from monitor.models import StatusCheck

class Command(BaseCommand):
    help = 'Clean up old status check data - keep last 7 days only'

    def handle(self, *args, **options):
        # Keep only LAST 7 days, delete anything older
        seven_days_ago = timezone.now() - timedelta(days=7)
        deleted_count, _ = StatusCheck.objects.filter(
            checked_at__lt=seven_days_ago  # "less than" 7 days ago = older than 7 days
        ).delete()
        
        self.stdout.write(self.style.SUCCESS(f"🧹 Cleaned up {deleted_count} status records older than 7 days"))