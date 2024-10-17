from apps.models import Notification
from django.utils import timezone

def system_notification():
    current_time = timezone.now()
    notifications = Notification.objects.filter(until_date__gte=current_time).order_by('-created_at')
    return notifications