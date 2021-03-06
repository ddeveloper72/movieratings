from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Movie, Rating
from .serializers import MovieSerializer, RatingSerializer, UserSerializer


# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny, )
    # query everything from the movie model db
    queryset = User.objects.all()
    serializer_class = UserSerializer


class MovieViewSet(viewsets.ModelViewSet):
    # query everything from the movie model db
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    authentication_classes = (TokenAuthentication, )

    # add permission class to MovieViewSet view function
    permission_classes = (IsAuthenticated, )

    # for a specific movie, True using method POST
    @action(detail=True, methods=['POST'])
    def rate_movie(self, request, pk=None):
        if 'stars' in request.data:
            
            # select movie from db using primary key
            movie = Movie.objects.get(id=pk)
            stars = request.data['stars']
            user = request.user
            # work around to specify fixed user id for building views
            # user = User.objects.get(id=1)
            # print('user', user.username + ' ✔')

            try:
                rating = Rating.objects.get(user=user.id,
                                            movie=movie.id)  # stored in db
                rating.stars = stars
                rating.save()
                serializer = RatingSerializer(rating, many=False)
                response = {'message': 'Rating Updated!', 
                            'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)
            except Rating.DoesNotExist:
                # pass whole objects
                rating = Rating.objects.create(user=user,
                                               movie=movie,
                                               stars=stars)
                response = {'message': 'Rating created!',
                            'result': serializer.data}
                return Response(response, status=status.HTTP_200_OK)

        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class RatingViewSet(viewsets.ModelViewSet):
    # query everything from the movie model db
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    authentication_classes = (TokenAuthentication, )
    # add permission class to RatingViewSet view function
    permission_classes = (IsAuthenticated, )

    def update(self, request, *args, **kwargs):
        response = {'message': 'You can\'t update ratings like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        response = {'message': 'You can\'t create ratings like that'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)
