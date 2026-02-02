"""
Views for Face Recognition Module.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
import os
import tempfile

from attendance.models import Student, AttendanceSession, Attendance
from .ai_engine import face_engine, absentee_detector, attendance_updater


@login_required
def face_recognition_dashboard(request):
    """Dashboard for face recognition system."""
    context = {
        'simulation_mode': face_engine.simulation_mode,
        'tolerance': face_engine.tolerance,
        'model': face_engine.model,
    }
    return render(request, 'face_recognition/dashboard.html', context)


@login_required
@require_POST
def process_face_image(request):
    """
    Process uploaded face image for recognition.
    
    Expects:
    - image: Image file
    - session_id: UUID of the attendance session
    """
    session_id = request.POST.get('session_id')
    image = request.FILES.get('image')
    
    if not session_id or not image:
        return JsonResponse({
            'success': False,
            'error': 'session_id and image are required'
        }, status=400)
    
    try:
        session = AttendanceSession.objects.get(id=session_id)
        students = session.course.students.filter(is_active=True)
        
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        try:
            # Identify student
            student, confidence = face_engine.identify_student(tmp_path, students)
            
            if student:
                # Mark attendance
                attendance, created = Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'status': 'present',
                        'verification_method': 'face_recognition',
                        'marked_by': request.user,
                        'face_confidence': confidence
                    }
                )
                
                # Trigger instant update
                attendance_updater.notify_update(attendance)
                
                return JsonResponse({
                    'success': True,
                    'recognized': True,
                    'student': {
                        'id': student.id,
                        'student_id': student.student_id,
                        'name': student.full_name,
                        'roll_number': student.roll_number
                    },
                    'confidence': round(confidence, 1),
                    'attendance_id': attendance.id,
                    'created': created
                })
            else:
                return JsonResponse({
                    'success': True,
                    'recognized': False,
                    'message': 'No matching student found'
                })
        finally:
            # Clean up temp file
            os.unlink(tmp_path)
            
    except AttendanceSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_POST
def register_student_face(request):
    """
    Register a student's face for recognition.
    
    Expects:
    - student_id: ID of the student
    - image: Face image file
    """
    student_id = request.POST.get('student_id')
    image = request.FILES.get('image')
    
    if not student_id or not image:
        return JsonResponse({
            'success': False,
            'error': 'student_id and image are required'
        }, status=400)
    
    try:
        student = Student.objects.get(id=student_id)
        
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        try:
            success = face_engine.register_student_face(student, tmp_path)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': f'Face registered for {student.full_name}'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'No face detected in image'
                })
        finally:
            os.unlink(tmp_path)
            
    except Student.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Student not found'
        }, status=404)


@login_required
def auto_mark_absentees(request, session_id):
    """
    Automatically mark remaining students as absent.
    """
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    count = absentee_detector.auto_mark_absentees(session, marked_by=request.user)
    
    # Send notifications for absentees
    from notifications.utils import send_absentee_notifications
    send_absentee_notifications(session)
    
    return JsonResponse({
        'success': True,
        'message': f'Marked {count} students as absent',
        'count': count
    })


@login_required
def get_session_stats_realtime(request, session_id):
    """
    Get real-time statistics for a session.
    """
    session = get_object_or_404(AttendanceSession, id=session_id)
    stats = attendance_updater.get_session_stats(session)
    
    return JsonResponse({
        'success': True,
        'stats': stats
    })


@login_required
def low_attendance_report(request):
    """
    Get list of students with low attendance.
    """
    course_id = request.GET.get('course_id')
    course = None
    
    if course_id:
        from attendance.models import Course
        course = get_object_or_404(Course, id=course_id)
    
    low_attendance = absentee_detector.check_low_attendance_students(course)
    
    data = [{
        'student_id': student.student_id,
        'name': student.full_name,
        'attendance_percentage': round(percentage, 1)
    } for student, percentage in low_attendance]
    
    return JsonResponse({
        'success': True,
        'threshold': absentee_detector.attendance_threshold,
        'students': data,
        'count': len(data)
    })


@csrf_exempt
@require_POST
def batch_face_recognition(request):
    """
    Process a classroom image to identify multiple students.
    """
    session_id = request.POST.get('session_id')
    image = request.FILES.get('image')
    
    if not session_id or not image:
        return JsonResponse({
            'success': False,
            'error': 'session_id and image are required'
        }, status=400)
    
    try:
        session = AttendanceSession.objects.get(id=session_id)
        students = session.course.students.filter(is_active=True)
        
        # Save uploaded image temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name
        
        try:
            # Batch identify
            results = face_engine.batch_identify(tmp_path, students)
            
            recognized = []
            for student, confidence, location in results:
                # Mark attendance
                attendance, created = Attendance.objects.update_or_create(
                    session=session,
                    student=student,
                    defaults={
                        'status': 'present',
                        'verification_method': 'face_recognition',
                        'face_confidence': confidence
                    }
                )
                
                recognized.append({
                    'student_id': student.student_id,
                    'name': student.full_name,
                    'confidence': round(confidence, 1),
                    'location': location
                })
            
            return JsonResponse({
                'success': True,
                'recognized_count': len(recognized),
                'students': recognized
            })
        finally:
            os.unlink(tmp_path)
            
    except AttendanceSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
