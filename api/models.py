from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=360)


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    # include user from Django auth that made rating
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # specify no of stars between 1 & 5
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    #  insure the user can not rate for the same movie more than once
    class Meta:
        unique_together = (('user', 'movie'),)  # tuple
        index_together = (('user', 'movie'),)
