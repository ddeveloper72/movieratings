from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Movie, Rating
from .serializers import MovieSerializer, RatingSerializer

# Create your views here.


class MovieViewSet(viewsets.ModelViewSet):
    # query everything from the movie model db
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

    # for a specific movie, True using method POST
    @action(detail=True, methods=['POST'])
    def rate_movie(self, request, pk=None):
        if 'stars' in request.data:

            print(pk + ' ✔')  # prink pk to terminal ✔

            response = {'message': 'its working!'}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {'message': 'You need to provide stars'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)



class RatingViewSet(viewsets.ModelViewSet):
    # query everything from the movie model db
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
