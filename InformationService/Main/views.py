from django.shortcuts import render
from rest_framework import viewsets
from .models import Genre, Country, Movie, Serial
from .serializers import (
    GenreSerializers, CountrySerializer, MovieSerializer, SerialSerializer
)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


def index(request):
    """Главная страница"""
    return render(request, 'index.html')


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializers

class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

class MovieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SerialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Serial.objects.all()
    serializer_class = SerialSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def movies_list(request):
    """Список фильмов"""
    movies = Movie.objects.all()
    return render(request, 'movies_list.html', {'movies': movies})

def serials_list(request):
    """Список сериалов"""
    serials = Serial.objects.all()
    return render(request, 'serials_list.html', {'serials': serials})

def movie_detail(request, pk):
    """View for a specific movie"""
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movie_detail.html', {'movie': movie})

def serial_detail(request, pk):
    """View for a specific serial"""
    serial = get_object_or_404(Serial, pk=pk)
    return render(request, 'serial_detail.html', {'serial': serial})

def about(request):
    """About page"""
    return render(request, 'about.html')