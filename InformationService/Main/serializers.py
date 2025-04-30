from rest_framework import serializers
from .models import Genre, Country, Movie, Serial


class GenreSerializers(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    class Meta:
        model = Genre
        fields = ['id', 'name']

class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор для стран"""
    class Meta:
        model = Country
        fields = ['id', 'name']

class MovieSerializer(serializers.ModelSerializer):
    """Сериализатор для фильмов с вложенными жанрами и странами"""
    genres = GenreSerializers(many=True, read_only=True)
    country = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_year', 'genres', 'country', 'poster', 'created_at']

class SerialSerializer(serializers.ModelSerializer):
    """Сериализатор для сериалов с вложенными жанрами и странами"""
    genres = GenreSerializers(many=True, read_only=True)
    country = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Serial
        fields = ['id', 'title', 'description', 'release_year', 'genres', 'country', 'episodes', 'poster', 'created_at']