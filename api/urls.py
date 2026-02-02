"""
URL patterns for Mobile App REST API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

# Create router for viewsets
router = DefaultRouter()
router.register(r'students', views.StudentViewSet, basename='student')
router.register(r'courses', views.CourseViewSet, basename='course')
router.register(r'sessions', views.AttendanceSessionViewSet, basename='session')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    # Authentication
    path('auth/login/', views.MobileLoginView.as_view(), name='mobile_login'),
    path('auth/logout/', views.MobileLogoutView.as_view(), name='mobile_logout'),
    
    # Dashboard endpoints
    path('dashboard/faculty/', views.faculty_dashboard, name='faculty_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    
    # Attendance marking
    path('attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('attendance/bulk-mark/', views.bulk_mark_attendance, name='bulk_mark_attendance'),
    
    # Face recognition
    path('face-recognition/mark/', views.face_recognition_mark, name='face_recognition_mark'),
    path('face-recognition/identify/', views.face_recognition_identify, name='face_recognition_identify'),
    
    # Router URLs
    path('', include(router.urls)),
]
