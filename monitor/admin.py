from django.contrib import admin
from django.utils import timezone
import pytz
from .models import Service, StatusCheck, OutagePeriod

class MyanmarTimeAdmin(admin.ModelAdmin):
    def myanmar_time(self, obj):
        myanmar_tz = pytz.timezone('Asia/Yangon')
        myanmar_time = obj.checked_at.astimezone(myanmar_tz)
        return myanmar_time.strftime('%b. %d, %Y, %I:%M %p')
    myanmar_time.short_description = 'Checked at (MMT)'

@admin.register(StatusCheck)
class StatusCheckAdmin(MyanmarTimeAdmin):
    list_display = ['service', 'status', 'response_time', 'myanmar_time']
    list_filter = ['status', 'service', 'checked_at']
    readonly_fields = ['checked_at']
    date_hierarchy = 'checked_at'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'url']

@admin.register(OutagePeriod)
class OutagePeriodAdmin(admin.ModelAdmin):
    list_display = ['service', 'started_at_mmt', 'resolved_at_mmt', 'duration_minutes']
    list_filter = ['service', 'started_at']
    readonly_fields = ['duration_minutes']
    date_hierarchy = 'started_at'
    
    def started_at_mmt(self, obj):
        myanmar_tz = pytz.timezone('Asia/Yangon')
        return obj.started_at.astimezone(myanmar_tz).strftime('%b. %d, %Y, %I:%M %p')
    started_at_mmt.short_description = 'Started at (MMT)'
    
    def resolved_at_mmt(self, obj):
        if obj.resolved_at:
            myanmar_tz = pytz.timezone('Asia/Yangon')
            return obj.resolved_at.astimezone(myanmar_tz).strftime('%b. %d, %Y, %I:%M %p')
        return '-'
    resolved_at_mmt.short_description = 'Resolved at (MMT)'