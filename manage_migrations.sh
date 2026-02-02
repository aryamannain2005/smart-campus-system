#!/bin/bash
# Script to run migrations for Smart Campus System

echo "Smart Campus System - Database Migration Script"
echo "================================================"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Django is installed
if ! python -c "import django" 2>/dev/null; then
    echo "Error: Django is not installed. Please run: pip install -r requirements.txt"
    exit 1
fi

echo "Step 1: Making migrations for attendance app..."
python manage.py makemigrations attendance

echo ""
echo "Step 2: Making migrations for notifications app..."
python manage.py makemigrations notifications

echo ""
echo "Step 3: Making migrations for all apps..."
python manage.py makemigrations

echo ""
echo "Step 4: Applying migrations..."
python manage.py migrate

echo ""
echo "Step 5: Creating cache table (optional)..."
python manage.py createcachetable 2>/dev/null || echo "Cache table creation skipped"

echo ""
echo "✓ Migration complete!"
echo ""
echo "Next steps:"
echo "1. Create superuser: python manage.py createsuperuser"
echo "2. Create sample data: python create_sample_data.py"
echo "3. Run server: python manage.py runserver"
echo ""
