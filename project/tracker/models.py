from datetime import datetime

from django.db import models


class TrackedHost(models.Model):
    active = models.BooleanField(default=False)
    host = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.host


class UserLog(models.Model):
    host = models.ForeignKey(TrackedHost, on_delete=models.CASCADE)
    tos = models.IntegerField(default=0)
    add_dt = models.DateTimeField(default=datetime.now, blank=True)

    def __str__(self):
        return f"{self.host} {str(self.tos)}"
