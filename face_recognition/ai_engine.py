"""
AI Face Recognition Engine for Smart Campus Attendance System.

This module provides face detection, encoding, and recognition capabilities.
In production, this would use actual face_recognition library with dlib.
For demonstration, it includes simulation capabilities.
"""

import os
import logging
import pickle
import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import face_recognition library
try:
    import face_recognition as fr
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition library not available. Using simulation mode.")


class FaceRecognitionEngine:
    """
    AI-powered face recognition engine for attendance system.
    
    Features:
    - Face detection in images
    - Face encoding generation
    - Face matching against known encodings
    - Confidence score calculation
    """
    
    def __init__(self):
        self.tolerance = getattr(settings, 'FACE_RECOGNITION_TOLERANCE', 0.6)
        self.model = getattr(settings, 'FACE_ENCODING_MODEL', 'hog')
        self.known_encodings = {}
        self.simulation_mode = not FACE_RECOGNITION_AVAILABLE
    
    def detect_faces(self, image_path):
        """
        Detect faces in an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of face locations (top, right, bottom, left)
        """
        if self.simulation_mode:
            # Simulate face detection
            logger.info(f"[SIMULATION] Detecting faces in {image_path}")
            return [(50, 200, 200, 50)]  # Simulated face location
        
        try:
            image = fr.load_image_file(image_path)
            face_locations = fr.face_locations(image, model=self.model)
            logger.info(f"Detected {len(face_locations)} face(s) in image")
            return face_locations
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def encode_face(self, image_path):
        """
        Generate face encoding from an image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Face encoding (numpy array) or None if no face found
        """
        if self.simulation_mode:
            # Generate simulated encoding
            logger.info(f"[SIMULATION] Generating face encoding for {image_path}")
            return np.random.rand(128)  # Simulated 128-dimensional encoding
        
        try:
            image = fr.load_image_file(image_path)
            face_encodings = fr.face_encodings(image)
            
            if face_encodings:
                logger.info("Face encoding generated successfully")
                return face_encodings[0]
            else:
                logger.warning("No face found in image")
                return None
        except Exception as e:
            logger.error(f"Error encoding face: {e}")
            return None
    
    def compare_faces(self, known_encoding, unknown_encoding):
        """
        Compare two face encodings.
        
        Args:
            known_encoding: Known face encoding
            unknown_encoding: Unknown face encoding to compare
            
        Returns:
            Tuple of (is_match, confidence_score)
        """
        if self.simulation_mode:
            # Simulate comparison with random confidence
            confidence = np.random.uniform(0.85, 0.99)
            is_match = confidence > (1 - self.tolerance)
            return is_match, confidence * 100
        
        try:
            # Calculate face distance
            face_distance = fr.face_distance([known_encoding], unknown_encoding)[0]
            
            # Convert distance to confidence score (0-100%)
            confidence = (1 - face_distance) * 100
            is_match = face_distance <= self.tolerance
            
            return is_match, confidence
        except Exception as e:
            logger.error(f"Error comparing faces: {e}")
            return False, 0.0
    
    def identify_student(self, image_path, students):
        """
        Identify a student from an image.
        
        Args:
            image_path: Path to the image file
            students: QuerySet of Student objects with face_encoding
            
        Returns:
            Tuple of (student, confidence) or (None, 0) if not found
        """
        unknown_encoding = self.encode_face(image_path)
        
        if unknown_encoding is None:
            return None, 0
        
        best_match = None
        best_confidence = 0
        
        for student in students:
            if student.face_encoding:
                try:
                    known_encoding = pickle.loads(student.face_encoding)
                    is_match, confidence = self.compare_faces(known_encoding, unknown_encoding)
                    
                    if is_match and confidence > best_confidence:
                        best_match = student
                        best_confidence = confidence
                except Exception as e:
                    logger.error(f"Error comparing with student {student.student_id}: {e}")
        
        if self.simulation_mode and students.exists():
            # In simulation mode, return a random student with high confidence
            import random
            student = random.choice(list(students))
            confidence = np.random.uniform(88, 98)
            return student, confidence
        
        return best_match, best_confidence
    
    def register_student_face(self, student, image_path):
        """
        Register a student's face encoding.
        
        Args:
            student: Student model instance
            image_path: Path to the student's face image
            
        Returns:
            Boolean indicating success
        """
        encoding = self.encode_face(image_path)
        
        if encoding is not None:
            # Store encoding as binary
            student.face_encoding = pickle.dumps(encoding)
            student.save()
            logger.info(f"Face encoding registered for student {student.student_id}")
            return True
        
        return False
    
    def batch_identify(self, image_path, students):
        """
        Identify multiple faces in a single image (e.g., classroom photo).
        
        Args:
            image_path: Path to the image file
            students: QuerySet of Student objects
            
        Returns:
            List of (student, confidence, face_location) tuples
        """
        if self.simulation_mode:
            # Simulate batch identification
            import random
            results = []
            num_faces = random.randint(1, min(5, students.count()))
            selected = random.sample(list(students), num_faces)
            
            for i, student in enumerate(selected):
                confidence = np.random.uniform(85, 98)
                location = (50 + i*100, 150 + i*50, 150 + i*100, 50 + i*50)
                results.append((student, confidence, location))
            
            return results
        
        results = []
        
        try:
            image = fr.load_image_file(image_path)
            face_locations = fr.face_locations(image, model=self.model)
            face_encodings = fr.face_encodings(image, face_locations)
            
            for encoding, location in zip(face_encodings, face_locations):
                best_match = None
                best_confidence = 0
                
                for student in students:
                    if student.face_encoding:
                        known_encoding = pickle.loads(student.face_encoding)
                        is_match, confidence = self.compare_faces(known_encoding, encoding)
                        
                        if is_match and confidence > best_confidence:
                            best_match = student
                            best_confidence = confidence
                
                if best_match:
                    results.append((best_match, best_confidence, location))
        
        except Exception as e:
            logger.error(f"Error in batch identification: {e}")
        
        return results


