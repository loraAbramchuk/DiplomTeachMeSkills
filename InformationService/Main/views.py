from django.shortcuts import render, get_object_or_404, redirect
from .models import Genre, Country, Movie, Serial, Review, Subscription, UserSubscription, Payment
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from functools import wraps

User = get_user_model()


def index(request):
    """Main page"""
    # Получаем последний добавленный фильм для баннера
    featured_movie = Movie.objects.order_by('-created_at').first()
    
    # Получаем последние 8 фильмов
    latest_movies = Movie.objects.order_by('-created_at')[1:9]
    
    # Получаем последние 8 сериалов
    latest_serials = Serial.objects.order_by('-created_at')[:8]
    
    context = {
        'featured_movie': featured_movie,
        'latest_movies': latest_movies,
        'latest_serials': latest_serials,
    }
    return render(request, 'Main/index.html', context)

def movies_list(request):
    """Список фильмов"""
    movies = Movie.objects.all()
    return render(request, 'Main/movies_list.html', {'movies': movies})

def serials_list(request):
    """Список сериалов"""
    serials = Serial.objects.all()
    return render(request, 'Main/serials_list.html', {'serials': serials})

def subscription_required(view_func):
    """Декоратор для проверки наличия активной подписки"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('users:login')
            
        active_subscription = UserSubscription.objects.filter(
            user=request.user,
            is_active=True,
            end_date__gt=timezone.now()
        ).exists()
        
        if not active_subscription:
            messages.warning(request, 'Для доступа к этому контенту необходима активная подписка.')
            return redirect('subscription_list')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

@subscription_required
def movie_detail(request, pk):
    """View for a specific movie"""
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'Main/movie_detail.html', {'movie': movie})

@subscription_required
def serial_detail(request, pk):
    """View for a specific serial"""
    serial = get_object_or_404(Serial, pk=pk)
    return render(request, 'Main/serial_detail.html', {'serial': serial})

@login_required
def add_movie_review(request, movie_id):
    """Add review for a movie"""
    if request.method == 'POST':
        # Проверяем, что пользователь не является модератором
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, 'Модераторы не могут оставлять отзывы!')
            return redirect('movie_detail', pk=movie_id)
            
        movie = get_object_or_404(Movie, pk=movie_id)
        Review.objects.create(
            user=request.user,
            movie=movie,
            text=request.POST['text'],
            rating=request.POST['rating']
        )
        messages.success(request, 'Отзыв успешно добавлен!')
        return redirect('movie_detail', pk=movie_id)

@login_required
def add_serial_review(request, serial_id):
    """Add review for a serial"""
    if request.method == 'POST':
        # Проверяем, что пользователь не является модератором
        if request.user.is_staff or request.user.is_superuser:
            messages.error(request, 'Модераторы не могут оставлять отзывы!')
            return redirect('serial_detail', pk=serial_id)
            
        serial = get_object_or_404(Serial, pk=serial_id)
        Review.objects.create(
            user=request.user,
            serial=serial,
            text=request.POST['text'],
            rating=request.POST['rating']
        )
        messages.success(request, 'Отзыв успешно добавлен!')
        return redirect('serial_detail', pk=serial_id)

def about(request):
    """About page"""
    return render(request, 'Main/about.html')

def user_profile(request, username):
    """Страница профиля пользователя с его рецензиями"""
    user_profile = get_object_or_404(User, username=username)
    
    # Получаем все рецензии пользователя
    movie_reviews = Review.objects.filter(user=user_profile, movie__isnull=False).select_related('movie').order_by('-created_at')
    serial_reviews = Review.objects.filter(user=user_profile, serial__isnull=False).select_related('serial').order_by('-created_at')
    
    context = {
        'user_profile': user_profile,
        'movie_reviews': movie_reviews,
        'serial_reviews': serial_reviews,
    }
    
    return render(request, 'Main/user_profile.html', context)

@login_required
def subscription_list(request):
    """Список доступных подписок"""
    subscriptions = Subscription.objects.all()
    user_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()
    
    return render(request, 'Main/subscription_list.html', {
        'subscriptions': subscriptions,
        'user_subscription': user_subscription
    })

@login_required
def subscribe(request, subscription_id):
    """Подписка на тариф"""
    subscription = get_object_or_404(Subscription, pk=subscription_id)
    
    # Проверяем, нет ли уже активной подписки
    active_subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()
    
    if active_subscription:
        messages.warning(request, 'У вас уже есть активная подписка!')
        return redirect('subscription_list')
    
    # Создаем запись о подписке
    user_subscription = UserSubscription.objects.create(
        user=request.user,
        subscription=subscription,
        start_date=timezone.now(),
        end_date=timezone.now() + timezone.timedelta(days=30),
        is_active=True
    )
    
    # Создаем запись об оплате
    Payment.objects.create(
        user=request.user,
        subscription=subscription,
        amount=subscription.price,
        status='completed'
    )
    
    messages.success(request, f'Вы успешно подписались на тариф {subscription.name}!')
    return redirect('subscription_list')

@login_required
def cancel_subscription(request):
    """Отмена подписки"""
    subscription = UserSubscription.objects.filter(
        user=request.user,
        is_active=True,
        end_date__gt=timezone.now()
    ).first()
    
    if subscription:
        subscription.is_active = False
        subscription.save()
        messages.success(request, 'Ваша подписка успешно отменена.')
    else:
        messages.warning(request, 'У вас нет активной подписки для отмены.')
    
    return redirect('subscription_list')

@login_required
def payment_history(request):
    """История платежей пользователя"""
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'Main/payment_history.html', {'payments': payments})