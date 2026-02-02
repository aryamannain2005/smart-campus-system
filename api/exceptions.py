"""
Custom exception handlers for Smart Campus API.
Provides consistent error responses for iOS app.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response format
        custom_response_data = {
            'success': False,
            'error': {
                'message': str(exc),
                'status_code': response.status_code,
            }
        }
        
        # Add field-specific errors if available
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['error']['message'] = response.data['detail']
            else:
                custom_response_data['error']['fields'] = response.data
        
        response.data = custom_response_data
        
        # Log the error
        logger.error(
            f"API Error: {exc} | Status: {response.status_code} | "
            f"View: {context.get('view').__class__.__name__ if context.get('view') else 'Unknown'}"
        )
    else:
        # Handle unexpected errors
        logger.exception(f"Unhandled exception: {exc}")
        response = Response(
            {
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred. Please try again later.',
                    'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response


class APIException(Exception):
    """Base exception for API errors."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'An error occurred'
    
    def __init__(self, message=None, status_code=None):
        self.message = message or self.default_message
        if status_code:
            self.status_code = status_code
        super().__init__(self.message)


class AttendanceAlreadyMarked(APIException):
    """Raised when trying to mark attendance that's already marked."""
    status_code = status.HTTP_409_CONFLICT
    default_message = 'Attendance already marked for this session'


class SessionNotActive(APIException):
    """Raised when trying to mark attendance for inactive session."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'This attendance session is not active'


class StudentNotEnrolled(APIException):
    """Raised when student is not enrolled in the course."""
    status_code = status.HTTP_403_FORBIDDEN
    default_message = 'Student is not enrolled in this course'


class FaceRecognitionFailed(APIException):
    """Raised when face recognition fails."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'Face recognition failed. Please try again'


class InvalidLocation(APIException):
    """Raised when GPS location is invalid or out of range."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = 'Invalid location. You must be on campus to mark attendance'
