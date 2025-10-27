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

    @action(detail=False, methods=['POST'])
    def get_upload_url(self, request):
        """
        File upload endpoint - currently disabled as S3 support has been removed.
        
        To enable file uploads, you can either:
        1. Re-enable S3 support by adding boto3 to requirements.txt and configuring AWS credentials
        2. Implement local file upload handling  
        3. Use a different cloud storage provider
        
        For now, movie images should be referenced by URL in the imagePath field.
        
        Returns HTTP 501 Not Implemented with guidance message.
        """

        
        # File upload is currently disabled since S3 support was removed
        return Response(
            {
                'error': 'File upload is currently disabled. S3 support has been removed to simplify deployment.',
                'message': 'Please use direct image URLs in the imagePath field instead.',
                'example': 'https://example.com/path/to/movie-poster.jpg',
                'note': 'To re-enable uploads, add boto3 to requirements.txt and configure AWS credentials.'
            },
            status=status.HTTP_501_NOT_IMPLEMENTED
        )


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
