"""
Utility functions for Notification System.
Handles sending notifications to students and parents.
"""

from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_absentee_notifications(session):
    """
    Send notifications for all absent students in a session.
    Called after attendance is marked.
    """
    from attendance.models import Attendance
    from .models import Notification, ParentNotification, NotificationLog
    
    absent_records = Attendance.objects.filter(
        session=session,
        status='absent'
    ).select_related('student', 'student__parent')
    
    notifications_created = 0
    
    for record in absent_records:
        student = record.student
        
        # Create student notification
        notification = Notification.objects.create(
            student=student,
            notification_type='absence',
            priority='high',
            title=f'Absence Alert: {session.course.code}',
            message=f"""Dear {student.first_name},

You have been marked absent for the following class:

Course: {session.course.code} - {session.course.name}
Date: {session.date.strftime('%B %d, %Y')}
Time: {session.start_time.strftime('%I:%M %p')}

If you believe this is an error, please contact your faculty member.

Regards,
Smart Campus Attendance System""",
            attendance=record,
            send_email=True,
            send_push=True
        )
        
        # Simulate sending notification
        _simulate_send_notification(notification)
        notifications_created += 1
        
        # Create parent notification if parent exists
        if student.parent:
            parent_notification = ParentNotification.objects.create(
                parent=student.parent,
                student=student,
                notification_type='absence',
                title=f'Child Absence Alert: {student.full_name}',
                message=f"""Dear {student.parent.name},

This is to inform you that your child {student.full_name} was marked absent for:

Course: {session.course.code} - {session.course.name}
Date: {session.date.strftime('%B %d, %Y')}
Time: {session.start_time.strftime('%I:%M %p')}

Please contact the institution if you have any concerns.

Regards,
Smart Campus Attendance System"""
            )
            
            # Simulate sending parent notification
            _simulate_send_parent_notification(parent_notification)
    
    logger.info(f"Created {notifications_created} absence notifications for session {session.id}")
    return notifications_created


def send_single_absentee_notification(attendance):
    """
    Send notification for a single absent student.
    Called when attendance status is changed to absent.
    """
    from .models import Notification, ParentNotification
    
    if attendance.status != 'absent':
        return None
    
    student = attendance.student
    session = attendance.session
    
    # Check if notification already exists
    existing = Notification.objects.filter(
        student=student,
        attendance=attendance,
        notification_type='absence'
    ).exists()
    
    if existing:
        return None
    
    # Create student notification
    notification = Notification.objects.create(
        student=student,
        notification_type='absence',
        priority='high',
        title=f'Absence Alert: {session.course.code}',
        message=f"""Dear {student.first_name},

You have been marked absent for {session.course.code} - {session.course.name} on {session.date.strftime('%B %d, %Y')}.

If this is an error, please contact your faculty.

Smart Campus Attendance System""",
        attendance=attendance,
        send_email=True,
        send_push=True
    )
    
    _simulate_send_notification(notification)
    
    # Parent notification
    if student.parent:
        parent_notification = ParentNotification.objects.create(
            parent=student.parent,
            student=student,
            notification_type='absence',
            title=f'Child Absence: {student.full_name}',
            message=f"Your child {student.full_name} was marked absent for {session.course.code} on {session.date.strftime('%B %d, %Y')}."
        )
        _simulate_send_parent_notification(parent_notification)
    
    return notification


def send_low_attendance_warning(student, attendance_percentage, threshold=75):
    """
    Send warning notification when attendance falls below threshold.
    """
    from .models import Notification, ParentNotification
    
    if attendance_percentage >= threshold:
        return None
    
    # Create student notification
    notification = Notification.objects.create(
        student=student,
        notification_type='low_attendance',
        priority='urgent',
        title='Low Attendance Warning',
        message=f"""Dear {student.first_name},

Your current attendance is {attendance_percentage:.1f}%, which is below the required {threshold}%.

Please ensure regular attendance to avoid academic penalties.

Regards,
Smart Campus Attendance System""",
        send_email=True,
        send_sms=True,
        send_push=True
    )
    
    _simulate_send_notification(notification)
    
    # Parent notification
    if student.parent:
        parent_notification = ParentNotification.objects.create(
            parent=student.parent,
            student=student,
            notification_type='low_attendance',
            title=f'Low Attendance Warning: {student.full_name}',
            message=f"""Dear {student.parent.name},

This is to inform you that your child {student.full_name}'s attendance is currently at {attendance_percentage:.1f}%, which is below the required {threshold}%.

Please ensure regular attendance to avoid academic consequences.

Regards,
Smart Campus Attendance System"""
        )
        _simulate_send_parent_notification(parent_notification)
    
    return notification


