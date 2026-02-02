# iOS Deployment Guide - Smart Campus System

## Overview
This guide will help you deploy the Smart Campus backend API for iOS app integration.

## Prerequisites
- Python 3.9 or higher
- PostgreSQL (for production) or SQLite (for development)
- iOS development environment (Xcode)
- Server for hosting (AWS, Heroku, DigitalOcean, etc.)

## Quick Start (Development)

### 1. Clone and Setup
```bash
cd smart_campus_system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python create_sample_data.py  # Optional: Create test data
```

### 4. Run Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

Your API will be available at `http://localhost:8000/api/`

## Production Deployment

### Option 1: Heroku Deployment

1. **Install Heroku CLI**
```bash
brew install heroku/brew/heroku  # macOS
```

2. **Create Heroku App**
```bash
heroku create smart-campus-api
heroku addons:create heroku-postgresql:mini
```

3. **Set Environment Variables**
```bash
heroku config:set DJANGO_SECRET_KEY="your-secret-key-here"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="smart-campus-api.herokuapp.com"
```

4. **Deploy**
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 2: AWS/DigitalOcean Deployment

1. **Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql -y
```

2. **Application Setup**
```bash
# Clone repository
git clone <your-repo-url>
cd smart_campus_system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-production.txt
```

3. **PostgreSQL Setup**
```bash
sudo -u postgres psql
CREATE DATABASE smart_campus;
CREATE USER smart_campus_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE smart_campus TO smart_campus_user;
\q
```

4. **Configure Environment**
```bash
cp .env.example .env
nano .env  # Edit with your production settings
```

5. **Run Migrations**
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

6. **Setup Gunicorn**
```bash
gunicorn smart_campus.wsgi:application --bind 0.0.0.0:8000
```

7. **Configure Nginx**
Create `/etc/nginx/sites-available/smart_campus`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /path/to/smart_campus_system/staticfiles/;
    }

    location /media/ {
        alias /path/to/smart_campus_system/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

8. **Enable Site and Restart Nginx**
```bash
sudo ln -s /etc/nginx/sites-available/smart_campus /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

9. **Setup SSL with Let's Encrypt**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## iOS App Integration

### 1. Base URL Configuration
In your iOS app, set the base URL:
```swift
let baseURL = "https://your-domain.com/api/"
// For development: "http://localhost:8000/api/"
```

### 2. Authentication

**Login Request:**
```swift
struct LoginRequest: Codable {
    let username: String
    let password: String
    let deviceType: String = "ios"
}

func login(username: String, password: String) async throws -> AuthResponse {
    let url = URL(string: "\(baseURL)auth/login/")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let loginData = LoginRequest(username: username, password: password)
    request.httpBody = try JSONEncoder().encode(loginData)
    
    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(AuthResponse.self, from: data)
}
```

**Store Token:**
```swift
struct AuthResponse: Codable {
    let success: Bool
    let token: String
    let userType: String
    let user: User
}

// Save token to Keychain
Keychain.save(token: response.token)
```

**Authenticated Requests:**
```swift
func makeAuthenticatedRequest(endpoint: String) async throws -> Data {
    let url = URL(string: "\(baseURL)\(endpoint)")!
    var request = URLRequest(url: url)
    request.setValue("Token \(savedToken)", forHTTPHeaderField: "Authorization")
    
    let (data, _) = try await URLSession.shared.data(for: request)
    return data
}
```

### 3. Key API Endpoints

**Student Dashboard:**
```swift
GET /api/dashboard/student/
Headers: Authorization: Token <your-token>
```

**Mark Attendance:**
```swift
POST /api/attendance/mark/
Headers: Authorization: Token <your-token>
Body: {
    "session_id": "uuid",
    "student_id": 123,
    "status": "present",
    "verification_method": "mobile_gps",
    "location_lat": 37.7749,
    "location_lng": -122.4194
}
```

**Get Notifications:**
```swift
GET /api/notifications/
Headers: Authorization: Token <your-token>
```

### 4. Error Handling
```swift
enum APIError: Error {
    case invalidURL
    case unauthorized
    case serverError(String)
    case networkError(Error)
}

func handleAPIError(_ error: Error) {
    if let apiError = error as? APIError {
        switch apiError {
        case .unauthorized:
            // Redirect to login
            break
        case .serverError(let message):
            // Show error message
            break
        default:
            break
        }
    }
}
```

## Testing the API

### Using cURL

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "student1", "password": "student123"}'
```

**Get Dashboard (with token):**
```bash
curl -X GET http://localhost:8000/api/dashboard/student/ \
  -H "Authorization: Token your-token-here"
```

### Using Postman

1. Import the API collection (see API_DOCUMENTATION.md)
2. Set environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (will be set after login)
3. Test all endpoints

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Use HTTPS (SSL certificate)
- [ ] Set up CORS correctly for your iOS app
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor error logs
- [ ] Use environment variables for sensitive data

## Performance Optimization

1. **Database Indexing**
   - Already configured in models
   - Run `python manage.py migrate` to apply

2. **Caching** (Optional)
   ```python
   # Add to settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **Database Connection Pooling**
   ```python
   # For PostgreSQL
   DATABASES['default']['CONN_MAX_AGE'] = 600
   ```

## Monitoring

### Setup Sentry (Error Tracking)
```python
# Add to settings.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

## Troubleshooting

### Common Issues

**1. CORS Errors**
- Check CORS_ALLOWED_ORIGINS in settings
- Ensure your iOS app domain is listed

**2. Authentication Fails**
- Verify token is being sent correctly
- Check token hasn't expired
- Ensure rest_framework.authtoken is in INSTALLED_APPS

**3. Database Connection Errors**
- Verify database credentials
- Check PostgreSQL is running
- Ensure database exists

**4. Static Files Not Loading**
- Run `python manage.py collectstatic`
- Check STATIC_ROOT and STATIC_URL settings

## Support

For issues and questions:
- Check logs: `tail -f logs/django.log`
- Review API documentation: API_DOCUMENTATION.md
- Test endpoints with Postman

## Next Steps

1. Review API_DOCUMENTATION.md for complete endpoint reference
2. Set up your iOS app to consume the API
3. Implement push notifications (optional)
4. Add analytics tracking (optional)
5. Set up automated backups
