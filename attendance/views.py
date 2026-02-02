"""
Views for Faculty Web Interface - Smart Attendance Management System.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime, timedelta

from .models import (
    Faculty, Student, Course, AttendanceSession, 
    Attendance, AttendanceReport, Department
)
from .forms import (
    FacultyLoginForm, AttendanceSessionForm, 
    ManualAttendanceForm, BulkAttendanceForm, AttendanceReportFilterForm,
    StudentRegistrationForm, StudentLoginForm, FacultyRegistrationForm,
    CourseForm
)


def home(request):
    """Landing page - redirects based on user type or shows login options."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'faculty_profile'):
            return redirect('attendance:dashboard')
        elif hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        else:
            # User has no valid profile, log them out
            logout(request)
            messages.warning(request, 'Your account has no associated profile. Please contact admin.')
    
    # Show landing page with login options for unauthenticated users
    return render(request, 'attendance/home.html')


def faculty_login(request):
    """Faculty login view."""
    if request.user.is_authenticated:
        # Check if user is a student and redirect appropriately
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        elif hasattr(request.user, 'faculty_profile'):
            return redirect('attendance:dashboard')
        else:
            # User has no valid profile, log them out
            logout(request)
    
    if request.method == 'POST':
        form = FacultyLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Verify user is a faculty member
            if hasattr(user, 'faculty_profile'):
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('attendance:dashboard')
            elif hasattr(user, 'student_profile'):
                login(request, user)
                messages.info(request, 'Redirecting to student portal...')
                return redirect('attendance:student_dashboard')
            else:
                messages.error(request, 'No profile found for this account. Please contact admin.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = FacultyLoginForm()
    
    return render(request, 'attendance/login.html', {'form': form})


def faculty_register(request):
    """Faculty self-registration view."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'faculty_profile'):
            return redirect('attendance:dashboard')
        elif hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        else:
            logout(request)
    
    if request.method == 'POST':
        form = FacultyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create User account
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create Faculty profile
            faculty = Faculty.objects.create(
                user=user,
                employee_id=form.cleaned_data['employee_id'],
                department=form.cleaned_data['department'],
                phone=form.cleaned_data.get('phone', ''),
                designation=form.cleaned_data['designation'],
                profile_image=form.cleaned_data.get('profile_image'),
                is_active=True
            )
            
            messages.success(request, f'Registration successful! Welcome, {faculty.user.get_full_name()}. You can now log in.')
            return redirect('attendance:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = FacultyRegistrationForm()
    
    return render(request, 'attendance/faculty_register.html', {'form': form})


@login_required
def faculty_logout(request):
    """Faculty logout view."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('attendance:login')


@login_required
def dashboard(request):
    """Faculty dashboard with overview statistics."""
    if not hasattr(request.user, 'faculty_profile'):
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        logout(request)
        messages.error(request, 'Access denied. Faculty account required.')
        return redirect('attendance:login')
    faculty = request.user.faculty_profile
    
    # Get faculty's courses
    courses = Course.objects.filter(faculty=faculty, is_active=True)
    
    # Today's sessions
    today = timezone.now().date()
    today_sessions = AttendanceSession.objects.filter(
        faculty=faculty, date=today
    )
    
    # Recent attendance sessions
    recent_sessions = AttendanceSession.objects.filter(
        faculty=faculty
    ).order_by('-date', '-start_time')[:10]
    
    # Statistics
    total_students = Student.objects.filter(
        courses__faculty=faculty, is_active=True
    ).distinct().count()
    
    # This week's attendance stats
    week_start = today - timedelta(days=today.weekday())
    week_sessions = AttendanceSession.objects.filter(
        faculty=faculty, date__gte=week_start
    )
    
    week_attendance = Attendance.objects.filter(
        session__in=week_sessions
    ).aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late'))
    )
    
    context = {
        'faculty': faculty,
        'courses': courses,
        'today_sessions': today_sessions,
        'recent_sessions': recent_sessions,
        'total_students': total_students,
        'week_attendance': week_attendance,
        'today': today,
    }
    return render(request, 'attendance/dashboard.html', context)


