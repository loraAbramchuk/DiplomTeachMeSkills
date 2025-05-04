from django.contrib import admin
from .models import Genre, Country, Movie, Serial, Review, Subscription, UserSubscription, Payment, MovieImage, SerialImage
from django.utils.html import mark_safe

class MovieImageInline(admin.TabularInline):
    model = MovieImage
    extra = 3

class SerialImageInline(admin.TabularInline):
    model = SerialImage
    extra = 3

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'kinopoisk_rating')
    list_filter = ('genres', 'country', 'release_year')
    search_fields = ('title', 'description')
    readonly_fields = ['created_at']
    inlines = [MovieImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'release_year', 'genres', 'country', 
                      'poster', 'trailer_url', 'watch_url', 'kinopoisk_rating', 'kinopoisk_url')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def poster_preview(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="height: 100px;" />')
        return "No Image"
    poster_preview.short_description = "Poster Preview"

@admin.register(Serial)
class SerialAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'episodes', 'kinopoisk_rating')
    list_filter = ('genres', 'country', 'release_year')
    search_fields = ('title', 'description')
    readonly_fields = ['created_at']
    inlines = [SerialImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'release_year', 'episodes', 'genres', 
                      'country', 'poster', 'trailer_url', 'watch_url', 'kinopoisk_rating', 'kinopoisk_url')
        }),
        ('Метаданные', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def poster_preview(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="height: 100px;" />')
        return "No Image"
    poster_preview.short_description = "Poster Preview"

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_content', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['text', 'user__username']
    readonly_fields = ['created_at']

    def get_content(self, obj):
        if obj.movie:
            return f"Фильм: {obj.movie.title}"
        return f"Сериал: {obj.serial.title}"
    get_content.short_description = 'Контент'

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(MovieImage)
class MovieImageAdmin(admin.ModelAdmin):
    list_display = ('movie', 'description')
    list_filter = ('movie',)

@admin.register(SerialImage)
class SerialImageAdmin(admin.ModelAdmin):
    list_display = ('serial', 'description')
    list_filter = ('serial',)