from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Movie, Rating


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        # define parameters for password
        extra_kwargs = {'password': {'write_only': True, 'required': True}} 

    #  create own definition to create user from built in crate_user function
    def crate(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'description', 'no_of_ratings', 'ave_ratings')


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'stars', 'user', 'movie')
