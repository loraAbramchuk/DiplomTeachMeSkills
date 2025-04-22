from django.contrib import admin
from . import models
# Register your models here.

# admin.site.register(models.Country)
# admin.site.register(models.Genre)
# admin.site.register(models.Movie)
# admin.site.register(models.Serial)

# admin.py
from django.contrib import admin
from .models import Genre, Country, Movie, Serial, Review
from django.utils.html import mark_safe

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
    list_display = ('id', 'title', 'release_year', 'created_at', 'poster_preview')  # Поля в списке
    list_filter = ('release_year', 'genres', 'country')  # Фильтры
    search_fields = ('title', 'description')  # Поля для поиска
    filter_horizontal = ('genres', 'country')  # Удобный выбор ManyToMany полей

    def poster_preview(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="height: 100px;" />')
        return "No Image"

    poster_preview.short_description = "Poster Preview"

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    display_genres.short_description = 'Genres'

    def display_countries(self, obj):
        return ", ".join([country.name for country in obj.country.all()])
    display_countries.short_description = 'Countries'

@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'release_year', 'episodes', 'created_at', 'poster_preview')
    list_filter = ('release_year', 'genres', 'country')
    search_fields = ('title', 'description')
    filter_horizontal = ('genres', 'country')

    def poster_preview(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="height: 100px;" />')
        return "No Image"
    poster_preview.short_description = "Poster Preview"

    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    display_genres.short_description = 'Genres'

    def display_countries(self, obj):
        return ", ".join([country.name for country in obj.country.all()])
    display_countries.short_description = 'Countries'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_content', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('text', 'user__username', 'movie__title', 'serial__title')

    def get_content(self, obj):
        if obj.movie:
            return f"Фильм: {obj.movie.title}"
        return f"Сериал: {obj.serial.title}"
    get_content.short_description = 'Контент'