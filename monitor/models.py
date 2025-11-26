from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)
    url = models.URLField()
    description = models.TextField()
    check_interval = models.IntegerField(default=1)  # minutes
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StatusCheck(models.Model):
    STATUS_CHOICES = [
        ('operational', 'Operational'),
        ('degraded', 'Degraded'),
        ('outage', 'Outage'),
    ]
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    response_time = models.IntegerField()  # milliseconds
    error_message = models.TextField(blank=True, null=True)
    checked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['service', 'checked_at']),
        ]

    def __str__(self):
        return f"{self.service.name} - {self.status}"

class OutagePeriod(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.service.name} outage - {self.started_at}"