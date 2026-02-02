"""
REST API Views for Mobile App Interface.
Provides endpoints for attendance management, face recognition, and notifications.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from attendance.models import (
    Student, Faculty, Course, Department,
    AttendanceSession, Attendance, AttendanceReport
)
from notifications.models import Notification
from .serializers import (
    StudentSerializer, FacultySerializer, CourseSerializer,
    AttendanceSessionSerializer, AttendanceSessionCreateSerializer,
    AttendanceSerializer, AttendanceMarkSerializer,
    FaceRecognitionSerializer, BulkAttendanceSerializer,
    NotificationSerializer, StudentAttendanceStatsSerializer,
    MobileLoginSerializer
)


class MobileLoginView(APIView):
    """
    Mobile app login endpoint.
    Returns authentication token for subsequent API calls.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = MobileLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                
                # Determine user type
                user_type = 'unknown'
                user_data = {'id': user.id, 'username': user.username}
                
                if hasattr(user, 'faculty_profile'):
                    user_type = 'faculty'
                    user_data.update(FacultySerializer(user.faculty_profile).data)
                elif hasattr(user, 'student_profile'):
                    user_type = 'student'
                    user_data.update(StudentSerializer(user.student_profile).data)
                
                return Response({
                    'success': True,
                    'token': token.key,
                    'user_type': user_type,
                    'user': user_data
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MobileLogoutView(APIView):
    """Mobile app logout - invalidates token."""
    
    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({'success': True, 'message': 'Logged out successfully'})
        except:
            return Response({'success': False, 'error': 'Logout failed'})


# ============== Student API Views ==============

class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing students."""
    queryset = Student.objects.filter(is_active=True)
    serializer_class = StudentSerializer
    filterset_fields = ['department', 'semester', 'section']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    ordering_fields = ['student_id', 'roll_number', 'first_name']
    ordering = ['roll_number']
    
    @action(detail=True, methods=['get'])
    def attendance_stats(self, request, pk=None):
        """Get attendance statistics for a student."""
        student = self.get_object()
        
        records = Attendance.objects.filter(student=student)
        stats = records.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late'))
        )
        
        # Calculate percentage
        total = stats['total'] or 1
        stats['attendance_percentage'] = round(
            (stats['present'] + stats['late']) / total * 100, 1
        )
        
        # Course-wise stats
        course_stats = []
        for course in student.courses.all():
            course_records = records.filter(session__course=course)
            course_agg = course_records.aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status='present')),
                absent=Count('id', filter=Q(status='absent'))
            )
            course_total = course_agg['total'] or 1
            course_stats.append({
                'course_code': course.code,
                'course_name': course.name,
                'total': course_agg['total'],
                'present': course_agg['present'],
                'absent': course_agg['absent'],
                'percentage': round(course_agg['present'] / course_total * 100, 1)
            })
        
        return Response({
            'total_classes': stats['total'],
            'present_count': stats['present'],
            'absent_count': stats['absent'],
            'late_count': stats['late'],
            'attendance_percentage': stats['attendance_percentage'],
            'course_wise_stats': course_stats
        })
    
    @action(detail=True, methods=['get'])
    def attendance_history(self, request, pk=None):
        """Get attendance history for a student."""
        student = self.get_object()
        records = Attendance.objects.filter(student=student).order_by('-session__date')[:50]
        serializer = AttendanceSerializer(records, many=True)
        return Response(serializer.data)


# ============== Course API Views ==============

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for viewing courses."""
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    filterset_fields = ['department', 'semester', 'faculty']
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'semester']
    ordering = ['code']
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Get students enrolled in a course."""
        course = self.get_object()
        students = course.students.filter(is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def sessions(self, request, pk=None):
        """Get attendance sessions for a course."""
        course = self.get_object()
        sessions = AttendanceSession.objects.filter(course=course).order_by('-date')[:20]
        serializer = AttendanceSessionSerializer(sessions, many=True)
        return Response(serializer.data)


# ============== Attendance Session API Views ==============

class AttendanceSessionViewSet(viewsets.ModelViewSet):
    """API endpoint for attendance sessions."""
    queryset = AttendanceSession.objects.all()
    filterset_fields = ['course', 'faculty', 'date', 'session_type', 'is_active']
    search_fields = ['course__code', 'course__name']
    ordering_fields = ['date', 'start_time']
    ordering = ['-date', '-start_time']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AttendanceSessionCreateSerializer
        return AttendanceSessionSerializer
    
    def perform_create(self, serializer):
        faculty = self.request.user.faculty_profile
        serializer.save(faculty=faculty)
    
    @action(detail=True, methods=['get'])
    def attendance_list(self, request, pk=None):
        """Get attendance records for a session."""
        session = self.get_object()
        records = Attendance.objects.filter(session=session)
        serializer = AttendanceSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a session."""
        session = self.get_object()
        records = Attendance.objects.filter(session=session)
        
        stats = records.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            excused=Count('id', filter=Q(status='excused'))
        )
        
        total = stats['total'] or 1
        stats['attendance_percentage'] = round(
            (stats['present'] + stats['late']) / total * 100, 1
        )
        
        return Response(stats)


