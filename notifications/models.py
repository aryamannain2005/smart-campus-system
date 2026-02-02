"""
Models for Notification System.
Handles alerts to students and parents.
"""

from django.db import models
from django.utils import timezone
import uuid


class Notification(models.Model):
    """Notification model for students."""
    NOTIFICATION_TYPES = [
        ('absence', 'Absence Alert'),
        ('low_attendance', 'Low Attendance Warning'),
        ('attendance_marked', 'Attendance Marked'),
        ('class_reminder', 'Class Reminder'),
        ('general', 'General Notification'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'attendance.Student', 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related attendance record (if applicable)
    attendance = models.ForeignKey(
        'attendance.Attendance',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Delivery channels
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    push_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.student.full_name}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class ParentNotification(models.Model):
    """Notification model for parents."""
    NOTIFICATION_TYPES = [
        ('absence', 'Child Absence Alert'),
        ('low_attendance', 'Low Attendance Warning'),
        ('weekly_report', 'Weekly Attendance Report'),
        ('general', 'General Notification'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        'attendance.Parent',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    student = models.ForeignKey(
        'attendance.Student',
        on_delete=models.CASCADE,
        related_name='parent_notifications'
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Delivery status
    email_sent = models.BooleanField(default=False)
    sms_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.notification_type} - {self.parent.name} ({self.student.full_name})"
    
    class Meta:
        ordering = ['-created_at']


class NotificationTemplate(models.Model):
    """Templates for notification messages."""
    name = models.CharField(max_length=100, unique=True)
    notification_type = models.CharField(max_length=20)
    subject_template = models.CharField(max_length=200)
    message_template = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Available placeholders: {student_name}, {course_name}, {date}, {time}, {attendance_percentage}
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class NotificationLog(models.Model):
    """Log of all sent notifications for auditing."""
    CHANNELS = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='logs'
    )
    parent_notification = models.ForeignKey(
        ParentNotification,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='logs'
    )
    channel = models.CharField(max_length=10, choices=CHANNELS)
    recipient = models.CharField(max_length=200)  # Email or phone number
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.channel} - {self.recipient} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']
