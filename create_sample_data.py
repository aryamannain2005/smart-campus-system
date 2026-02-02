#!/usr/bin/env python
"""
Script to create sample data for Smart Campus Management System.
Run this after migrations to populate the database with test data.

Usage:
    python manage.py shell < create_sample_data.py
    OR
    python manage.py runscript create_sample_data (if django-extensions installed)
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_campus.settings')
django.setup()

from django.contrib.auth.models import User
from attendance.models import (
    Department, Faculty, Parent, Student, Course, 
    AttendanceSession, Attendance
)
from notifications.models import NotificationTemplate
from django.utils import timezone
from datetime import timedelta
import random


def create_sample_data():
    print("Creating sample data for Smart Campus Management System...")
    
    # Create Departments
    print("\n1. Creating Departments...")
    departments = [
        {'name': 'Computer Science & Engineering', 'code': 'CSE'},
        {'name': 'Electronics & Communication', 'code': 'ECE'},
        {'name': 'Mechanical Engineering', 'code': 'ME'},
        {'name': 'Civil Engineering', 'code': 'CE'},
        {'name': 'Information Technology', 'code': 'IT'},
    ]
    
    dept_objects = {}
    for dept in departments:
        obj, created = Department.objects.get_or_create(
            code=dept['code'],
            defaults={'name': dept['name']}
        )
        dept_objects[dept['code']] = obj
        print(f"   {'Created' if created else 'Exists'}: {obj}")
    
    # Create Admin User
    print("\n2. Creating Admin User...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@smartcampus.edu',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print(f"   Created admin user (username: admin, password: admin123)")
    else:
        print(f"   Admin user already exists")
    
    # Create Faculty Users
    print("\n3. Creating Faculty Members...")
    faculty_data = [
        {'username': 'faculty1', 'first_name': 'Dr. Rajesh', 'last_name': 'Kumar', 'emp_id': 'FAC001', 'dept': 'CSE', 'designation': 'Professor'},
        {'username': 'faculty2', 'first_name': 'Dr. Priya', 'last_name': 'Sharma', 'emp_id': 'FAC002', 'dept': 'CSE', 'designation': 'Associate Professor'},
        {'username': 'faculty3', 'first_name': 'Dr. Amit', 'last_name': 'Singh', 'emp_id': 'FAC003', 'dept': 'ECE', 'designation': 'Assistant Professor'},
        {'username': 'faculty4', 'first_name': 'Dr. Neha', 'last_name': 'Gupta', 'emp_id': 'FAC004', 'dept': 'IT', 'designation': 'Professor'},
    ]
    
    faculty_objects = {}
    for fac in faculty_data:
        user, created = User.objects.get_or_create(
            username=fac['username'],
            defaults={
                'email': f"{fac['username']}@smartcampus.edu",
                'first_name': fac['first_name'],
                'last_name': fac['last_name'],
                'is_staff': True
            }
        )
        if created:
            user.set_password('faculty123')
            user.save()
        
        faculty, _ = Faculty.objects.get_or_create(
            employee_id=fac['emp_id'],
            defaults={
                'user': user,
                'department': dept_objects[fac['dept']],
                'designation': fac['designation'],
                'phone': f'+91 98765{random.randint(10000, 99999)}'
            }
        )
        faculty_objects[fac['emp_id']] = faculty
        print(f"   {'Created' if created else 'Exists'}: {faculty}")
    
    # Create Parents
    print("\n4. Creating Parents...")
    parent_data = [
        {'name': 'Mr. Ramesh Verma', 'email': 'ramesh.verma@email.com', 'phone': '+91 9876543210', 'relationship': 'father'},
        {'name': 'Mrs. Sunita Patel', 'email': 'sunita.patel@email.com', 'phone': '+91 9876543211', 'relationship': 'mother'},
        {'name': 'Mr. Suresh Reddy', 'email': 'suresh.reddy@email.com', 'phone': '+91 9876543212', 'relationship': 'father'},
        {'name': 'Mrs. Kavita Joshi', 'email': 'kavita.joshi@email.com', 'phone': '+91 9876543213', 'relationship': 'mother'},
        {'name': 'Mr. Prakash Mehta', 'email': 'prakash.mehta@email.com', 'phone': '+91 9876543214', 'relationship': 'guardian'},
    ]
    
    parent_objects = []
    for parent in parent_data:
        obj, created = Parent.objects.get_or_create(
            email=parent['email'],
            defaults=parent
        )
        parent_objects.append(obj)
        print(f"   {'Created' if created else 'Exists'}: {obj}")
    
    # Create Students
    print("\n5. Creating Students...")
    student_data = [
        {'student_id': 'STU2024001', 'roll': '21CSE001', 'first': 'Aarav', 'last': 'Sharma', 'dept': 'CSE', 'sem': 5, 'sec': 'A'},
        {'student_id': 'STU2024002', 'roll': '21CSE002', 'first': 'Vivaan', 'last': 'Patel', 'dept': 'CSE', 'sem': 5, 'sec': 'A'},
        {'student_id': 'STU2024003', 'roll': '21CSE003', 'first': 'Aditya', 'last': 'Singh', 'dept': 'CSE', 'sem': 5, 'sec': 'A'},
        {'student_id': 'STU2024004', 'roll': '21CSE004', 'first': 'Vihaan', 'last': 'Kumar', 'dept': 'CSE', 'sem': 5, 'sec': 'A'},
        {'student_id': 'STU2024005', 'roll': '21CSE005', 'first': 'Arjun', 'last': 'Reddy', 'dept': 'CSE', 'sem': 5, 'sec': 'A'},
        {'student_id': 'STU2024006', 'roll': '21CSE006', 'first': 'Sai', 'last': 'Verma', 'dept': 'CSE', 'sem': 5, 'sec': 'B'},
        {'student_id': 'STU2024007', 'roll': '21CSE007', 'first': 'Reyansh', 'last': 'Gupta', 'dept': 'CSE', 'sem': 5, 'sec': 'B'},
        {'student_id': 'STU2024008', 'roll': '21CSE008', 'first': 'Ayaan', 'last': 'Joshi', 'dept': 'CSE', 'sem': 5, 'sec': 'B'},
        {'student_id': 'STU2024009', 'roll': '21ECE001', 'first': 'Krishna', 'last': 'Iyer', 'dept': 'ECE', 'sem': 3, 'sec': 'A'},
        {'student_id': 'STU2024010', 'roll': '21ECE002', 'first': 'Ishaan', 'last': 'Nair', 'dept': 'ECE', 'sem': 3, 'sec': 'A'},
        {'student_id': 'STU2024011', 'roll': '21IT001', 'first': 'Ananya', 'last': 'Desai', 'dept': 'IT', 'sem': 5, 'sec': 'A'},
        {'student_id': 'STU2024012', 'roll': '21IT002', 'first': 'Diya', 'last': 'Menon', 'dept': 'IT', 'sem': 5, 'sec': 'A'},
    ]
    
    student_objects = []
    for i, stu in enumerate(student_data):
        obj, created = Student.objects.get_or_create(
            student_id=stu['student_id'],
            defaults={
                'roll_number': stu['roll'],
                'first_name': stu['first'],
                'last_name': stu['last'],
                'email': f"{stu['first'].lower()}.{stu['last'].lower()}@student.smartcampus.edu",
                'phone': f'+91 98{random.randint(10000000, 99999999)}',
                'department': dept_objects[stu['dept']],
                'semester': stu['sem'],
                'section': stu['sec'],
                'parent': parent_objects[i % len(parent_objects)] if parent_objects else None
            }
        )
        student_objects.append(obj)
        print(f"   {'Created' if created else 'Exists'}: {obj}")
    
    # Create Courses
    print("\n6. Creating Courses...")
    course_data = [
        {'code': 'CS501', 'name': 'Data Structures & Algorithms', 'dept': 'CSE', 'faculty': 'FAC001', 'sem': 5, 'credits': 4},
        {'code': 'CS502', 'name': 'Database Management Systems', 'dept': 'CSE', 'faculty': 'FAC002', 'sem': 5, 'credits': 4},
        {'code': 'CS503', 'name': 'Operating Systems', 'dept': 'CSE', 'faculty': 'FAC001', 'sem': 5, 'credits': 3},
        {'code': 'EC301', 'name': 'Digital Electronics', 'dept': 'ECE', 'faculty': 'FAC003', 'sem': 3, 'credits': 4},
        {'code': 'IT501', 'name': 'Web Technologies', 'dept': 'IT', 'faculty': 'FAC004', 'sem': 5, 'credits': 3},
    ]
    
    course_objects = {}
    for course in course_data:
        obj, created = Course.objects.get_or_create(
            code=course['code'],
            defaults={
                'name': course['name'],
                'department': dept_objects[course['dept']],
                'faculty': faculty_objects[course['faculty']],
                'semester': course['sem'],
                'credits': course['credits']
            }
        )
        course_objects[course['code']] = obj
        print(f"   {'Created' if created else 'Exists'}: {obj}")
    
    # Enroll students in courses
    print("\n7. Enrolling Students in Courses...")
    # CSE students in CSE courses
    cse_students = [s for s in student_objects if s.department.code == 'CSE']
    for course_code in ['CS501', 'CS502', 'CS503']:
        course_objects[course_code].students.add(*cse_students)
        print(f"   Enrolled {len(cse_students)} students in {course_code}")
    
    # ECE students in ECE courses
    ece_students = [s for s in student_objects if s.department.code == 'ECE']
    course_objects['EC301'].students.add(*ece_students)
    print(f"   Enrolled {len(ece_students)} students in EC301")
    
    # IT students in IT courses
    it_students = [s for s in student_objects if s.department.code == 'IT']
    course_objects['IT501'].students.add(*it_students)
    print(f"   Enrolled {len(it_students)} students in IT501")
    
    # Create Attendance Sessions and Records
    print("\n8. Creating Sample Attendance Sessions...")
    today = timezone.now().date()
    
    for course_code, course in course_objects.items():
        # Create sessions for the past week
        for days_ago in range(7, 0, -1):
            session_date = today - timedelta(days=days_ago)
            if session_date.weekday() < 5:  # Skip weekends
                session, created = AttendanceSession.objects.get_or_create(
                    course=course,
                    date=session_date,
                    defaults={
                        'faculty': course.faculty,
                        'start_time': '09:00:00',
                        'end_time': '10:00:00',
                        'session_type': random.choice(['manual', 'face_recognition']),
                        'is_active': False
                    }
                )
                
                if created:
                    # Create attendance records
                    for student in course.students.all():
                        status = random.choices(
                            ['present', 'absent', 'late'],
                            weights=[0.75, 0.15, 0.10]
                        )[0]
                        
                        Attendance.objects.get_or_create(
                            session=session,
                            student=student,
                            defaults={
                                'status': status,
                                'verification_method': session.session_type,
                                'face_confidence': random.uniform(85, 99) if session.session_type == 'face_recognition' else None
                            }
                        )
                    print(f"   Created session for {course_code} on {session_date}")
    
    # Create today's active session
    print("\n9. Creating Today's Active Session...")
    # Check if session already exists (handle duplicates gracefully)
    existing_sessions = AttendanceSession.objects.filter(
        course=course_objects['CS501'],
        date=today,
        start_time='09:00:00'
    )
    if existing_sessions.exists():
        active_session = existing_sessions.first()
        active_session.is_active = True
        active_session.save()
        print(f"   Updated existing session for CS501 today to active")
        # Clean up any duplicates
        if existing_sessions.count() > 1:
            existing_sessions.exclude(pk=active_session.pk).delete()
            print(f"   Cleaned up {existing_sessions.count()} duplicate sessions")
    else:
        active_session = AttendanceSession.objects.create(
            course=course_objects['CS501'],
            date=today,
            start_time='09:00:00',
            faculty=faculty_objects['FAC001'],
            session_type='face_recognition',
            is_active=True
        )
        print(f"   Created active session for CS501 today")
    
    # Create Notification Templates
    print("\n10. Creating Notification Templates...")
    templates = [
        {
            'name': 'Absence Alert',
            'notification_type': 'absence',
            'subject_template': 'Absence Alert: {course_name}',
            'message_template': 'Dear {student_name}, you have been marked absent for {course_name} on {date}.'
        },
        {
            'name': 'Low Attendance Warning',
            'notification_type': 'low_attendance',
            'subject_template': 'Low Attendance Warning',
            'message_template': 'Dear {student_name}, your attendance is currently at {attendance_percentage}%, which is below the required threshold.'
        },
        {
            'name': 'Attendance Confirmation',
            'notification_type': 'attendance_marked',
            'subject_template': 'Attendance Confirmed: {course_name}',
            'message_template': 'Your attendance has been marked as present for {course_name} on {date} at {time}.'
        },
    ]
    
    for template in templates:
        obj, created = NotificationTemplate.objects.get_or_create(
            name=template['name'],
            defaults=template
        )
        print(f"   {'Created' if created else 'Exists'}: {obj}")
    
    print("\n" + "="*60)
    print("Sample data creation completed!")
    print("="*60)
    print("\nLogin Credentials:")
    print("-" * 40)
    print("Admin:    username='admin'     password='admin123'")
    print("Faculty:  username='faculty1'  password='faculty123'")
    print("          username='faculty2'  password='faculty123'")
    print("          username='faculty3'  password='faculty123'")
    print("          username='faculty4'  password='faculty123'")
    print("-" * 40)
    print("\nAccess the application at: http://localhost:8000/attendance/")
    print("Admin panel at: http://localhost:8000/admin/")
    print("API endpoints at: http://localhost:8000/api/")


if __name__ == '__main__':
    create_sample_data()
