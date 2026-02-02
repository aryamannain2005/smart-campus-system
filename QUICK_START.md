# Smart Campus System - Quick Start Guide

## For Developers (Local Development)

### 1. Clone and Setup (5 minutes)

```bash
# Navigate to project
cd smart_campus_system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup (2 minutes)

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (choose a password)

# Create sample data (optional)
python create_sample_data.py
```

### 3. Run Server (1 minute)

```bash
# Start development server
python manage.py runserver

# Server will be available at:
# - Web Interface: http://localhost:8000/
# - Admin Panel: http://localhost:8000/admin/
# - API: http://localhost:8000/api/
```

### 4. Test API (2 minutes)

```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "student123"}'

# You should get a response with a token
# Use this token for authenticated requests
```

## For iOS Developers

### 1. Backend Setup

Follow the developer setup above to get the backend running locally.

### 2. Configure iOS App

```swift
// In your iOS app, set the base URL
let baseURL = "http://localhost:8000/api/"
// For testing on device, use your Mac's IP address:
// let baseURL = "http://192.168.1.XXX:8000/api/"
```

### 3. Test Authentication

```swift
// Example login request
struct LoginRequest: Codable {
    let username: String
    let password: String
}

func login() async {
    let url = URL(string: "\(baseURL)auth/login/")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let loginData = LoginRequest(username: "student1", password: "student123")
    request.httpBody = try? JSONEncoder().encode(loginData)
    
    do {
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(AuthResponse.self, from: data)
        print("Token: \(response.token)")
    } catch {
        print("Error: \(error)")
    }
}
```

### 4. Key Endpoints

- **Login:** `POST /api/auth/login/`
- **Student Dashboard:** `GET /api/dashboard/student/`
- **Mark Attendance:** `POST /api/attendance/mark/`
- **Get Notifications:** `GET /api/notifications/`

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## Default Test Accounts

After running `create_sample_data.py`:

### Admin
- Username: `admin`
- Password: `admin123`

### Faculty
- Username: `faculty1` to `faculty4`
- Password: `faculty123`

### Students
- Username: `student1` to `student50`
- Password: `student123`

## Common Tasks

### Reset Database
```bash
rm db.sqlite3
python manage.py migrate
python create_sample_data.py
```

### View Logs
```bash
tail -f logs/django.log
```

### Run Tests
```bash
python manage.py test
```

### Check for Issues
```bash
python manage.py check
```

## Project Structure

```
smart_campus_system/
├── smart_campus/          # Main project settings
│   ├── settings.py        # Configuration
│   └── urls.py           # URL routing
├── attendance/           # Attendance management
│   ├── models.py         # Database models
│   ├── views.py          # Web views
│   └── templates/        # HTML templates
├── api/                  # REST API for mobile
│   ├── views.py          # API endpoints
│   ├── serializers.py    # Data serialization
│   └── urls.py           # API routing
├── notifications/        # Notification system
├── face_recognition/     # AI face recognition
├── static/              # CSS, JS files
├── media/               # Uploaded files
└── manage.py            # Django management
```

## Next Steps

1. **Read the Documentation**
   - [IOS_DEPLOYMENT_GUIDE.md](IOS_DEPLOYMENT_GUIDE.md) - Full deployment guide
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete API reference
   - [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre-deployment checklist

2. **Explore the Admin Panel**
   - Go to http://localhost:8000/admin/
   - Login with admin credentials
   - Explore students, courses, attendance records

3. **Test the API**
   - Use Postman or curl to test endpoints
   - Try different authentication scenarios
   - Test error handling

4. **Start iOS Development**
   - Integrate API client in your iOS app
   - Implement authentication flow
   - Build attendance marking feature
   - Add notifications

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
python manage.py runserver 8001
```

### Module Not Found
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Database Locked
```bash
# Stop the server and try again
# Or delete db.sqlite3 and recreate
```

## Getting Help

- Check the logs: `tail -f logs/django.log`
- Review error messages carefully
- Search Django documentation
- Check API_DOCUMENTATION.md for endpoint details

## Production Deployment

When ready to deploy to production:

1. Follow [IOS_DEPLOYMENT_GUIDE.md](IOS_DEPLOYMENT_GUIDE.md)
2. Complete [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
3. Set up proper hosting (Heroku, AWS, etc.)
4. Configure environment variables
5. Use PostgreSQL instead of SQLite
6. Set DEBUG=False
7. Configure HTTPS/SSL

---

**Happy Coding! 🚀**
