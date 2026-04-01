from rest_framework import viewsets
from .models import Movie, MovieDirectory, MovieWatcher, MovieWishlist
from .serializers import MovieSerializer, MovieDirectorySerializer, MovieWatcherSerializer, MovieWishlistSerializer


class MovieDirectoryViewSet(viewsets.ModelViewSet):
    queryset = MovieDirectory.objects.all()
    serializer_class = MovieDirectorySerializer


class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all().order_by('-created_at')
    serializer_class = MovieSerializer


class MovieWatcherViewSet(viewsets.ModelViewSet):
    queryset = MovieWatcher.objects.all().order_by('-created_at')
    serializer_class = MovieWatcherSerializer


class MovieWishlistViewSet(viewsets.ModelViewSet):
    queryset = MovieWishlist.objects.filter(
        is_rejected=False).order_by('-date_found')
    serializer_class = MovieWishlistSerializer
