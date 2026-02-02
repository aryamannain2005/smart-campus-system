# Smart Campus API Documentation

## Base URL
```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Authentication

All API endpoints (except login) require token authentication.

### Headers
```
Authorization: Token <your-auth-token>
Content-Type: application/json
```

---

## Authentication Endpoints

### Login
**POST** `/api/auth/login/`

Authenticate user and receive token.

**Request Body:**
```json
{
  "username": "student1",
  "password": "student123",
  "device_type": "ios",
  "device_token": "optional-push-notification-token"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_type": "student",
  "user": {
    "id": 1,
    "username": "student1",
    "student_id": "STU2024001",
    "roll_number": "21CS101",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "email": "john.doe@university.edu",
    "phone": "+1234567890",
    "department": {
      "id": 1,
      "name": "Computer Science",
      "code": "CS"
    },
    "semester": 3,
    "section": "A",
    "profile_image": "/media/student_images/john_doe.jpg",
    "is_active": true
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
```

### Logout
**POST** `/api/auth/logout/`

Invalidate the current authentication token.

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Dashboard Endpoints

### Student Dashboard
**GET** `/api/dashboard/student/`

Get comprehensive dashboard data for logged-in student.

**Response (200 OK):**
```json
{
  "success": true,
  "student": {
    "id": 1,
    "student_id": "STU2024001",
    "full_name": "John Doe",
    "email": "john.doe@university.edu",
    "department": {...},
    "semester": 3,
    "section": "A"
  },
  "attendance_stats": {
    "total": 45,
    "present": 38,
    "absent": 5,
    "late": 2,
    "percentage": 88.9
  },
  "recent_attendance": [
    {
      "id": 123,
      "session": "uuid-here",
      "student": {...},
      "status": "present",
      "verification_method": "mobile_gps",
      "marked_at": "2026-02-01T10:30:00Z",
      "session_info": {
        "course_code": "CS301",
        "course_name": "Data Structures",
        "date": "2026-02-01"
      }
    }
  ],
  "unread_notifications": 3,
  "courses": [
    {
      "id": 1,
      "code": "CS301",
      "name": "Data Structures",
      "department": {...},
      "faculty": {...},
      "semester": 3,
      "credits": 4,
      "student_count": 45,
      "is_active": true
    }
  ]
}
```

### Faculty Dashboard
**GET** `/api/dashboard/faculty/`

Get comprehensive dashboard data for logged-in faculty.

**Response (200 OK):**
```json
{
  "success": true,
  "faculty": {
    "id": 1,
    "employee_id": "FAC001",
    "full_name": "Dr. Jane Smith",
    "department": {...},
    "designation": "Associate Professor"
  },
  "courses": [...],
  "today_sessions": [...],
  "week_stats": {
    "total": 150,
    "present": 135,
    "absent": 15
  },
  "total_students": 120
}
```

---

## Attendance Endpoints

### Mark Attendance
**POST** `/api/attendance/mark/`

Mark attendance for a single student.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": 1,
  "status": "present",
  "verification_method": "mobile_gps",
  "location_lat": 37.7749,
  "location_lng": -122.4194,
  "notes": "Optional notes"
}
```

**Parameters:**
- `session_id` (UUID, required): Attendance session ID
- `student_id` (integer, required): Student ID
- `status` (string, required): One of: `present`, `absent`, `late`, `excused`
- `verification_method` (string, optional): One of: `manual`, `face_recognition`, `mobile_gps`, `qr_scan`
- `location_lat` (float, optional): GPS latitude
- `location_lng` (float, optional): GPS longitude
- `notes` (string, optional): Additional notes

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Attendance marked successfully",
  "attendance_id": 456,
  "created": true
}
```

### Bulk Mark Attendance
**POST** `/api/attendance/bulk-mark/`

Mark attendance for multiple students at once.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "attendance_data": [
    {
      "student_id": 1,
      "status": "present",
      "verification_method": "manual"
    },
    {
      "student_id": 2,
      "status": "absent"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Marked attendance for 2 students",
  "results": [
    {
      "student_id": 1,
      "status": "present",
      "created": true
    },
    {
      "student_id": 2,
      "status": "absent",
      "created": false
    }
  ]
}
```

---

## Session Endpoints

### List Sessions
**GET** `/api/sessions/`

Get list of attendance sessions (paginated).

**Query Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `page_size` (integer, optional): Items per page (default: 20)

**Response (200 OK):**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/sessions/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "course": {
        "id": 1,
        "code": "CS301",
        "name": "Data Structures",
        "department": {...},
        "faculty": {...}
      },
      "faculty": {...},
      "date": "2026-02-01",
      "start_time": "10:00:00",
      "end_time": "11:00:00",
      "session_type": "manual",
      "is_active": true,
      "attendance_count": 42
    }
  ]
}
```

### Get Session Details
**GET** `/api/sessions/{session_id}/`

Get details of a specific session.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "course": {...},
  "faculty": {...},
  "date": "2026-02-01",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "session_type": "manual",
  "is_active": true,
  "attendance_count": 42
}
```

