# Smart Campus System - iOS Deployment Checklist

## Pre-Deployment

### Code Review
- [x] All Python code is error-free
- [x] Models are properly defined
- [x] API endpoints are tested
- [x] Serializers are optimized
- [x] Error handling is comprehensive
- [x] Logging is configured

### Security
- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False in production
- [ ] Configure ALLOWED_HOSTS properly
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure CORS for your iOS app domain
- [ ] Review and update CORS_ALLOWED_ORIGINS
- [ ] Enable security middleware
- [ ] Set secure cookie flags
- [ ] Review password validators
- [ ] Set up rate limiting

### Database
- [ ] Choose production database (PostgreSQL recommended)
- [ ] Set up database credentials
- [ ] Configure database connection pooling
- [ ] Set up automated backups
- [ ] Test database migrations
- [ ] Create database indexes (already in models)

### Environment Variables
- [ ] Create .env file from .env.example
- [ ] Set DJANGO_SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Set ALLOWED_HOSTS
- [ ] Set database credentials
- [ ] Set CORS_ALLOWED_ORIGINS
- [ ] Set email settings (optional)
- [ ] Set SMS settings (optional)

### Dependencies
- [ ] Install production requirements: `pip install -r requirements-production.txt`
- [ ] Verify all packages are compatible
- [ ] Update requirements if needed

## Deployment Steps

### 1. Server Setup
- [ ] Provision server (AWS, Heroku, DigitalOcean, etc.)
- [ ] Install Python 3.9+
- [ ] Install PostgreSQL
- [ ] Install Nginx (if using VPS)
- [ ] Install Gunicorn
- [ ] Set up firewall rules

### 2. Application Setup
- [ ] Clone repository to server
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Copy .env file with production values
- [ ] Create logs directory: `mkdir -p logs`
- [ ] Set proper file permissions

### 3. Database Setup
- [ ] Create production database
- [ ] Create database user
- [ ] Grant privileges
- [ ] Update DATABASE settings in .env
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Load initial data (optional): `python create_sample_data.py`

### 4. Static Files
- [ ] Run collectstatic: `python manage.py collectstatic --noinput`
- [ ] Configure static file serving (Nginx or WhiteNoise)
- [ ] Test static files are accessible

### 5. Web Server Configuration
- [ ] Configure Gunicorn
- [ ] Set up systemd service (for VPS)
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Test server configuration
- [ ] Enable and start services

### 6. Testing
- [ ] Test API endpoints with curl/Postman
- [ ] Test authentication flow
- [ ] Test attendance marking
- [ ] Test notifications
- [ ] Test face recognition (if enabled)
- [ ] Test error handling
- [ ] Load testing (optional)

## Post-Deployment

### Monitoring
- [ ] Set up error tracking (Sentry recommended)
- [ ] Configure log rotation
- [ ] Set up uptime monitoring
- [ ] Configure performance monitoring
- [ ] Set up database monitoring

### Backups
- [ ] Configure automated database backups
- [ ] Test backup restoration
- [ ] Set up media files backup
- [ ] Document backup procedures

### Documentation
- [ ] Update API documentation with production URL
- [ ] Document deployment process
- [ ] Create runbook for common issues
- [ ] Document environment variables

### iOS App Integration
- [ ] Update base URL in iOS app
- [ ] Test login from iOS app
- [ ] Test all API endpoints from iOS app
- [ ] Test push notifications (if implemented)
- [ ] Test offline functionality
- [ ] Submit app to App Store

## Maintenance

### Regular Tasks
- [ ] Monitor error logs daily
- [ ] Review performance metrics weekly
- [ ] Update dependencies monthly
- [ ] Review security advisories
- [ ] Test backups monthly
- [ ] Review and optimize database queries

### Updates
- [ ] Create staging environment for testing
- [ ] Test updates in staging first
- [ ] Schedule maintenance windows
- [ ] Notify users of planned downtime
- [ ] Keep changelog updated

## Quick Commands Reference

### Development
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver 0.0.0.0:8000

# Create sample data
python create_sample_data.py
```

### Production
```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn smart_campus.wsgi:application --bind 0.0.0.0:8000 --workers 3

# Check for issues
python manage.py check --deploy

# Database backup
pg_dump smart_campus > backup_$(date +%Y%m%d).sql
```

### Heroku Specific
```bash
# Deploy to Heroku
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# View logs
heroku logs --tail

# Set environment variable
heroku config:set VARIABLE_NAME=value
```

## Troubleshooting

### Common Issues

**Database Connection Errors**
- Check database credentials in .env
- Verify PostgreSQL is running
- Check firewall rules
- Verify database exists

**Static Files Not Loading**
- Run collectstatic
- Check STATIC_ROOT and STATIC_URL
- Verify Nginx configuration
- Check file permissions

**CORS Errors**
- Verify CORS_ALLOWED_ORIGINS includes your iOS app domain
- Check CORS middleware is enabled
- Test with curl to isolate issue

**Authentication Fails**
- Verify rest_framework.authtoken is in INSTALLED_APPS
- Run migrations to create token table
- Check token is being sent in Authorization header

**500 Internal Server Error**
- Check error logs: `tail -f logs/django.log`
- Verify all environment variables are set
- Check database connection
- Review recent code changes

## Support Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Deployment Guide: IOS_DEPLOYMENT_GUIDE.md
- API Documentation: API_DOCUMENTATION.md

## Emergency Contacts

- System Administrator: [Add contact]
- Database Administrator: [Add contact]
- DevOps Team: [Add contact]
- On-call Developer: [Add contact]

---

**Last Updated:** February 1, 2026
**Version:** 1.0
