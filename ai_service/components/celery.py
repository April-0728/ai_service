from django.conf.global_settings import TIME_ZONE
import os

if os.getenv('ENABLE_CELERY') == 'True':
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    DJANGO_CELERY_BEAT_TZ_AWARE = False
    CELERY_ENABLE_UTC = False
    CELERY_WORKER_CONCURRENCY = 2  # 并发数
    CELERY_MAX_TASKS_PER_CHILD = 5  # worker最多执行5个任务便自我销毁释放内存
    CELERY_TIMEZONE = TIME_ZONE  # celery 时区问题
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
    CELERY_BEAT_SCHEDULER = os.getenv('CELERY_BEAT_SCHEDULER')  # Backend数据库