### Get Session Attendance List
**GET** `/api/sessions/{session_id}/attendance_list/`

Get all attendance records for a session.

**Response (200 OK):**
```json
[
  {
    "id": 123,
    "session": "550e8400-e29b-41d4-a716-446655440000",
    "student": {
      "id": 1,
      "student_id": "STU2024001",
      "roll_number": "21CS101",
      "full_name": "John Doe"
    },
    "status": "present",
    "verification_method": "mobile_gps",
    "marked_at": "2026-02-01T10:30:00Z",
    "face_confidence": null,
    "location_lat": 37.7749,
    "location_lng": -122.4194,
    "notes": "",
    "session_info": {
      "course_code": "CS301",
      "course_name": "Data Structures",
      "date": "2026-02-01"
    }
  }
]
```

### Get Session Statistics
**GET** `/api/sessions/{session_id}/stats/`

Get attendance statistics for a session.

**Response (200 OK):**
```json
{
  "total": 45,
  "present": 38,
  "absent": 5,
  "late": 2,
  "excused": 0,
  "attendance_percentage": 88.9
}
```

### Create Session
**POST** `/api/sessions/`

Create a new attendance session (Faculty only).

**Request Body:**
```json
{
  "course": 1,
  "date": "2026-02-01",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "session_type": "manual"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "course": 1,
  "date": "2026-02-01",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "session_type": "manual"
}
```

---

## Face Recognition Endpoints

### Identify Student (Face Recognition)
**POST** `/api/face-recognition/identify/`

Identify a student from an uploaded image.

**Request Body (multipart/form-data):**
- `session_id` (UUID): Session ID
- `image` (file): Image file containing student's face
- `location_lat` (float, optional): GPS latitude
- `location_lng` (float, optional): GPS longitude

**Response (200 OK - Recognized):**
```json
{
  "success": true,
  "recognized": true,
  "student": {
    "id": 1,
    "student_id": "STU2024001",
    "full_name": "John Doe",
    "email": "john.doe@university.edu"
  },
  "confidence": 92.5,
  "message": "Face recognized successfully"
}
```

**Response (200 OK - Not Recognized):**
```json
{
  "success": true,
  "recognized": false,
  "message": "No match found"
}
```

### Mark Attendance via Face Recognition
**POST** `/api/face-recognition/mark/`

Mark attendance after face recognition.

