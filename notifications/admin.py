"""
Admin configuration for Notification System.
"""

from django.contrib import admin
from .models import Notification, ParentNotification, NotificationTemplate, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['student', 'notification_type', 'title', 'is_read', 'is_sent', 'created_at']
    list_filter = ['notification_type', 'is_read', 'is_sent', 'priority']
    search_fields = ['student__first_name', 'student__last_name', 'title']
    date_hierarchy = 'created_at'


@admin.register(ParentNotification)
class ParentNotificationAdmin(admin.ModelAdmin):
    list_display = ['parent', 'student', 'notification_type', 'title', 'email_sent', 'sms_sent', 'created_at']
    list_filter = ['notification_type', 'email_sent', 'sms_sent']
    search_fields = ['parent__name', 'student__first_name']
    date_hierarchy = 'created_at'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'notification_type', 'is_active']
    list_filter = ['notification_type', 'is_active']


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['channel', 'recipient', 'status', 'sent_at', 'created_at']
    list_filter = ['channel', 'status']
    search_fields = ['recipient']
    date_hierarchy = 'created_at'
