from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime
import pytz
from .models import Service, StatusCheck, OutagePeriod

@api_view(['GET'])
def status_overview(request):
    services_data = []
    
    # Myanmar timezone
    myanmar_tz = pytz.timezone('Asia/Yangon')
    myanmar_now = timezone.now().astimezone(myanmar_tz)
    
    for service in Service.objects.filter(is_active=True):
        # Get today's start in Myanmar time
        today_start = myanmar_now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Convert to UTC for database query
        today_start_utc = today_start.astimezone(pytz.UTC)
        
        # Get today's checks
        today_checks = StatusCheck.objects.filter(
            service=service,
            checked_at__gte=today_start_utc
        ).order_by('checked_at')
        
        # Get latest check (current status)
        latest_check = StatusCheck.objects.filter(service=service).order_by('-checked_at').first()
        
        # Calculate uptime for today
        today_operational = today_checks.filter(status='operational').count()
        today_total = today_checks.count()
        uptime_today = (today_operational / today_total * 100) if today_total > 0 else 100
        
        # Format today's history for the status bar (Myanmar time)
        today_history = []
        for check in today_checks:
            myanmar_time = check.checked_at.astimezone(myanmar_tz)
            today_history.append({
                'time': myanmar_time.strftime('%H:%M'),
                'status': check.status,
                'response_time': check.response_time,
                'full_time': myanmar_time.isoformat()
            })
        
        # Get detailed outage timeline for last 7 days
        seven_days_ago = timezone.now() - timedelta(days=7)
        outages = OutagePeriod.objects.filter(
            service=service,
            started_at__gte=seven_days_ago
        ).order_by('-started_at')
        
        # Create detailed timeline for last 7 days
        detailed_timeline = []
        for day in range(7):
            day_date = (myanmar_now - timedelta(days=day)).date()
            day_start = timezone.make_aware(datetime.combine(day_date, datetime.min.time()))
            day_end = timezone.make_aware(datetime.combine(day_date, datetime.max.time()))
            
            # Get all outages for this day
            day_outages = outages.filter(
                started_at__date=day_date
            )
            
            # Calculate operational periods
            if day_outages.exists():
                status = 'mixed'
                outage_details = []
                for outage in day_outages:
                    start_mmt = outage.started_at.astimezone(myanmar_tz)
                    if outage.resolved_at:
                        end_mmt = outage.resolved_at.astimezone(myanmar_tz)
                        duration = outage.duration_minutes
                        outage_details.append({
                            'start_time': start_mmt.strftime('%H:%M'),
                            'end_time': end_mmt.strftime('%H:%M'),
                            'duration': f"{duration}min",
                            'status': 'outage'
                        })
                    else:
                        outage_details.append({
                            'start_time': start_mmt.strftime('%H:%M'),
                            'end_time': 'Ongoing',
                            'duration': 'Ongoing',
                            'status': 'outage'
                        })
            else:
                status = 'operational'
                outage_details = []
                
            detailed_timeline.append({
                'date': day_date.strftime('%Y-%m-%d'),
                'day_name': day_date.strftime('%A'),
                'status': status,
                'outage_count': len(day_outages),
                'outage_details': outage_details,
                'is_today': day_date == myanmar_now.date()
            })
        
        # Format last checked time in Myanmar time
        if latest_check:
            last_checked_myanmar = latest_check.checked_at.astimezone(myanmar_tz)
            last_checked = last_checked_myanmar.isoformat()
            last_checked_display = last_checked_myanmar.strftime('%H:%M MMT')
        else:
            last_checked = None
            last_checked_display = None
        
        services_data.append({
            'name': service.name,
            'description': service.description,
            'url': service.url,
            'current_status': latest_check.status if latest_check else 'unknown',
            'response_time': latest_check.response_time if latest_check else 0,
            'uptime_today': round(uptime_today, 1),
            'today_history': today_history,
            'last_7_days_timeline': detailed_timeline[::-1],  # Oldest first
            'last_checked': last_checked,
            'last_checked_display': last_checked_display,
            'timezone': 'MMT (UTC+6:30)'
        })
    
    return Response({
        'services': services_data,
        'last_updated': myanmar_now.isoformat(),
        'last_updated_display': myanmar_now.strftime('%Y-%m-%d %H:%M:%S MMT'),
        'timezone': 'Asia/Yangon (UTC+6:30)'
    })