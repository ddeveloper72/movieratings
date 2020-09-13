from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.


class Movie(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=360)
    image = models.ImageField(upload_to="img/", blank=True, null=True)

    # count the number of ratings for the movie
    def no_of_ratings(self):
        ratings = Rating.objects.filter(movie=self)
        return len(ratings)


    # sum ratings and divide by number of ratings
    def ave_ratings(self):
        sum = 0
        ratings = Rating.objects.filter(movie=self)
        for rating in ratings:
            sum += rating.stars
        
        if len(ratings) > 0:
            return sum / len(ratings)
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
        unique_together = (('user', 'movie'),)  # tuple
        index_together = (('user', 'movie'),)
