from rest_framework import viewsets
from .models import Movie, MovieDirectory, MovieWatcher, MovieWishlist
from .serializers import MovieSerializer, MovieDirectorySerializer, MovieWatcherSerializer, MovieWishlistSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .tmdb_oracle import search_movie_tmdb


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


@api_view(['POST'])
def scan_movie(request):
    """Busca una película en TMDB y la inyecta al Videoclub."""
    title = request.data.get('title')
    if not title:
        return Response({"error": "Se requiere el título de la cinta."}, status=status.HTTP_400_BAD_REQUEST)

    # Evita duplicados
    if Movie.objects.filter(title__icontains=title).exists():
        return Response({"message": "La cinta ya está en las bóvedas del Videoclub."}, status=status.HTTP_200_OK)

    # Invoca al Oráculo
    movie_data = search_movie_tmdb(title)

    if not movie_data:
        return Response({"error": "La cinta no fue encontrada en los registros de TMDB."}, status=status.HTTP_404_NOT_FOUND)

    # Guarda la película
    movie = Movie.objects.create(
        title=movie_data['title'],
        original_title=movie_data['original_title'],
        director=movie_data['director'],
        cast=movie_data['cast'],
        release_year=movie_data['release_year'],
        duration_minutes=movie_data['duration_minutes'],
        genres=movie_data['genres'],
        synopsis=movie_data['synopsis'],
        poster_url=movie_data['poster_url']
    )

    return Response({
        "message": f"¡Cinta '{movie.title}' procesada y archivada!",
        "id": movie.id
    }, status=status.HTTP_201_CREATED)
