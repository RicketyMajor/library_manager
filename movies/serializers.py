from rest_framework import serializers
from .models import Movie, MovieDirectory, MovieInbox, MovieWatcher, MovieWishlist


class MovieDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieDirectory
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class MovieWatcherSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieWatcher
        fields = '__all__'


class MovieWishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieWishlist
        fields = '__all__'


class MovieInboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieInbox
        fields = '__all__'
