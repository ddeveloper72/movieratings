from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Movie, Rating
from .serializers import MovieSerializer, RatingSerializer, UserSerializer
from .s3_utils import generate_presigned_upload_url


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
        Generate a presigned S3 URL for direct frontend upload of movie images.
        
        Security layers:
        - Requires authentication (TokenAuthentication)
        - Rate limiting (max 10 uploads per user per hour)
        - File size limit (max 5 MB enforced by presigned URL)
        - Content type validation (images only)
        - File extension validation
        - Content-based deduplication (optional via file hash)
        
        Expects JSON body:
        {
            "filename": "movie-poster.jpg",
            "contentType": "image/jpeg",  // optional, defaults to image/jpeg
            "fileHash": "abc123..."  // optional SHA256 hash for deduplication
        }
        
        Returns:
        {
            "upload_url": "https://...",  // presigned URL for PUT upload
            "public_url": "https://...",  // final public URL to save in Movie.imagePath
            "method": "PUT",
            "headers": {"Content-Type": "...", "x-amz-acl": "public-read"},
            "max_size_mb": 5,  // Maximum allowed file size
            "deduplicated": true  // If true, this file may already exist (same hash)
        }
        """
        from django.core.cache import cache
        import os
        
        filename = request.data.get('filename')
        content_type = request.data.get('contentType', 'image/jpeg')
        file_hash = request.data.get('fileHash')  # Optional for deduplication
        
        if not filename:
            return Response(
                {'error': 'filename is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in allowed_extensions:
            return Response(
                {'error': f'Invalid file extension. Allowed: {", ".join(allowed_extensions)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate content type matches extension
        ext_to_mime = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        expected_mime = ext_to_mime.get(file_ext)
        if content_type != expected_mime:
            return Response(
                {'error': f'Content type mismatch. {file_ext} files should use {expected_mime}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate content type is an image
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif']
        if content_type not in allowed_types:
            return Response(
                {'error': f'Invalid content type. Allowed: {", ".join(allowed_types)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Rate limiting: max 10 uploads per user per hour
        user_id = request.user.id
        cache_key = f'upload_rate_limit_{user_id}'
        upload_count = cache.get(cache_key, 0)
        
        if upload_count >= 10:
            return Response(
                {'error': 'Rate limit exceeded. Maximum 10 uploads per hour. Please try again later.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        # Increment rate limit counter
        cache.set(cache_key, upload_count + 1, 3600)  # 1 hour timeout
        
        try:
            # Generate presigned URL with 5MB size limit and optional hash
            presigned_data = generate_presigned_upload_url(
                filename, 
                content_type,
                max_size_mb=5,
                file_hash=file_hash
            )
            presigned_data['max_size_mb'] = 5
            presigned_data['uploads_remaining'] = 10 - upload_count - 1
            presigned_data['deduplicated'] = bool(file_hash)
            
            return Response(presigned_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Failed to generate upload URL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
