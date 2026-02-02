"""
Django REST Framework Serializers for Mobile App API.
"""

from rest_framework import serializers
from attendance.models import (
    Student, Faculty, Course, Department,
    AttendanceSession, Attendance, AttendanceReport
)
from notifications.models import Notification


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code']


class StudentSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'roll_number', 'first_name', 'last_name',
            'full_name', 'email', 'phone', 'department', 'semester',
            'section', 'profile_image', 'is_active'
        ]


class StudentMinimalSerializer(serializers.ModelSerializer):
    """Minimal student info for attendance lists."""
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'student_id', 'roll_number', 'full_name']


class FacultySerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Faculty
        fields = [
            'id', 'employee_id', 'full_name', 'department',
            'designation', 'phone', 'profile_image'
        ]
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class CourseSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)
    student_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'code', 'name', 'department', 'faculty',
            'semester', 'credits', 'student_count', 'is_active'
        ]
    
    def get_student_count(self, obj):
        return obj.students.filter(is_active=True).count()


class AttendanceSessionSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)
    attendance_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceSession
        fields = [
            'id', 'course', 'faculty', 'date', 'start_time',
            'end_time', 'session_type', 'is_active', 'attendance_count'
        ]
    
    def get_attendance_count(self, obj):
        return obj.attendance_records.count()


class AttendanceSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance sessions."""
    class Meta:
        model = AttendanceSession
        fields = ['course', 'date', 'start_time', 'end_time', 'session_type']


class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentMinimalSerializer(read_only=True)
    session_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Attendance
        fields = [
            'id', 'session', 'student', 'status', 'verification_method',
            'marked_at', 'face_confidence', 'location_lat', 'location_lng',
            'notes', 'session_info'
        ]
    
    def get_session_info(self, obj):
        return {
            'course_code': obj.session.course.code,
            'course_name': obj.session.course.name,
            'date': obj.session.date,
        }


class AttendanceMarkSerializer(serializers.Serializer):
    """Serializer for marking attendance."""
    session_id = serializers.UUIDField()
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=['present', 'absent', 'late', 'excused'])
    verification_method = serializers.ChoiceField(
        choices=['manual', 'face_recognition', 'mobile_gps', 'qr_scan'],
        default='mobile_gps'
    )
    location_lat = serializers.FloatField(required=False, allow_null=True)
    location_lng = serializers.FloatField(required=False, allow_null=True)
    face_confidence = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class FaceRecognitionSerializer(serializers.Serializer):
    """Serializer for face recognition attendance."""
    session_id = serializers.UUIDField()
    image = serializers.ImageField()
    location_lat = serializers.FloatField(required=False, allow_null=True)
    location_lng = serializers.FloatField(required=False, allow_null=True)


class BulkAttendanceSerializer(serializers.Serializer):
    """Serializer for bulk attendance marking."""
    session_id = serializers.UUIDField()
    attendance_data = serializers.ListField(
        child=serializers.DictField()
    )


class AttendanceReportSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student = StudentMinimalSerializer(read_only=True)
    
    class Meta:
        model = AttendanceReport
        fields = [
            'id', 'report_type', 'course', 'student', 'start_date',
            'end_date', 'total_sessions', 'present_count', 'absent_count',
            'late_count', 'attendance_percentage', 'generated_at'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'is_read', 'created_at', 'read_at'
        ]


class StudentAttendanceStatsSerializer(serializers.Serializer):
    """Serializer for student attendance statistics."""
    total_classes = serializers.IntegerField()
    present_count = serializers.IntegerField()
    absent_count = serializers.IntegerField()
    late_count = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()
    course_wise_stats = serializers.ListField()


class MobileLoginSerializer(serializers.Serializer):
    """Serializer for mobile app login."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    device_token = serializers.CharField(required=False, allow_blank=True)
    device_type = serializers.ChoiceField(
        choices=['ios', 'android'],
        required=False
    )