**Request Body:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": 1,
  "confidence": 92.5
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Face recognized and attendance marked",
  "student": {...},
  "confidence": 92.5,
  "attendance_id": 456
}
```

---

## Student Endpoints

### List Students
**GET** `/api/students/`

Get list of active students (paginated).

**Response (200 OK):**
```json
{
  "count": 500,
  "next": "http://localhost:8000/api/students/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "student_id": "STU2024001",
      "roll_number": "21CS101",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe",
      "email": "john.doe@university.edu",
      "phone": "+1234567890",
      "department": {...},
      "semester": 3,
      "section": "A",
      "profile_image": "/media/student_images/john_doe.jpg",
      "is_active": true
    }
  ]
}
```

### Get Student Details
**GET** `/api/students/{student_id}/`

Get details of a specific student.

### Get Student Attendance Stats
**GET** `/api/students/{student_id}/attendance_stats/`

Get attendance statistics for a student.

**Response (200 OK):**
```json
{
  "total_classes": 45,
  "present_count": 38,
  "absent_count": 5,
  "late_count": 2,
  "attendance_percentage": 88.9,
  "course_wise_stats": [
    {
      "course_code": "CS301",
      "course_name": "Data Structures",
      "total": 15,
      "present": 13,
      "absent": 2,
      "percentage": 86.7
    }
  ]
}
```

### Get Student Attendance History
**GET** `/api/students/{student_id}/attendance_history/`

Get recent attendance records for a student (last 50).

---

## Course Endpoints

### List Courses
**GET** `/api/courses/`

Get list of active courses.

### Get Course Details
**GET** `/api/courses/{course_id}/`

### Get Course Students
**GET** `/api/courses/{course_id}/students/`

Get all students enrolled in a course.

### Get Course Sessions
**GET** `/api/courses/{course_id}/sessions/`

Get recent attendance sessions for a course (last 20).

---

## Notification Endpoints

### List Notifications
**GET** `/api/notifications/`

Get notifications for logged-in student (paginated).

**Response (200 OK):**
```json
{
  "count": 25,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "notification_type": "absence",
      "title": "Absence Alert",
      "message": "You were marked absent in CS301 - Data Structures on 2026-02-01",
      "is_read": false,
      "created_at": "2026-02-01T11:00:00Z",
      "read_at": null
    }
  ]
}
```

### Get Unread Notifications
**GET** `/api/notifications/unread/`

Get only unread notifications.

### Mark Notification as Read
**POST** `/api/notifications/{notification_id}/mark_read/`

**Response (200 OK):**
```json
{
  "success": true
}
```

### Mark All Notifications as Read
**POST** `/api/notifications/mark_all_read/`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "field_name": [
    "This field is required."
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 429 Too Many Requests
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### 500 Internal Server Error
```json
{
  "detail": "A server error occurred."
}
```

---

## Rate Limiting

- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour

---

## Pagination

All list endpoints support pagination:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Format:**
```json
{
  "count": 100,
  "next": "http://api.example.com/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## iOS Swift Example

### Complete API Client

```swift
import Foundation

class SmartCampusAPI {
    static let shared = SmartCampusAPI()
    
    private let baseURL = "https://your-domain.com/api/"
    private var authToken: String?
    
    // MARK: - Authentication
    
    func login(username: String, password: String) async throws -> AuthResponse {
        let endpoint = "auth/login/"
        let body: [String: Any] = [
            "username": username,
            "password": password,
            "device_type": "ios"
        ]
        
        let response: AuthResponse = try await post(endpoint: endpoint, body: body, requiresAuth: false)
        self.authToken = response.token
        return response
    }
    
    func logout() async throws {
        let endpoint = "auth/logout/"
        let _: EmptyResponse = try await post(endpoint: endpoint, body: [:], requiresAuth: true)
        self.authToken = nil
    }
    
    // MARK: - Dashboard
    
    func getStudentDashboard() async throws -> StudentDashboard {
        return try await get(endpoint: "dashboard/student/")
    }
    
    // MARK: - Attendance
    
    func markAttendance(sessionId: String, studentId: Int, status: String, location: CLLocationCoordinate2D?) async throws -> AttendanceResponse {
        let endpoint = "attendance/mark/"
        var body: [String: Any] = [
            "session_id": sessionId,
            "student_id": studentId,
            "status": status,
            "verification_method": "mobile_gps"
        ]
        
        if let location = location {
            body["location_lat"] = location.latitude
            body["location_lng"] = location.longitude
        }
        
        return try await post(endpoint: endpoint, body: body, requiresAuth: true)
    }
    
    // MARK: - Notifications
    
    func getNotifications(page: Int = 1) async throws -> PaginatedResponse<Notification> {
        return try await get(endpoint: "notifications/?page=\(page)")
    }
    
    func markAllNotificationsRead() async throws {
        let _: EmptyResponse = try await post(endpoint: "notifications/mark_all_read/", body: [:], requiresAuth: true)
    }
    
    // MARK: - Generic Request Methods
    
    private func get<T: Decodable>(endpoint: String) async throws -> T {
        guard let url = URL(string: baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let token = authToken {
            request.setValue("Token \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
    
    private func post<T: Decodable>(endpoint: String, body: [String: Any], requiresAuth: Bool) async throws -> T {
        guard let url = URL(string: baseURL + endpoint) else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if requiresAuth, let token = authToken {
            request.setValue("Token \(token)", forHTTPHeaderField: "Authorization")
        }
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        
        guard (200...299).contains(httpResponse.statusCode) else {
            throw APIError.httpError(httpResponse.statusCode)
        }
        
        return try JSONDecoder().decode(T.self, from: data)
    }
}

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case httpError(Int)
}
```

---

## Testing with Postman

1. Import this collection into Postman
2. Set environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (will be set after login)
3. Run the login request first to get your token
4. Token will be automatically used in subsequent requests

---

## Support

For questions or issues:
- Review the deployment guide: IOS_DEPLOYMENT_GUIDE.md
- Check server logs for errors
- Test endpoints with curl or Postman first
