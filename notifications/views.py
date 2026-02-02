"""
Views for Notification System.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import Notification, ParentNotification, NotificationLog


@login_required
def notification_list(request):
    """View all notifications for the logged-in user."""
    try:
        student = request.user.student_profile
        notifications = Notification.objects.filter(student=student).order_by('-created_at')
    except:
        notifications = []
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'notifications/list.html', context)


@login_required
def notification_detail(request, notification_id):
    """View a single notification and mark it as read."""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Mark as read
    if not notification.is_read:
        notification.mark_as_read()
    
    context = {
        'notification': notification,
    }
    return render(request, 'notifications/detail.html', context)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """AJAX endpoint to mark notification as read."""
    notification = get_object_or_404(Notification, id=notification_id)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification marked as read'
    })


@login_required
@require_POST
def mark_all_as_read(request):
    """Mark all notifications as read for the current user."""
    try:
        student = request.user.student_profile
        Notification.objects.filter(
            student=student,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        return JsonResponse({
            'success': True,
            'message': 'All notifications marked as read'
        })
    except:
        return JsonResponse({
            'success': False,
            'error': 'Failed to mark notifications as read'
        }, status=400)


@login_required
def unread_count(request):
    """Get count of unread notifications."""
    try:
        student = request.user.student_profile
        count = Notification.objects.filter(
            student=student,
            is_read=False
        ).count()
    except:
        count = 0
    
    return JsonResponse({'count': count})


@login_required
def notification_logs(request):
    """View notification delivery logs (admin only)."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    logs = NotificationLog.objects.all().order_by('-created_at')[:100]
    
    context = {
        'logs': logs,
    }
    return render(request, 'notifications/logs.html', context)
