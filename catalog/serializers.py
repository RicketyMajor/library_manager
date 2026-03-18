from rest_framework import serializers
from .models import Book, Author, Genre, Watcher, WishlistItem, Friend, Loan


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)

    class Meta:
        model = Book
        # ¡Magia! Esto expone todos los metadatos, descripciones y URLs.
        fields = '__all__'


class WatcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Watcher
        fields = '__all__'


class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = '__all__'


class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friend
        fields = '__all__'


class LoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    friend_name = serializers.CharField(source='friend.name', read_only=True)

    class Meta:
        model = Loan
        fields = '__all__'
