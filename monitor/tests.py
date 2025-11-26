from django.test import TestCase
from django.utils import timezone
from .models import Service

class ServiceModelTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name="Test Service",
            url="https://example.com",
            description="Test description"
        )
    
    def test_service_creation(self):
        self.assertEqual(self.service.name, "Test Service")
        self.assertTrue(self.service.is_active)