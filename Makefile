migrate:
	python manage.py makemigrations
	python manage.py migrate
	DJANGO_SUPERUSER_USERNAME=admin DJANGO_SUPERUSER_EMAIL=admin@example.com DJANGO_SUPERUSER_PASSWORD=password python manage.py createsuperuser --noinput
run:
    daphne -b 0.0.0.0 -p 8000 ai_service.asgi:application

celery:
    celery -A ai_service worker -B --loglevel=info