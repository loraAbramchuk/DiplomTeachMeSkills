from rest_framework import viewsets, status
from rest_framework.response import Response
from Main.models import Genre, Country, Movie, Serial, Review
from .serializers import (
    GenreSerializers, CountrySerializer,
    MovieSerializer, SerialSerializer, ReviewSerializer     
)
from .permissions import IsAdminOrModeratorOrReadOnly


class GenreViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с жанрами.
    Только администраторы и модераторы могут создавать, редактировать и удалять жанры.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializers
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class CountryViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы со странами.
    Только администраторы и модераторы могут создавать, редактировать и удалять страны.
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]


class MovieViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с фильмами.
    Только администраторы и модераторы могут создавать, редактировать и удалять фильмы.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        return queryset


class SerialViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с сериалами.
    Только администраторы и модераторы могут создавать, редактировать и удалять сериалы.
    """
    queryset = Serial.objects.all()
    serializer_class = SerialSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        return queryset 
    
class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с отзывами.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAdminOrModeratorOrReadOnly] 