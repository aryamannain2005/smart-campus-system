web: gunicorn smart_campus.wsgi:application --bind 0.0.0.0:$PORT --log-file -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
