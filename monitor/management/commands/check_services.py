import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from monitor.models import Service, StatusCheck, OutagePeriod

class Command(BaseCommand):
    help = 'Check status of all active services'

    def check_service(self, url):
        try:
            start_time = timezone.now()
            response = requests.get(url, timeout=10)
            response_time = int((timezone.now() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                status = 'degraded' if response_time > 2000 else 'operational'
            else:
                status = 'outage'
                
            return status, response_time, None
            
        except requests.exceptions.RequestException as e:
            return 'outage', 0, str(e)

    def handle_outage(self, service, status_check):
        ongoing_outage = OutagePeriod.objects.filter(
            service=service,
            resolved_at__isnull=True
        ).first()

        if status_check.status == 'outage' and not ongoing_outage:
            OutagePeriod.objects.create(
                service=service,
                started_at=status_check.checked_at
            )
            self.stdout.write(self.style.ERROR(f"🚨 OUTAGE STARTED: {service.name}"))
        elif status_check.status != 'outage' and ongoing_outage:
            ongoing_outage.resolved_at = status_check.checked_at
            duration = (ongoing_outage.resolved_at - ongoing_outage.started_at).total_seconds() / 60
            ongoing_outage.duration_minutes = int(duration)
            ongoing_outage.save()
            self.stdout.write(self.style.SUCCESS(f"✅ OUTAGE RESOLVED: {service.name} ({duration:.1f} minutes)"))

    def handle(self, *args, **options):
        services = Service.objects.filter(is_active=True)
        
        if not services.exists():
            self.stdout.write(self.style.ERROR("❌ No active services found. Run 'python manage.py setup_services' first."))
            return

        self.stdout.write(f"🔍 Checking {services.count()} services...")
        
        for service in services:
            status, response_time, error = self.check_service(service.url)
            
            status_check = StatusCheck.objects.create(
                service=service,
                status=status,
                response_time=response_time,
                error_message=error
            )
            
            self.handle_outage(service, status_check)
            
            status_style = {
                'operational': self.style.SUCCESS,
                'degraded': self.style.WARNING,
                'outage': self.style.ERROR
            }
            
            self.stdout.write(status_style[status](
                f"{service.name}: {status} ({response_time}ms)"
            ))

        self.stdout.write(self.style.SUCCESS("🎉 All services checked successfully!"))