from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_lenght=32)
    description = models.TextField(max_length=360)


class Rading(models.Model):
    movie = models.ForeignKey(Movie)
    # include user from Django auth that made rating
    user = models.ForeignKey(User)