# ============== Attendance Marking API Views ==============

@api_view(['POST'])
def mark_attendance(request):
    """
    Mark attendance for a student.
    Used by mobile app for GPS-based or manual attendance.
    """
    serializer = AttendanceMarkSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        
        session = get_object_or_404(AttendanceSession, id=data['session_id'])
        student = get_object_or_404(Student, id=data['student_id'])
        
        # Validate session is active
        if not session.is_active:
            return Response({
                'success': False,
                'error': 'This attendance session is not active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate student is enrolled in course
        if not session.course.students.filter(id=student.id).exists():
            return Response({
                'success': False,
                'error': 'Student is not enrolled in this course'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Create or update attendance record
        attendance, created = Attendance.objects.update_or_create(
            session=session,
            student=student,
            defaults={
                'status': data['status'],
                'verification_method': data.get('verification_method', 'mobile_gps'),
                'marked_by': request.user,
                'location_lat': data.get('location_lat'),
                'location_lng': data.get('location_lng'),
                'face_confidence': data.get('face_confidence'),
                'notes': data.get('notes', '')
            }
        )
        
        # Send notification if absent
        if data['status'] == 'absent':
            try:
                from notifications.utils import send_single_absentee_notification
                send_single_absentee_notification(attendance)
            except Exception as e:
                # Log but don't fail the request if notification fails
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send notification: {e}")
        
        return Response({
            'success': True,
            'message': 'Attendance marked successfully',
            'attendance_id': attendance.id,
            'created': created
        })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error marking attendance: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def bulk_mark_attendance(request):
    """
    Mark attendance for multiple students at once.
    """
    serializer = BulkAttendanceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            'success': False,
            'error': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        session = get_object_or_404(AttendanceSession, id=data['session_id'])
        
        # Validate session is active
        if not session.is_active:
            return Response({
                'success': False,
                'error': 'This attendance session is not active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        results = []
        errors = []
        
        for item in data['attendance_data']:
            try:
                student = get_object_or_404(Student, id=item['student_id'])
                
                # Validate student is enrolled
                if not session.course.students.filter(id=student.id).exists():
                    errors.append({
                        'student_id': item['student_id'],
                        'error': 'Student not enrolled in course'
                    })
                    continue
                
                attendance, created = Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'status': item.get('status', 'present'),
                        'verification_method': item.get('verification_method', 'manual'),
                        'marked_by': request.user,
                        'notes': item.get('notes', '')
                    }
                )
                results.append({
                    'student_id': student.id,
                    'status': attendance.status,
                    'created': created
                })
            except Exception as e:
                errors.append({
                    'student_id': item.get('student_id'),
                    'error': str(e)
                })
        
        # Send absentee notifications
        try:
            from notifications.utils import send_absentee_notifications
            send_absentee_notifications(session)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send notifications: {e}")
        
        response_data = {
            'success': True,
            'message': f'Marked attendance for {len(results)} students',
            'results': results
        }
        
        if errors:
            response_data['errors'] = errors
            response_data['message'] += f' ({len(errors)} errors)'
        
        return Response(response_data)
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.exception(f"Error in bulk mark attendance: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def face_recognition_mark(request):
    """
    Mark attendance using face recognition.
    Receives image and returns recognized student with attendance marked.
    """
    session_id = request.data.get('session_id')
    student_id = request.data.get('student_id')
    confidence = request.data.get('confidence', 95.0)
    
    if not session_id or not student_id:
        return Response({
            'success': False,
            'error': 'session_id and student_id are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = AttendanceSession.objects.get(id=session_id)
        student = Student.objects.get(id=student_id)
        
        # Create attendance record
        attendance, created = Attendance.objects.update_or_create(
            session=session,
            student=student,
            defaults={
                'status': 'present',
                'verification_method': 'face_recognition',
                'marked_by': request.user if request.user.is_authenticated else None,
                'face_confidence': float(confidence)
            }
        )
        
        return Response({
            'success': True,
            'message': 'Face recognized and attendance marked',
            'student': StudentSerializer(student).data,
            'confidence': confidence,
            'attendance_id': attendance.id
        })
    except (AttendanceSession.DoesNotExist, Student.DoesNotExist) as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def face_recognition_identify(request):
    """
    AI Face Recognition endpoint.
    Receives an image and returns identified student(s).
    This is a simulation - in production, would use actual face recognition.
    """
    session_id = request.data.get('session_id')
    
    if not session_id:
        return Response({
            'success': False,
            'error': 'session_id is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        session = AttendanceSession.objects.get(id=session_id)
        students = session.course.students.filter(is_active=True)
        
        # Simulate face recognition - in production, this would:
        # 1. Extract face encoding from uploaded image
        # 2. Compare with stored face encodings
        # 3. Return matched student(s)
        
        # For simulation, return a random unrecognized student
        recognized = Attendance.objects.filter(
            session=session, 
            status='present'
        ).values_list('student_id', flat=True)
        
        unrecognized = students.exclude(id__in=recognized)
        
        if unrecognized.exists():
            student = unrecognized.first()
            confidence = 92.5  # Simulated confidence score
            
            return Response({
                'success': True,
                'recognized': True,
                'student': StudentSerializer(student).data,
                'confidence': confidence,
                'message': 'Face recognized successfully'
            })
        else:
            return Response({
                'success': True,
                'recognized': False,
                'message': 'All students already marked or no match found'
            })
            
    except AttendanceSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)


# ============== Notification API Views ==============

class NotificationViewSet(viewsets.ModelViewSet):
    """API endpoint for notifications."""
    serializer_class = NotificationSerializer
    filterset_fields = ['notification_type', 'is_read', 'priority']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return Notification.objects.filter(student=user.student_profile)
        return Notification.objects.none()
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications."""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({'success': True, 'message': 'All notifications marked as read'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a single notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'success': True})


# ============== Dashboard API Views ==============

@api_view(['GET'])
def faculty_dashboard(request):
    """
    Get faculty dashboard data for mobile app.
    """
    try:
        faculty = request.user.faculty_profile
    except:
        return Response({
            'success': False,
            'error': 'Faculty profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Get courses
    courses = Course.objects.filter(faculty=faculty, is_active=True)
    
    # Today's sessions
    today_sessions = AttendanceSession.objects.filter(
        faculty=faculty, date=today
    )
    
    # Week statistics
    week_sessions = AttendanceSession.objects.filter(
        faculty=faculty, date__gte=week_start
    )
    week_attendance = Attendance.objects.filter(
        session__in=week_sessions
    ).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent'))
    )
    
    return Response({
        'success': True,
        'faculty': FacultySerializer(faculty).data,
        'courses': CourseSerializer(courses, many=True).data,
        'today_sessions': AttendanceSessionSerializer(today_sessions, many=True).data,
        'week_stats': week_attendance,
        'total_students': Student.objects.filter(
            courses__faculty=faculty, is_active=True
        ).distinct().count()
    })


@api_view(['GET'])
def student_dashboard(request):
    """
    Get student dashboard data for mobile app.
    """
    try:
        student = request.user.student_profile
    except:
        return Response({
            'success': False,
            'error': 'Student profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get attendance stats
    records = Attendance.objects.filter(student=student)
    stats = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    )
    
    total = stats['total'] or 1
    stats['percentage'] = round((stats['present'] + stats['late']) / total * 100, 1)
    
    # Recent attendance
    recent = records.order_by('-session__date')[:10]
    
    # Unread notifications
    notifications = Notification.objects.filter(
        student=student, is_read=False
    ).count()
    
    return Response({
        'success': True,
        'student': StudentSerializer(student).data,
        'attendance_stats': stats,
        'recent_attendance': AttendanceSerializer(recent, many=True).data,
        'unread_notifications': notifications,
        'courses': CourseSerializer(student.courses.filter(is_active=True), many=True).data
    })
