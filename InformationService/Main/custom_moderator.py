from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Movie, Serial, Review, User, Genre, Country
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

def is_moderator(user):
    return user.groups.filter(name='Модераторы').exists()

@login_required
@user_passes_test(is_moderator)
def moderator_dashboard(request):
    # Статистика
    total_movies = Movie.objects.count()
    total_serials = Serial.objects.count()
    total_reviews = Review.objects.count()
    pending_reviews = Review.objects.filter(status='pending').count()
    
    # Последние добавленные фильмы и сериалы
    recent_movies = Movie.objects.order_by('-created_at')[:5]
    recent_serials = Serial.objects.order_by('-created_at')[:5]
    
    # Последние отзывы
    recent_reviews = Review.objects.order_by('-created_at')[:5]
    
    context = {
        'total_movies': total_movies,
        'total_serials': total_serials,
        'total_reviews': total_reviews,
        'pending_reviews': pending_reviews,
        'recent_movies': recent_movies,
        'recent_serials': recent_serials,
        'recent_reviews': recent_reviews,
    }
    return render(request, 'moderator/dashboard.html', context)

@login_required
@user_passes_test(is_moderator)
def content_management(request):
    query = request.GET.get('q', '')
    content_type = request.GET.get('type', 'all')
    sort = request.GET.get('sort', 'created_at')
    order = request.GET.get('order', 'desc')

    sort_fields = {
        'title': 'title',
        'year': 'release_year',
        'created_at': 'created_at',
    }
    sort_field = sort_fields.get(sort, 'created_at')
    if order == 'desc':
        sort_field = '-' + sort_field

    movie_filter = {}
    serial_filter = {}
    if query:
        movie_filter['title__icontains'] = query
        serial_filter['title__icontains'] = query
    if request.GET.get('year'):
        movie_filter['release_year'] = request.GET['year']
        serial_filter['release_year'] = request.GET['year']
    if request.GET.get('genre'):
        movie_filter['genres__id'] = request.GET['genre']
        serial_filter['genres__id'] = request.GET['genre']
    if request.GET.get('country'):
        movie_filter['country__id'] = request.GET['country']
        serial_filter['country__id'] = request.GET['country']

    movies = Movie.objects.filter(**movie_filter).order_by(sort_field).distinct()
    serials = Serial.objects.filter(**serial_filter).order_by(sort_field).distinct()

    movie_paginator = Paginator(movies, 10)
    serial_paginator = Paginator(serials, 10)
    page = request.GET.get('page', 1)
    movies = movie_paginator.get_page(page)
    serials = serial_paginator.get_page(page)

    genres = Genre.objects.all()
    countries = Country.objects.all()

    context = {
        'movies': movies,
        'serials': serials,
        'query': query,
        'content_type': content_type,
        'sort': sort,
        'order': order,
        'genres': genres,
        'countries': countries,
        'selected_genre': request.GET.get('genre', ''),
        'selected_country': request.GET.get('country', ''),
        'selected_year': request.GET.get('year', ''),
    }
    return render(request, 'moderator/content_management.html', context)

@login_required
@user_passes_test(is_moderator)
def review_management(request):
    status = request.GET.get('status', 'all')
    query = request.GET.get('q', '')
    
    reviews = Review.objects.all()
    
    if status != 'all':
        reviews = reviews.filter(status=status)
    
    if query:
        reviews = reviews.filter(
            Q(text__icontains=query) |
            Q(user__username__icontains=query)
        )
    
    paginator = Paginator(reviews, 10)
    page = request.GET.get('page', 1)
    reviews = paginator.get_page(page)
    
    context = {
        'reviews': reviews,
        'status': status,
        'query': query,
    }
    return render(request, 'moderator/review_management.html', context)

@login_required
@user_passes_test(is_moderator)
@require_POST
def update_review_status(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    data = json.loads(request.body)
    new_status = data.get('status')
    
    if new_status in ['approved', 'rejected']:
        review.status = new_status
        review.save()
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid status'})

@login_required
@user_passes_test(is_moderator)
def edit_content(request, content_type, content_id):
    if content_type == 'movie':
        content = get_object_or_404(Movie, id=content_id)
        template = 'moderator/edit_movie.html'
    elif content_type == 'serial':
        content = get_object_or_404(Serial, id=content_id)
        template = 'moderator/edit_serial.html'
    else:
        return redirect('moderator_dashboard')
    
    if request.method == 'POST':
        # Обработка формы редактирования
        title = request.POST.get('title')
        description = request.POST.get('description')
        release_year = request.POST.get('release_year')
        
        content.title = title
        content.description = description
        content.release_year = release_year
        
        if 'poster' in request.FILES:
            content.poster = request.FILES['poster']
        
        content.save()
        messages.success(request, 'Контент успешно обновлен')
        return redirect('content_management')
    
    context = {
        'content': content,
        'content_type': content_type,
    }
    return render(request, template, context)

@login_required
@user_passes_test(is_moderator)
def create_content(request, content_type):
    if content_type not in ['movie', 'serial']:
        return redirect('moderator_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        release_year = request.POST.get('release_year')
        
        if content_type == 'movie':
            content = Movie.objects.create(
                title=title,
                description=description,
                release_year=release_year
            )
        else:
            content = Serial.objects.create(
                title=title,
                description=description,
                release_year=release_year
            )
        
        if 'poster' in request.FILES:
            content.poster = request.FILES['poster']
            content.save()
        
        messages.success(request, 'Контент успешно создан')
        return redirect('content_management')
    
    template = f'moderator/create_{content_type}.html'
    return render(request, template, {'content_type': content_type})

@login_required
@user_passes_test(is_moderator)
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.text = request.POST.get('text', review.text)
        review.status = request.POST.get('status', review.status)
        review.save()
        messages.success(request, 'Отзыв успешно обновлен')
        return redirect('review_management')
    return render(request, 'moderator/edit_review.html', {'review': review}) 