"""
Admin configuration for Attendance Management System.
"""

from django.contrib import admin
from .models import (
    Department, Faculty, Parent, Student, Course,
    AttendanceSession, Attendance, AttendanceReport
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'designation', 'is_active']
    list_filter = ['department', 'is_active', 'designation']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name']


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'relationship']
    search_fields = ['name', 'email']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'roll_number', 'full_name', 'department', 'semester', 'section', 'is_active']
    list_filter = ['department', 'semester', 'section', 'is_active']
    search_fields = ['student_id', 'roll_number', 'first_name', 'last_name', 'email']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'faculty', 'semester', 'credits', 'is_active']
    list_filter = ['department', 'semester', 'is_active']
    search_fields = ['code', 'name']
    filter_horizontal = ['students']


@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ['course', 'faculty', 'date', 'start_time', 'session_type', 'is_active']
    list_filter = ['session_type', 'is_active', 'date']
    search_fields = ['course__code', 'course__name']
    date_hierarchy = 'date'


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'session', 'status', 'verification_method', 'marked_at']
    list_filter = ['status', 'verification_method', 'session__date']
    search_fields = ['student__student_id', 'student__first_name', 'student__last_name']
    date_hierarchy = 'marked_at'


@admin.register(AttendanceReport)
class AttendanceReportAdmin(admin.ModelAdmin):
    list_display = ['report_type', 'course', 'start_date', 'end_date', 'attendance_percentage', 'generated_at']
    list_filter = ['report_type', 'generated_at']
    date_hierarchy = 'generated_at'
