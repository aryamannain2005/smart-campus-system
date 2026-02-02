"""
URL patterns for Notification System.
"""

from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('<uuid:notification_id>/', views.notification_detail, name='detail'),
    path('<uuid:notification_id>/mark-read/', views.mark_as_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('logs/', views.notification_logs, name='logs'),
]
