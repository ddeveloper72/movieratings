from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(max_length=360)
    imagePath = models.URLField(max_length=200, blank=True, null=True)

    # count the number of ratings for the movie
    def no_of_ratings(self):
        ratings = Rating.objects.filter(movie=self)
        return len(ratings)


    # sum ratings and divide by number of ratings
    def ave_ratings(self):
        total = 0
        ratings = Rating.objects.filter(movie=self)
        for rating in ratings:
            total += rating.stars
        
        if len(ratings) > 0:
            return total / len(ratings)
        else:
            return 0


class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    # include user from Django auth that made rating
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # specify no of stars between 1 & 5
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    #  insure the user can not rate for the same movie more than once
    class Meta:
        # Replace deprecated unique_together/index_together with modern constraints and indexes
        constraints = [
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie')
        ]
        indexes = [
            models.Index(fields=['user', 'movie'], name='idx_user_movie')
        ]
