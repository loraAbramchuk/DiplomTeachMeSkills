from rest_framework import serializers
from Main.models import Genre, Country, Movie, Serial, Review           


class GenreSerializers(serializers.ModelSerializer):
    """Сериализатор для жанров в API"""
    class Meta:
        model = Genre
        fields = ['id', 'name']


class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор для стран в API"""
    class Meta:
        model = Country
        fields = ['id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    """Сериализатор для фильмов в API с вложенными жанрами и странами"""
    genres = GenreSerializers(many=True, read_only=True)
    country = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_year', 'genres', 'country', 'poster', 'created_at']


class SerialSerializer(serializers.ModelSerializer):
    """Сериализатор для сериалов в API с вложенными жанрами и странами"""
    genres = GenreSerializers(many=True, read_only=True)
    country = CountrySerializer(many=True, read_only=True)

    class Meta:
        model = Serial
        fields = ['id', 'title', 'description', 'release_year', 'genres', 'country', 'episodes', 'poster', 'created_at'] 


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов в API"""
    class Meta:
        model = Review
        fields = ['id', 'movie', 'user', 'rating', 'comment', 'created_at']



