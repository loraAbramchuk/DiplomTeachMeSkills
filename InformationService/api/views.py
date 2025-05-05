from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from Main.models import Genre, Country, Movie, Serial, Review
from users.models import CustomUser
from .serializers import (
    GenreSerializers, CountrySerializer,
    MovieSerializer, SerialSerializer, ReviewSerializer,
    UserSerializer
)
from .permissions import IsModeratorOrReadOnly, IsSuperuserOnly


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с пользователями.
    Доступно только для суперпользователей.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsSuperuserOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'status': 'success'})


class GenreViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с жанрами.
    Только модераторы и суперпользователи могут создавать, редактировать и удалять жанры.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializers
    permission_classes = [IsModeratorOrReadOnly]


class CountryViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы со странами.
    Только модераторы и суперпользователи могут создавать, редактировать и удалять страны.
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsModeratorOrReadOnly]


class MovieViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с фильмами.
    Только модераторы и суперпользователи могут создавать, редактировать и удалять фильмы.
    """
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsModeratorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        return queryset


class SerialViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с сериалами.
    Только модераторы и суперпользователи могут создавать, редактировать и удалять сериалы.
    """
    queryset = Serial.objects.all()
    serializer_class = SerialSerializer
    permission_classes = [IsModeratorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_id = self.request.query_params.get('genre_id')
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        return queryset 
    
class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint для работы с отзывами.
    Поддерживает фильтрацию по статусу и поиск по тексту.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsModeratorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['text', 'user__username']

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        review = self.get_object()
        review.status = 'approved'
        review.save()
        return Response({'status': 'success'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        review = self.get_object()
        review.status = 'rejected'
        review.save()
        return Response({'status': 'success'}) 