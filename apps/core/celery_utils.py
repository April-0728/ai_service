import json

from django_celery_beat.models import CrontabSchedule, PeriodicTask


class CeleryUtils:
    @staticmethod
    def cycle_task_create_or_update(name, crontab, args, task):
        """创建或更新周期任务"""
        minute, hour, day, month, week = crontab.split()
        kwargs = dict(minute=minute, hour=hour, day_of_week=week, day_of_month=day, month_of_year=month)
        crontab, _ = CrontabSchedule.objects.get_or_create(**kwargs, defaults=kwargs)
        defaults = dict(
            crontab=crontab,
            name=name,
            task=task,
            enabled=True,
            args=json.dumps(args),
        )
        PeriodicTask.objects.update_or_create(name=name, defaults=defaults)

    @staticmethod
    def delete_cycle_task(name):
        """删除周期任务"""
        PeriodicTask.objects.filter(name=name).delete()
