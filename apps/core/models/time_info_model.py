from django.db import models


class TimeInfoModel(models.Model):
    created_at = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("修改时间", auto_now=True)

    class Meta:
        abstract = True
        get_latest_by = 'updated_at'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['-created_at']),
        ]
