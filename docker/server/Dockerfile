FROM python:3.10
WORKDIR /apps

ADD ./requirements ./requirements
# 使用腾讯云镜像源
RUN pip install -r ./requirements/requirements.txt -i https://mirrors.tencent.com/pypi/simple

ENV SECRET_KEY django-insecure-wi*fg%43$^^bwbus!1+p2sud3wnpe@3$is$3h8$cdw6h+s!-ug
ENV DEBUG False
ENV DB_ENGINE  django.db.backends.sqlite3
ENV DB_NAME ai-service

ADD ./ai_service ./ai_service
ADD ./apps ./apps
ADD ./manage.py ./manage.py

RUN #python manage.py collectstatic --noinput