from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from . import custom_moderator

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.search, name='search'),
    path('movies/', views.movies_list, name='movies_list'),
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),
    path('movies/<int:movie_id>/review/', views.add_movie_review, name='add_movie_review'),
    path('serials/', views.serials_list, name='serials_list'),
    path('serials/<int:pk>/', views.serial_detail, name='serial_detail'),
    path('serials/<int:serial_id>/review/', views.add_serial_review, name='add_serial_review'),
    path('about/', views.about, name='about'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    
    # Аутентификация
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
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
    
    # URL-маршруты для админки модератора
    path('moderator-panel/', custom_moderator.moderator_dashboard, name='moderator_dashboard'),
    path('moderator-panel/content/', custom_moderator.content_management, name='content_management'),
    path('moderator-panel/content/create/<str:content_type>/', custom_moderator.create_content, name='create_content'),
    path('moderator-panel/content/<str:content_type>/<int:content_id>/', custom_moderator.edit_content, name='edit_content'),
    path('moderator-panel/reviews/', custom_moderator.review_management, name='review_management'),
    path('moderator-panel/reviews/<int:review_id>/update_status/', custom_moderator.update_review_status, name='update_review_status'),
    path('moderator-panel/reviews/<int:review_id>/edit/', custom_moderator.edit_review, name='edit_review'),
]