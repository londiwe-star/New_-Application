"""
URL configuration for the news application.

This module defines all URL patterns for the news portal.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'news'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Articles
    path('articles/', views.ArticleListView.as_view(), name='article_list'),
    path('articles/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/approve/', views.article_approve, name='article_approve'),
    path('articles/pending/', views.pending_articles, name='pending_articles'),
    path('articles/my/', views.my_articles, name='my_articles'),
    
    # Subscriptions
    path('publishers/', views.publisher_list, name='publisher_list'),
    path('journalists/', views.journalist_list, name='journalist_list'),
    path('subscribe/publisher/<int:publisher_id>/', views.subscribe_publisher, name='subscribe_publisher'),
    path('subscribe/journalist/<int:journalist_id>/', views.subscribe_journalist, name='subscribe_journalist'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]