class AutomatedAbsenteeDetector:
    """
    Automated system for detecting and flagging absent students.
    
    Features:
    - Automatic detection of students not marked present
    - Threshold-based absence flagging
    - Integration with notification system
    """
    
    def __init__(self):
        self.attendance_threshold = 75  # Minimum required attendance %
    
    def detect_session_absentees(self, session):
        """
        Detect all absent students for a session.
        
        Args:
            session: AttendanceSession instance
            
        Returns:
            List of absent Student objects
        """
        from attendance.models import Attendance
        
        # Get all students enrolled in the course
        enrolled_students = set(session.course.students.filter(is_active=True))
        
        # Get students marked present or late
        present_students = set(
            Attendance.objects.filter(
                session=session,
                status__in=['present', 'late']
            ).values_list('student', flat=True)
        )
        
        # Find absent students
        absent_students = enrolled_students - present_students
        
        logger.info(f"Detected {len(absent_students)} absent students for session {session.id}")
        return list(absent_students)
    
    def auto_mark_absentees(self, session, marked_by=None):
        """
        Automatically mark remaining students as absent.
        
        Args:
            session: AttendanceSession instance
            marked_by: User who triggered the auto-marking
            
        Returns:
            Number of students marked absent
        """
        from attendance.models import Attendance, Student
        
        # Get enrolled students
        enrolled = session.course.students.filter(is_active=True)
        
        # Get already marked students
        marked = Attendance.objects.filter(session=session).values_list('student_id', flat=True)
        
        # Find unmarked students
        unmarked = enrolled.exclude(id__in=marked)
        
        count = 0
        for student in unmarked:
            Attendance.objects.create(
                session=session,
                student=student,
                status='absent',
                verification_method='manual',
                marked_by=marked_by,
                notes='Auto-marked as absent'
            )
            count += 1
        
        logger.info(f"Auto-marked {count} students as absent for session {session.id}")
        return count
    
    def check_low_attendance_students(self, course=None):
        """
        Find students with attendance below threshold.
        
        Args:
            course: Optional Course to filter by
            
        Returns:
            List of (student, attendance_percentage) tuples
        """
        from attendance.models import Student, Attendance
        from django.db.models import Count, Q
        
        students = Student.objects.filter(is_active=True)
        if course:
            students = students.filter(courses=course)
        
        low_attendance = []
        
        for student in students:
            records = Attendance.objects.filter(student=student)
            if course:
                records = records.filter(session__course=course)
            
            stats = records.aggregate(
                total=Count('id'),
                present=Count('id', filter=Q(status__in=['present', 'late']))
            )
            
            if stats['total'] > 0:
                percentage = (stats['present'] / stats['total']) * 100
                if percentage < self.attendance_threshold:
                    low_attendance.append((student, percentage))
        
        return low_attendance


class InstantAttendanceUpdater:
    """
    Real-time attendance update system.
    
    Features:
    - WebSocket-ready updates
    - Instant notification triggers
    - Live dashboard updates
    """
    
    def __init__(self):
        self.callbacks = []
    
    def register_callback(self, callback):
        """Register a callback for attendance updates."""
        self.callbacks.append(callback)
    
    def notify_update(self, attendance):
        """
        Notify all registered callbacks of an attendance update.
        
        Args:
            attendance: Attendance instance that was updated
        """
        update_data = {
            'type': 'attendance_update',
            'session_id': str(attendance.session.id),
            'student_id': attendance.student.id,
            'student_name': attendance.student.full_name,
            'status': attendance.status,
            'verification_method': attendance.verification_method,
            'timestamp': attendance.marked_at.isoformat(),
        }
        
        for callback in self.callbacks:
            try:
                callback(update_data)
            except Exception as e:
                logger.error(f"Error in attendance update callback: {e}")
        
        # Trigger notification if absent
        if attendance.status == 'absent':
            from notifications.utils import send_single_absentee_notification
            send_single_absentee_notification(attendance)
        
        logger.info(f"Instant update sent for attendance {attendance.id}")
        return update_data
    
    def get_session_stats(self, session):
        """
        Get real-time statistics for a session.
        
        Args:
            session: AttendanceSession instance
            
        Returns:
            Dictionary with attendance statistics
        """
        from attendance.models import Attendance
        from django.db.models import Count, Q
        
        stats = Attendance.objects.filter(session=session).aggregate(
            total=Count('id'),
            present=Count('id', filter=Q(status='present')),
            absent=Count('id', filter=Q(status='absent')),
            late=Count('id', filter=Q(status='late')),
            excused=Count('id', filter=Q(status='excused'))
        )
        
        total = stats['total'] or 1
        stats['percentage'] = round((stats['present'] + stats['late']) / total * 100, 1)
        
        return stats


# Global instances
face_engine = FaceRecognitionEngine()
absentee_detector = AutomatedAbsenteeDetector()
attendance_updater = InstantAttendanceUpdater()
