from rest_framework import serializers
from .models import Book, Author, Genre, Watcher, WishlistItem


class BookSerializer(serializers.ModelSerializer):
    # Extraemos el nombre del autor para que el JSON sea más fácil de leer
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'format_type',
                  'is_read', 'publisher', 'page_count']


class WatcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watcher
        fields = '__all__'


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = '__all__'
