from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Tank(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    tank_id = models.IntegerField()

    def __str__(self):
        return self.name

class Reading(models.Model):
    reading_type = models.CharField(max_length=255)
    tank = models.ForeignKey('Tank', on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    value = models.FloatField()
