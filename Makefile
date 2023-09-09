migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
    daphne -b 0.0.0.0 -p 8000 ai_service.asgi:application

celery:
    celery -A ai_service worker -B --loglevel=info