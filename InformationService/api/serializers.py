from rest_framework import serializers
from Main.models import Genre, Country, Movie, Serial, Review
from users.models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей в API"""
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


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
    user = serializers.StringRelatedField()
    movie = serializers.StringRelatedField(required=False)
    serial = serializers.StringRelatedField(required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user', 'movie', 'serial', 'text', 'rating', 
            'status', 'status_display', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']



