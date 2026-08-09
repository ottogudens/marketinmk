web: cd backend && gunicorn config.wsgi --workers 4 --bind 0.0.0.0:$PORT
migrate: cd backend && python manage.py migrate
collectstatic: cd backend && python manage.py collectstatic --noinput
