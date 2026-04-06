import re
import requests
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rich.markup import render
from .models import Movie, MovieDirectory, MovieWatcher, MovieWishlist, MovieInbox
from .serializers import MovieSerializer, MovieDirectorySerializer, MovieWatcherSerializer, MovieWishlistSerializer, MovieInboxSerializer
from .tmdb_oracle import search_movie_tmdb
from django.shortcuts import render


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


class MovieInboxViewSet(viewsets.ModelViewSet):
    queryset = MovieInbox.objects.all().order_by('-date_scanned')
    serializer_class = MovieInboxSerializer


@api_view(['POST'])
def receive_barcode(request):
    """Recibe EAN/UPC, busca el título comercial y lo guarda en el Inbox."""
    barcode = request.data.get('barcode')
    if not barcode:
        return Response({"error": "Falta el código de barras."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Búsqueda Comercial (UPCitemdb es gratuito y no requiere API KEY para pruebas básicas)
    upc_url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
    try:
        upc_resp = requests.get(upc_url, timeout=5.0)
        data = upc_resp.json()

        if upc_resp.status_code != 200 or not data.get('items'):
            # Si no lo encuentra, lo guardamos crudo igual para que lo corrijas a mano en el TUI
            MovieInbox.objects.get_or_create(barcode=barcode, defaults={
                                             'title': f"Desconocido ({barcode})"})
            return Response({"error": "El código fue guardado, pero no se reconoció en el comercio."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Extracción y Limpieza del título
        raw_title = data['items'][0]['title']
        # Limpia "Blu-ray", "DVD", "Edición Coleccionista" y corta si hay guiones
        clean = re.sub(
            r'(?i)(blu-ray|bluray|dvd|4k|uhd|steelbook|edición|edition)', '', raw_title)
        clean_title = re.split(r'[-(\[]', clean)[0].strip()

    except Exception as e:
        return Response({"error": f"Error conectando al comercio: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 3. Guardar en el Inbox
    # OJO: Asegúrate de que tu modelo MovieInbox tenga un campo 'title = models.CharField(max_length=255, null=True, blank=True)'
    MovieInbox.objects.get_or_create(
        barcode=barcode, defaults={'title': clean_title})

    return Response({"message": f"'{clean_title}' depositado en el Inbox."}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def process_barcode(request):
    """El TUI invoca esta ruta para traducir el EAN y guardarlo usando TMDB."""
    barcode = request.data.get('barcode')
    if not barcode:
        return Response({"error": "Falta el código de barras."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Traducción en API Comercial (UPCitemdb)
    upc_url = f"https://api.upcitemdb.com/prod/trial/lookup?upc={barcode}"
    try:
        upc_resp = requests.get(upc_url, timeout=5.0)
        data = upc_resp.json()
        if upc_resp.status_code != 200 or not data.get('items'):
            return Response({"error": f"El código {barcode} no es reconocido comercialmente."}, status=status.HTTP_404_NOT_FOUND)

        raw_title = data['items'][0]['title']
        clean_title = clean_movie_title(raw_title)
    except Exception as e:
        return Response({"error": f"Error de red comercial: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 2. Validación de Duplicados
    if Movie.objects.filter(title__icontains=clean_title).exists():
        return Response({"error": f"'{clean_title}' ya está en tus bóvedas."}, status=status.HTTP_400_BAD_REQUEST)

    # 3. Invocación al Oráculo
    movie_data = search_movie_tmdb(clean_title)
    if not movie_data:
        return Response({"error": f"'{clean_title}' no existe en TMDB."}, status=status.HTTP_404_NOT_FOUND)

    # 4. Guardado Final
    Movie.objects.create(
        title=movie_data['title'],
        original_title=movie_data.get('original_title', ''),
        director=movie_data.get('director', 'Desconocido'),
        cast=movie_data.get('cast', ''),
        release_year=movie_data.get('release_year'),
        duration_minutes=movie_data.get('duration_minutes', 0),
        genres=movie_data.get('genres', []),
        synopsis=movie_data.get('synopsis', ''),
        poster_url=movie_data.get('poster_url', '')
    )
    return Response({"message": f"'{movie_data['title']}' archivada con éxito."}, status=status.HTTP_201_CREATED)


def movie_scanner_view(request):
    """Renderiza el escáner QR aislado exclusivamente para películas."""
    return render(request, 'movies/movie_scanner.html')