@login_required
@login_required
def create_session(request):
    """Create a new attendance session."""
    if not hasattr(request.user, 'faculty_profile'):
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        logout(request)
        messages.error(request, 'Access denied. Faculty account required.')
        return redirect('attendance:login')
    faculty = request.user.faculty_profile
    
    if request.method == 'POST':
        form = AttendanceSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.faculty = faculty
            session.save()
            messages.success(request, 'Attendance session created successfully!')
            return redirect('attendance:mark_attendance', session_id=session.id)
    else:
        form = AttendanceSessionForm()
        # Filter courses to only show faculty's courses
        form.fields['course'].queryset = Course.objects.filter(
            faculty=faculty, is_active=True
        )
    
    return render(request, 'attendance/create_session.html', {'form': form})


@login_required
def create_course(request):
    """Create a new course."""
    if not hasattr(request.user, 'faculty_profile'):
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        logout(request)
        messages.error(request, 'Access denied. Faculty account required.')
        return redirect('attendance:login')
    faculty = request.user.faculty_profile
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.faculty = faculty
            course.is_active = True
            course.save()
            messages.success(request, f'Course "{course.name}" created successfully!')
            return redirect('attendance:dashboard')
    else:
        form = CourseForm()
        # Pre-select faculty's department if available
        if faculty.department:
            form.fields['department'].initial = faculty.department
    
    return render(request, 'attendance/create_course.html', {'form': form})


@login_required
def manage_courses(request):
    """View and manage faculty's courses."""
    if not hasattr(request.user, 'faculty_profile'):
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        logout(request)
        messages.error(request, 'Access denied. Faculty account required.')
        return redirect('attendance:login')
    faculty = request.user.faculty_profile
    
    courses = Course.objects.filter(faculty=faculty).order_by('-is_active', 'code')
    
    return render(request, 'attendance/manage_courses.html', {'courses': courses})


@login_required
def enroll_students(request, course_id):
    """Enroll students in a course."""
    if not hasattr(request.user, 'faculty_profile'):
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        logout(request)
        messages.error(request, 'Access denied. Faculty account required.')
        return redirect('attendance:login')
    
    faculty = request.user.faculty_profile
    course = get_object_or_404(Course, id=course_id, faculty=faculty)
    
    # Get all students, optionally filter by department
    all_students = Student.objects.filter(is_active=True).order_by('roll_number')
    enrolled_ids = set(course.students.values_list('id', flat=True))
    
    if request.method == 'POST':
        selected_ids = request.POST.getlist('students')
        # Update enrollment
        course.students.clear()
        if selected_ids:
            students_to_enroll = Student.objects.filter(id__in=selected_ids)
            course.students.add(*students_to_enroll)
        
        messages.success(request, f'Successfully updated enrollment for {course.code}. {len(selected_ids)} students enrolled.')
        return redirect('attendance:manage_courses')
    
    context = {
        'course': course,
        'all_students': all_students,
        'enrolled_ids': enrolled_ids,
    }
    return render(request, 'attendance/enroll_students.html', context)


@login_required
def mark_attendance(request, session_id):
    """Mark attendance for a session - Manual entry."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    
    # Get students enrolled in the course
    students = session.course.students.filter(is_active=True).order_by('roll_number')
    
    # Get existing attendance records
    existing_records = {
        att.student_id: att for att in 
        Attendance.objects.filter(session=session)
    }
    
    if request.method == 'POST':
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'absent')
            notes = request.POST.get(f'notes_{student.id}', '')
            
            if student.id in existing_records:
                # Update existing record
                record = existing_records[student.id]
                record.status = status
                record.notes = notes
                record.save()
            else:
                # Create new record
                Attendance.objects.create(
                    session=session,
                    student=student,
                    status=status,
                    verification_method='manual',
                    marked_by=request.user,
                    notes=notes
                )
        
        messages.success(request, 'Attendance marked successfully!')
        
        # Trigger absentee notifications
        from notifications.utils import send_absentee_notifications
        send_absentee_notifications(session)
        
        return redirect('attendance:session_detail', session_id=session.id)
    
    context = {
        'session': session,
        'students': students,
        'existing_records': existing_records,
    }
    return render(request, 'attendance/mark_attendance.html', context)


@login_required
def face_recognition_attendance(request, session_id):
    """Face recognition based attendance marking."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    students = session.course.students.filter(is_active=True)
    
    context = {
        'session': session,
        'students': students,
    }
    return render(request, 'attendance/face_recognition.html', context)


