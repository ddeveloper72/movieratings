from django.db import models

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_lenght=32)
    description = models.TextField(max_length=360)
