from django.shortcuts import render
from rest_framework import viewsets
from .models import Movie, Rating

# Create your views here.

class MovieViewSet(viewsets.ModelViewSet):