@login_required
def session_detail(request, session_id):
    """View attendance session details."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    attendance_records = Attendance.objects.filter(session=session).select_related('student')
    
    # Calculate statistics
    stats = attendance_records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
        excused=Count('id', filter=Q(status='excused'))
    )
    
    if stats['total'] > 0:
        stats['percentage'] = round((stats['present'] + stats['late']) / stats['total'] * 100, 1)
    else:
        stats['percentage'] = 0
    
    context = {
        'session': session,
        'attendance_records': attendance_records,
        'stats': stats,
    }
    return render(request, 'attendance/session_detail.html', context)


@login_required
def attendance_reports(request):
    """View and generate attendance reports."""
    if not hasattr(request.user, 'faculty_profile'):
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        logout(request)
        messages.error(request, 'Access denied. Faculty account required.')
        return redirect('attendance:login')
    faculty = request.user.faculty_profile
    
    form = AttendanceReportFilterForm(request.GET or None)
    form.fields['course'].queryset = Course.objects.filter(faculty=faculty, is_active=True)
    
    # Base queryset
    sessions = AttendanceSession.objects.filter(faculty=faculty)
    
    # Apply filters
    if form.is_valid():
        if form.cleaned_data.get('course'):
            sessions = sessions.filter(course=form.cleaned_data['course'])
        if form.cleaned_data.get('start_date'):
            sessions = sessions.filter(date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data.get('end_date'):
            sessions = sessions.filter(date__lte=form.cleaned_data['end_date'])
    
    # Get attendance data
    report_data = []
    for session in sessions.order_by('-date')[:50]:
        records = Attendance.objects.filter(session=session)
        stats = records.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
        )
        report_data.append({
            'session': session,
            'stats': stats,
        })
    
    context = {
        'form': form,
        'report_data': report_data,
    }
    return render(request, 'attendance/reports.html', context)


@login_required
def student_attendance_detail(request, student_id):
    """View detailed attendance for a specific student."""
    student = get_object_or_404(Student, id=student_id)
    
    # Get all attendance records for this student
    records = Attendance.objects.filter(student=student).select_related(
        'session', 'session__course'
    ).order_by('-session__date')
    
    # Calculate overall statistics
    stats = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )
    
    if stats['total'] > 0:
        stats['percentage'] = round((stats['present'] + stats['late']) / stats['total'] * 100, 1)
    else:
        stats['percentage'] = 0
    
    context = {
        'student': student,
        'records': records,
        'stats': stats,
    }
    return render(request, 'attendance/student_detail.html', context)


@login_required
def course_students(request, course_id):
    """View students enrolled in a course."""
    course = get_object_or_404(Course, id=course_id)
    students = course.students.filter(is_active=True).order_by('roll_number')
    
    context = {
        'course': course,
        'students': students,
    }
    return render(request, 'attendance/course_students.html', context)


# AJAX Views for real-time updates
@login_required
@require_POST
def update_attendance_ajax(request):
    """AJAX endpoint for instant attendance updates."""
    try:
        attendance_id = request.POST.get('attendance_id')
        new_status = request.POST.get('status')
        
        attendance = get_object_or_404(Attendance, id=attendance_id)
        old_status = attendance.status
        attendance.status = new_status
        attendance.save()
        
        # Send notification if status changed to absent
        if new_status == 'absent' and old_status != 'absent':
            from notifications.utils import send_single_absentee_notification
            send_single_absentee_notification(attendance)
        
        return JsonResponse({
            'success': True,
            'message': 'Attendance updated successfully',
            'new_status': new_status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
def get_session_stats_ajax(request, session_id):
    """AJAX endpoint for getting real-time session statistics."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    records = Attendance.objects.filter(session=session)
    
    stats = records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )
    
    return JsonResponse(stats)


# ============================================
# Student Registration and Authentication Views
# ============================================

