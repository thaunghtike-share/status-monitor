from django.core.management.base import BaseCommand
from monitor.models import Service

class Command(BaseCommand):
    help = 'Setup initial monitoring services'

    def handle(self, *args, **options):
        services = [
            {
                'name': 'LearnDevOpsNow Portal',
                'url': 'https://learndevopsnow-mm.blog',
                'description': 'Main learning platform and user interface'
            },
            {
                'name': 'LearnDevOpsNow API',
                'url': 'https://api.learndevopsnow-mm.blog/api/status/',
                'description': 'Backend API services and data endpoints'
            }
        ]

        for service_data in services:
            service, created = Service.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created service: {service.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"ℹ️ Service already exists: {service.name}"))