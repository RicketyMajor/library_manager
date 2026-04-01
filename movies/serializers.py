from rest_framework import serializers
from .models import Movie, MovieDirectory


class MovieDirectorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieDirectory
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'