def student_register(request):
    """Student self-registration view."""
    if request.user.is_authenticated:
        # Check if user is a student
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        return redirect('attendance:dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            # Create User account
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            
            # Create Student profile
            student = Student.objects.create(
                user=user,
                student_id=form.cleaned_data['student_id'],
                roll_number=form.cleaned_data['roll_number'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data.get('phone', ''),
                department=form.cleaned_data['department'],
                semester=form.cleaned_data['semester'],
                section=form.cleaned_data['section'],
                profile_image=form.cleaned_data.get('profile_image'),
                is_active=True
            )
            
            # Process face encoding if image was uploaded
            if student.profile_image:
                try:
                    from face_recognition.utils import encode_face_from_image
                    encoding = encode_face_from_image(student.profile_image.path)
                    if encoding is not None:
                        student.face_encoding = encoding
                        student.save()
                except Exception as e:
                    # Face encoding failed, but registration continues
                    pass
            
            messages.success(request, f'Registration successful! Welcome, {student.first_name}. You can now log in.')
            return redirect('attendance:student_login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'attendance/student_register.html', {'form': form})


def student_login(request):
    """Student login view."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'student_profile'):
            return redirect('attendance:student_dashboard')
        return redirect('attendance:dashboard')
    
    if request.method == 'POST':
        form = StudentLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Verify user is a student
            if hasattr(user, 'student_profile'):
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('attendance:student_dashboard')
            else:
                messages.error(request, 'This account is not registered as a student. Please use faculty login.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    else:
        form = StudentLoginForm()
    
    return render(request, 'attendance/student_login.html', {'form': form})


@login_required
def student_dashboard(request):
    """Student dashboard showing their attendance records."""
    if not hasattr(request.user, 'student_profile'):
        if hasattr(request.user, 'faculty_profile'):
            return redirect('attendance:dashboard')
        logout(request)
        messages.error(request, 'Access denied. Student account required.')
        return redirect('attendance:student_login')
    student = request.user.student_profile
    
    # Get enrolled courses
    courses = student.courses.filter(is_active=True)
    
    # Get recent attendance records
    recent_attendance = Attendance.objects.filter(
        student=student
    ).select_related('session', 'session__course').order_by('-session__date')[:20]
    
    # Calculate overall statistics
    all_records = Attendance.objects.filter(student=student)
    stats = all_records.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    )
    
    if stats['total'] > 0:
        stats['percentage'] = round((stats['present'] + stats['late']) / stats['total'] * 100, 1)
    else:
        stats['percentage'] = 0
    
    # Per-course statistics
    course_stats = []
    for course in courses:
        course_records = all_records.filter(session__course=course)
        c_stats = course_records.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            late=Count('id', filter=Q(status='late')),
        )
        if c_stats['total'] > 0:
            c_stats['percentage'] = round((c_stats['present'] + c_stats['late']) / c_stats['total'] * 100, 1)
        else:
            c_stats['percentage'] = 0
        course_stats.append({
            'course': course,
            'stats': c_stats
        })
    
    context = {
        'student': student,
        'courses': courses,
        'recent_attendance': recent_attendance,
        'stats': stats,
        'course_stats': course_stats,
    }
    return render(request, 'attendance/student_dashboard.html', context)


@login_required
def student_profile(request):
    """View and edit student profile."""
    if not hasattr(request.user, 'student_profile'):
        if hasattr(request.user, 'faculty_profile'):
            return redirect('attendance:dashboard')
        logout(request)
        messages.error(request, 'Access denied. Student account required.')
        return redirect('attendance:student_login')
    student = request.user.student_profile
    
    if request.method == 'POST':
        # Update profile fields
        student.phone = request.POST.get('phone', student.phone)
        
        # Handle profile image update
        if 'profile_image' in request.FILES:
            student.profile_image = request.FILES['profile_image']
            # Re-encode face
            try:
                from face_recognition.utils import encode_face_from_image
                encoding = encode_face_from_image(student.profile_image.path)
                if encoding is not None:
                    student.face_encoding = encoding
            except Exception:
                pass
        
        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('attendance:student_profile')
    
    context = {
        'student': student,
    }
    return render(request, 'attendance/student_profile.html', context)
