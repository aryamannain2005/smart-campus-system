"""
Models for Smart Attendance Management System.
Includes Student, Faculty, Course, and Attendance models.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Department(models.Model):
    """Department model for organizing courses and faculty."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['name']


class Faculty(models.Model):
    """Faculty model linked to Django User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='faculty_members')
    phone = models.CharField(max_length=15, blank=True)
    designation = models.CharField(max_length=50, default='Assistant Professor')
    profile_image = models.ImageField(upload_to='faculty_images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"

    class Meta:
        verbose_name_plural = 'Faculty'
        ordering = ['employee_id']


class Parent(models.Model):
    """Parent model for notification purposes."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    relationship = models.CharField(max_length=20, choices=[
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class Student(models.Model):
    """Student model with face encoding for recognition."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', null=True, blank=True)
    student_id = models.CharField(max_length=20, unique=True)
    roll_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='students')
    semester = models.IntegerField(default=1)
    section = models.CharField(max_length=5, default='A')
    profile_image = models.ImageField(upload_to='student_images/', blank=True, null=True)
    face_encoding = models.BinaryField(blank=True, null=True)  # Stored face encoding for recognition
    parent = models.ForeignKey(Parent, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['roll_number']


class Course(models.Model):
    """Course model for attendance tracking."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='courses')
    semester = models.IntegerField(default=1)
    credits = models.IntegerField(default=3)
    students = models.ManyToManyField(Student, related_name='courses', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['code']


class AttendanceSession(models.Model):
    """Attendance session for a particular class."""
    SESSION_TYPES = [
        ('manual', 'Manual Entry'),
        ('face_recognition', 'Face Recognition'),
        ('mobile', 'Mobile App'),
        ('qr_code', 'QR Code'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='attendance_sessions')
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='attendance_sessions')
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='manual')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.code} - {self.date} ({self.session_type})"

    class Meta:
        ordering = ['-date', '-start_time']


class Attendance(models.Model):
    """Individual attendance record for a student."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]

    VERIFICATION_METHODS = [
        ('manual', 'Manual'),
        ('face_recognition', 'Face Recognition'),
        ('mobile_gps', 'Mobile GPS'),
        ('qr_scan', 'QR Scan'),
    ]

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    verification_method = models.CharField(max_length=20, choices=VERIFICATION_METHODS, default='manual')
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='marked_attendances')
    face_confidence = models.FloatField(null=True, blank=True)  # Confidence score for face recognition
    location_lat = models.FloatField(null=True, blank=True)  # GPS latitude for mobile verification
    location_lng = models.FloatField(null=True, blank=True)  # GPS longitude for mobile verification
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.student_id} - {self.session.course.code} - {self.status}"

    class Meta:
        unique_together = ['session', 'student']
        ordering = ['-marked_at']


class AttendanceReport(models.Model):
    """Generated attendance reports."""
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('course', 'Course Report'),
        ('student', 'Student Report'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    total_sessions = models.IntegerField(default=0)
    present_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    late_count = models.IntegerField(default=0)
    attendance_percentage = models.FloatField(default=0.0)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)

    def __str__(self):
        return f"{self.report_type} - {self.start_date} to {self.end_date}"

    class Meta:
        ordering = ['-generated_at']
