"""
URL patterns for Face Recognition Module.
"""

from django.urls import path
from . import views

app_name = 'face_recognition'

urlpatterns = [
    path('', views.face_recognition_dashboard, name='dashboard'),
    path('process/', views.process_face_image, name='process'),
    path('register/', views.register_student_face, name='register'),
    path('batch/', views.batch_face_recognition, name='batch'),
    path('auto-absent/<uuid:session_id>/', views.auto_mark_absentees, name='auto_absent'),
    path('stats/<uuid:session_id>/', views.get_session_stats_realtime, name='stats'),
    path('low-attendance/', views.low_attendance_report, name='low_attendance'),
]
