from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('movies/', views.movies_list, name='movies_list'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:movie_id>/review/', views.add_movie_review, name='add_movie_review'),
    path('serials/', views.serials_list, name='serials_list'),
    path('serials/<int:pk>/', views.serial_detail, name='serial_detail'),
    path('serials/<int:serial_id>/review/', views.add_serial_review, name='add_serial_review'),
    path('about/', views.about, name='about'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    
    # Маршруты для подписок
    path('subscriptions/', views.subscription_list, name='subscription_list'),
    path('subscriptions/<int:subscription_id>/subscribe/', views.subscribe, name='subscribe'),
    path('subscriptions/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('payments/history/', views.payment_history, name='payment_history'),
    
    # Рекомендательная система
    path('trending/', views.trending, name='trending'),
    path('api/recommendations/', views.get_recommendations, name='recommendations'),
    path('api/similar/<str:content_type>/<int:pk>/', views.get_similar, name='similar_content'),
    # path('api/trending/', views.get_trending, name='trending'),
]