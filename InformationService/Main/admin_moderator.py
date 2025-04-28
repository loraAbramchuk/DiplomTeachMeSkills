from django.contrib.admin import AdminSite
from django.contrib import admin
from django.utils.html import mark_safe
from .models import Movie, Serial, Review

class ModeratorAdminSite(AdminSite):
    site_header = 'Панель модератора'
    site_title = 'Панель модератора'
    index_title = 'Управление контентом'
    site_url = None

moderator_site = ModeratorAdminSite(name='moderator')

@admin.register(Movie, site=moderator_site)
class MovieModeratorAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'created_at', 'poster_preview']
    list_filter = ['release_year', 'genres', 'country']
    search_fields = ['title', 'description']
    filter_horizontal = ['genres', 'country']
    readonly_fields = ['created_at']
    
    def poster_preview(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="height: 100px;" />')
        return "No Image"
    poster_preview.short_description = "Poster Preview"

@admin.register(Serial, site=moderator_site)
class SerialModeratorAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'episodes', 'created_at']
    list_filter = ['release_year', 'genres', 'country']
    search_fields = ['title', 'description']
    filter_horizontal = ['genres', 'country']
    readonly_fields = ['created_at']
    
    def poster_preview(self, obj):
        if obj.poster:
            return mark_safe(f'<img src="{obj.poster.url}" style="height: 100px;" />')
        return "No Image"
    poster_preview.short_description = "Poster Preview"

@admin.register(Review, site=moderator_site)
class ReviewModeratorAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_content', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['text', 'user__username']
    readonly_fields = ['user', 'movie', 'serial', 'rating', 'created_at']
    
    def get_content(self, obj):
        if obj.movie:
            return f"Фильм: {obj.movie.title}"
        return f"Сериал: {obj.serial.title}"
    get_content.short_description = 'Контент'
    
    def has_add_permission(self, request):
        return False 