def send_attendance_confirmation(attendance):
    """
    Send confirmation when attendance is marked (especially for face recognition).
    """
    from .models import Notification
    
    if attendance.status not in ['present', 'late']:
        return None
    
    student = attendance.student
    session = attendance.session
    
    status_text = 'present' if attendance.status == 'present' else 'late'
    method_text = attendance.get_verification_method_display()
    
    notification = Notification.objects.create(
        student=student,
        notification_type='attendance_marked',
        priority='low',
        title=f'Attendance Confirmed: {session.course.code}',
        message=f"""Your attendance has been marked as {status_text} for {session.course.code} on {session.date.strftime('%B %d, %Y')}.

Verification method: {method_text}
Time: {attendance.marked_at.strftime('%I:%M %p')}

Smart Campus Attendance System""",
        attendance=attendance,
        send_push=True
    )
    
    _simulate_send_notification(notification)
    return notification


def _simulate_send_notification(notification):
    """
    Simulate sending notification through various channels.
    In production, this would integrate with actual email/SMS/push services.
    """
    from .models import NotificationLog
    
    notification.is_sent = True
    notification.sent_at = timezone.now()
    
    # Simulate email
    if notification.send_email:
        NotificationLog.objects.create(
            notification=notification,
            channel='email',
            recipient=notification.student.email,
            status='sent',
            sent_at=timezone.now()
        )
        notification.email_sent = True
        logger.info(f"[SIMULATED] Email sent to {notification.student.email}: {notification.title}")
    
    # Simulate SMS
    if notification.send_sms and notification.student.phone:
        NotificationLog.objects.create(
            notification=notification,
            channel='sms',
            recipient=notification.student.phone,
            status='sent',
            sent_at=timezone.now()
        )
        notification.sms_sent = True
        logger.info(f"[SIMULATED] SMS sent to {notification.student.phone}: {notification.title}")
    
    # Simulate push notification
    if notification.send_push:
        NotificationLog.objects.create(
            notification=notification,
            channel='push',
            recipient=f"device_{notification.student.id}",
            status='sent',
            sent_at=timezone.now()
        )
        notification.push_sent = True
        logger.info(f"[SIMULATED] Push notification sent to student {notification.student.student_id}: {notification.title}")
    
    notification.save()


def _simulate_send_parent_notification(parent_notification):
    """
    Simulate sending notification to parent.
    """
    from .models import NotificationLog
    
    parent = parent_notification.parent
    
    # Simulate email
    NotificationLog.objects.create(
        parent_notification=parent_notification,
        channel='email',
        recipient=parent.email,
        status='sent',
        sent_at=timezone.now()
    )
    parent_notification.email_sent = True
    logger.info(f"[SIMULATED] Email sent to parent {parent.email}: {parent_notification.title}")
    
    # Simulate SMS
    if parent.phone:
        NotificationLog.objects.create(
            parent_notification=parent_notification,
            channel='sms',
            recipient=parent.phone,
            status='sent',
            sent_at=timezone.now()
        )
        parent_notification.sms_sent = True
        logger.info(f"[SIMULATED] SMS sent to parent {parent.phone}: {parent_notification.title}")
    
    parent_notification.sent_at = timezone.now()
    parent_notification.save()


def check_and_send_low_attendance_warnings():
    """
    Check all students and send warnings for those with low attendance.
    This would typically be run as a scheduled task.
    """
    from attendance.models import Student, Attendance
    from django.db.models import Count, Q
    
    threshold = 75  # Minimum required attendance percentage
    
    students = Student.objects.filter(is_active=True)
    warnings_sent = 0
    
    for student in students:
        records = Attendance.objects.filter(student=student)
        stats = records.aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status__in=['present', 'late']))
        )
        
        if stats['total'] > 0:
            percentage = (stats['present'] / stats['total']) * 100
            if percentage < threshold:
                send_low_attendance_warning(student, percentage, threshold)
                warnings_sent += 1
    
    logger.info(f"Sent {warnings_sent} low attendance warnings")
    return warnings_sent
