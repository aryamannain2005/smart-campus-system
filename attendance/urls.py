"""
URL patterns for Attendance Management System.
"""

from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Home page (landing page - no login required)
    path('', views.home, name='home'),
    
    # Faculty Authentication
    path('login/', views.faculty_login, name='login'),
    path('logout/', views.faculty_logout, name='logout'),
    path('register/', views.faculty_register, name='faculty_register'),
    
    # Student Authentication & Registration
    path('student/register/', views.student_register, name='student_register'),
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    
    # Faculty Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Course Management
    path('course/create/', views.create_course, name='create_course'),
    path('courses/', views.manage_courses, name='manage_courses'),
    path('course/<int:course_id>/enroll/', views.enroll_students, name='enroll_students'),
    
    # Session Management
    path('session/create/', views.create_session, name='create_session'),
    path('session/<uuid:session_id>/', views.session_detail, name='session_detail'),
    path('session/<uuid:session_id>/mark/', views.mark_attendance, name='mark_attendance'),
    path('session/<uuid:session_id>/face-recognition/', views.face_recognition_attendance, name='face_recognition_attendance'),
    
    # Reports
    path('reports/', views.attendance_reports, name='reports'),
    
    # Student Views (Faculty viewing student details)
    path('student/<int:student_id>/', views.student_attendance_detail, name='student_detail'),
    path('course/<int:course_id>/students/', views.course_students, name='course_students'),
    
    # AJAX Endpoints
    path('ajax/update-attendance/', views.update_attendance_ajax, name='update_attendance_ajax'),
    path('ajax/session-stats/<uuid:session_id>/', views.get_session_stats_ajax, name='session_stats_ajax'),
]
