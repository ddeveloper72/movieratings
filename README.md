# Django Movie Ratings API

## [live application on Heroku](https://ddeveloper72-movie-rater-api.herokuapp.com/)

## Django 3.0.6. rest API application for providing secure access to the movie ratings SQL data base

## about me

The purpose of this application is to serve information to my front end Angular 10.  I ran into difficulty when I decided to host all of my static files remotely, on AWS.  having used SVG icons from a sprite library, I discovered that Django's built in security principles, wouldn't let me render them. Like most things, I discovered that there was a trick or a knack, to use JavaScript to reach out to my AWS S3 bucket instead and so render the svg icons inline via DOM model injection to my HTML mark-up.

Additional lessons learned, was how to log into and back out of the Django admin site, using my own frontend.  I'll certainly be maintaining  method for reaching the admin login portal for future projects!  The live link above, will let one see for themselves, what I mean.

### the technical stuff

If you're interested in the nuts and bolts for accessing the admin login, you can do so by updating your url patters like so:

```python

from django.contrib.auth.views import LoginView

urlpatterns = [
    
    # add a custom admin login page
    path('login/', LoginView.as_view(),
        {'template_name': 'core/login.html'}, name='login'),
    # include logout page as home for admin on logout
    path('admin/logout/', include('home.urls')),
    # ...rest of my patterns continue
] 

```

Here I'm referring to the built in Django LoginView as the view function then on user logout, redirecting the user to the home page.  using logoutView, redirects the user to the Django's built in needed during development when there was no custom front end, but now now.

### the API itself

I've used the concept, based on a tutorial by Senior Full Stack Engineer, Krystian Czekalski, then added to it for my own learning experience.

#### The Models

* 1st we setup a Movie mode:
Each movie will have a title, description and an image.
Each movie will also have a rating as well as an average rating (average rating from multiple users).

* 2nd we setup a Ratings model:
the movie is linked to the 1st model  by ForeignKey
the user from the authenticated User is linked by ForeignKey
The number of stars given by the user out of 5, is assigned to the movie.
The relationship between user and movie is unique.

![Readme Under Construction](https://github.com/ddeveloper72/django3-refresher/blob/master/static/img/django.png "Work in progress!")