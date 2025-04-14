from django.contrib import admin
from . import models
# Register your models here.

# admin.site.register(models.Country)
# admin.site.register(models.Genre)
# admin.site.register(models.Movie)
# admin.site.register(models.Serial)

# admin.py
from django.contrib import admin
from .models import Genre, Country, Movie, Serial

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Отображаемые поля в списке
    search_fields = ('name',)  # Поля для поиска

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_year', 'created_at')  # Поля в списке
    list_filter = ('release_year', 'genres', 'country')  # Фильтры
    search_fields = ('title', 'description')  # Поля для поиска
    filter_horizontal = ('genres', 'country')  # Удобный выбор ManyToMany полей

@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_year', 'episodes', 'created_at')
    list_filter = ('release_year', 'genres', 'country')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres', 'country')